# -*- coding: utf-8 -*-
"""
多因子选股器 - 交互式可视化工具

功能:
  1. 可视化界面调整因子权重
  2. 实时预览选股结果
  3. 支持多种预设策略模板
  4. 导出选股结果
  5. 因子结果存储与增量更新

运行: streamlit run multi_factor_selector.py
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib
from datetime import datetime, timedelta

# 导入数据库配置
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from db_config import execute_query, INITIAL_CASH

# 导入因子存储模块
from factor_storage import (
    create_factor_table, save_factors, batch_save_factors,
    load_factors, get_latest_factor_date, get_factor_dates,
    delete_factors_by_date
)


# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="多因子选股器",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #667eea;
    }
    .factor-slider {
        padding: 10px 0;
    }
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 因子定义
# ============================================================

FACTOR_DEFINITIONS = {
    'momentum_20d': {
        'name': '20日动量',
        'desc': 'ROC(20), 反映短期价格趋势',
        'direction': 1,
        'default_weight': 0.20,
        'color': '#e74c3c',
        'icon': '📈'
    },
    'momentum_60d': {
        'name': '60日动量',
        'desc': 'ROC(60), 反映中期价格趋势',
        'direction': 1,
        'default_weight': 0.15,
        'color': '#e67e22',
        'icon': '📊'
    },
    'volatility': {
        'name': '波动率',
        'desc': 'ATR(14)/Close, 归一化波动率 (反向)',
        'direction': -1,
        'default_weight': 0.15,
        'color': '#3498db',
        'icon': '📉'
    },
    'rsi_14': {
        'name': 'RSI(14)',
        'desc': 'RSI(14), 超卖区间更优 (反向)',
        'direction': -1,
        'default_weight': 0.10,
        'color': '#9b59b6',
        'icon': '🔄'
    },
    'adx_14': {
        'name': 'ADX(14)',
        'desc': 'ADX(14), 趋势强度指标',
        'direction': 1,
        'default_weight': 0.10,
        'color': '#1abc9c',
        'icon': '🎯'
    },
    'turnover_ratio': {
        'name': '换手率',
        'desc': '当日量/20日均量, 量能放大信号',
        'direction': 1,
        'default_weight': 0.10,
        'color': '#f39c12',
        'icon': '💹'
    },
    'price_position': {
        'name': '价格位置',
        'desc': '当前价在60日区间位置 (反向)',
        'direction': -1,
        'default_weight': 0.10,
        'color': '#27ae60',
        'icon': '📍'
    },
    'macd_signal': {
        'name': 'MACD信号',
        'desc': 'MACD柱状图',
        'direction': 1,
        'default_weight': 0.10,
        'color': '#8e44ad',
        'icon': '📶'
    }
}

# 预设策略模板
STRATEGY_TEMPLATES = {
    '均衡策略': {
        'desc': '各因子均衡配置, 适合稳健投资',
        'weights': {
            'momentum_20d': 0.15, 'momentum_60d': 0.15, 'volatility': 0.15,
            'rsi_14': 0.10, 'adx_14': 0.10, 'turnover_ratio': 0.10,
            'price_position': 0.15, 'macd_signal': 0.10
        }
    },
    '动量优先': {
        'desc': '侧重价格趋势, 追涨杀跌策略',
        'weights': {
            'momentum_20d': 0.30, 'momentum_60d': 0.25, 'volatility': 0.05,
            'rsi_14': 0.05, 'adx_14': 0.15, 'turnover_ratio': 0.10,
            'price_position': 0.05, 'macd_signal': 0.05
        }
    },
    '价值挖掘': {
        'desc': '寻找超卖反弹机会, 逆向投资',
        'weights': {
            'momentum_20d': 0.05, 'momentum_60d': 0.05, 'volatility': 0.10,
            'rsi_14': 0.30, 'adx_14': 0.05, 'turnover_ratio': 0.10,
            'price_position': 0.30, 'macd_signal': 0.05
        }
    },
    '趋势跟踪': {
        'desc': '强趋势股票, ADX权重高',
        'weights': {
            'momentum_20d': 0.20, 'momentum_60d': 0.15, 'volatility': 0.05,
            'rsi_14': 0.05, 'adx_14': 0.30, 'turnover_ratio': 0.15,
            'price_position': 0.05, 'macd_signal': 0.05
        }
    },
    '低波动': {
        'desc': '选择低波动股票, 风险控制优先',
        'weights': {
            'momentum_20d': 0.10, 'momentum_60d': 0.10, 'volatility': 0.35,
            'rsi_14': 0.15, 'adx_14': 0.05, 'turnover_ratio': 0.05,
            'price_position': 0.10, 'macd_signal': 0.10
        }
    }
}


# ============================================================
# 数据加载函数
# ============================================================

@st.cache_data(ttl=3600)
def load_stock_data(start_date, end_date, min_bars=60):
    """批量加载日K线数据"""
    sql = """
        SELECT stock_code, trade_date, open_price, high_price, low_price,
               close_price, volume
        FROM trade_stock_daily
        WHERE trade_date >= %s AND trade_date <= %s
        ORDER BY stock_code, trade_date ASC
    """
    rows = execute_query(sql, [start_date, end_date])
    if not rows:
        return {}

    df_all = pd.DataFrame(rows)
    df_all['trade_date'] = pd.to_datetime(df_all['trade_date'])
    for col in ['open_price', 'high_price', 'low_price', 'close_price', 'volume']:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

    result = {}
    progress_bar = st.progress(0)
    status_text = st.empty()

    codes = df_all['stock_code'].unique()
    for i, code in enumerate(codes):
        group = df_all[df_all['stock_code'] == code]
        sub = group.set_index('trade_date').sort_index()
        sub = sub[['open_price', 'high_price', 'low_price', 'close_price', 'volume']]
        sub.columns = ['open', 'high', 'low', 'close', 'volume']
        if len(sub) >= min_bars:
            result[code] = sub

        progress_bar.progress((i + 1) / len(codes))
        status_text.text(f'加载数据: {code} ({i+1}/{len(codes)})')

    progress_bar.empty()
    status_text.empty()

    return result


def calc_all_factors(df):
    """计算单只股票的全部因子"""
    if len(df) < 60:
        return None

    h = df['high'].values.astype(np.float64)
    l = df['low'].values.astype(np.float64)
    c = df['close'].values.astype(np.float64)
    v = df['volume'].values.astype(np.float64)

    if c[-1] <= 0 or np.isnan(c[-1]):
        return None

    try:
        roc_20 = talib.ROC(c, timeperiod=20)
        roc_60 = talib.ROC(c, timeperiod=60)
        atr = talib.ATR(h, l, c, timeperiod=14)
        rsi = talib.RSI(c, timeperiod=14)
        adx = talib.ADX(h, l, c, timeperiod=14)
        vol_ma = talib.SMA(v, timeperiod=20)
        macd_line, macd_signal, macd_hist = talib.MACD(c)

        high_60 = np.nanmax(h[-60:])
        low_60 = np.nanmin(l[-60:])
        price_range = high_60 - low_60

        vol_ma_val = vol_ma[-1] if not np.isnan(vol_ma[-1]) and vol_ma[-1] > 0 else 1

        factors = {
            'momentum_20d': float(roc_20[-1]) if not np.isnan(roc_20[-1]) else 0,
            'momentum_60d': float(roc_60[-1]) if not np.isnan(roc_60[-1]) else 0,
            'volatility': float(atr[-1] / c[-1]) if not np.isnan(atr[-1]) and c[-1] > 0 else 0,
            'rsi_14': float(rsi[-1]) if not np.isnan(rsi[-1]) else 50,
            'adx_14': float(adx[-1]) if not np.isnan(adx[-1]) else 0,
            'turnover_ratio': float(v[-1] / vol_ma_val) if vol_ma_val > 0 else 1,
            'price_position': float((c[-1] - low_60) / price_range) if price_range > 0 else 0.5,
            'macd_signal': float(macd_hist[-1]) if not np.isnan(macd_hist[-1]) else 0,
            'close': float(c[-1]),
        }
        return factors
    except Exception:
        return None


def batch_calc_factors(all_data, progress_callback=None):
    """批量计算所有股票的因子"""
    factor_dict = {}
    codes = list(all_data.keys())

    for i, code in enumerate(codes):
        df = all_data[code]
        f = calc_all_factors(df)
        if f is not None:
            factor_dict[code] = f

        if progress_callback:
            progress_callback(i + 1, len(codes), code)

    return pd.DataFrame(factor_dict).T


def score_stocks(factor_df, factor_config):
    """多因子打分"""
    result = factor_df.copy()
    result['score'] = 0.0

    for fname, cfg in factor_config.items():
        if fname not in result.columns:
            continue

        # 横截面排名归一化 (0~1)
        rank = result[fname].rank(pct=True)

        # 反向因子翻转
        if cfg['direction'] < 0:
            rank = 1 - rank

        result[f'{fname}_rank'] = rank
        result['score'] += rank * cfg['weight']

    return result.sort_values('score', ascending=False)


# ============================================================
# 主界面
# ============================================================

def main():
    # 标题
    st.markdown('<h1 class="main-header">📊 多因子选股器</h1>', unsafe_allow_html=True)
    st.markdown('---')

    # 侧边栏 - 全局配置
    with st.sidebar:
        st.header('⚙️ 全局配置')

        # 日期范围
        st.subheader('📅 数据范围')
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                '开始日期',
                value=datetime.now() - timedelta(days=365),
                key='start_date'
            )
        with col2:
            end_date = st.date_input(
                '结束日期',
                value=datetime.now(),
                key='end_date'
            )

        st.markdown('---')

        # 预设策略
        st.subheader('📋 策略模板')
        template = st.selectbox(
            '选择预设策略',
            options=['自定义'] + list(STRATEGY_TEMPLATES.keys()),
            index=0
        )

        if template != '自定义':
            st.info(STRATEGY_TEMPLATES[template]['desc'])

        st.markdown('---')

        # 选股数量
        st.subheader('🔢 选股配置')
        top_n = st.slider('选股数量', min_value=5, max_value=50, value=20)

        # 筛选条件
        st.subheader('🔍 筛选条件')
        min_price = st.number_input('最低价格', value=3.0, step=0.5)
        max_price = st.number_input('最高价格', value=500.0, step=10.0)

        st.markdown('---')

        # 因子数据源
        st.subheader('📦 因子数据')
        # 显示已有因子日期
        try:
            existing_dates = get_factor_dates()
            if existing_dates:
                date_options = {f"{d['calc_date']} ({d['stock_count']}只)": d['calc_date'] for d in existing_dates[:10]}
                date_options['-- 从数据库加载 --'] = 'load_from_db'
                date_options['-- 重新计算 --'] = 'recalculate'
            else:
                date_options = {'-- 重新计算 --': 'recalculate'}
        except:
            date_options = {'-- 重新计算 --': 'recalculate'}

        data_source = st.selectbox('数据来源', options=list(date_options.keys()), index=0)
        selected_date = date_options[data_source]

        # 运行按钮
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            run_button = st.button('🚀 计算因子', type='primary', use_container_width=True)
        with col_btn2:
            if st.session_state.get('raw_factor_df') is not None:
                rescore_button = st.button('🔄 重新打分', type='secondary', use_container_width=True)
            else:
                rescore_button = False

        # 保存按钮（计算后显示）
        if st.session_state.get('raw_factor_df') is not None:
            if st.button('💾 保存因子到数据库', type='secondary', use_container_width=True):
                st.session_state['save_factors'] = True

    # 主区域 - 添加因子管理Tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs(['🎯 因子配置', '📊 选股结果', '📈 因子分析', '💾 数据导出', '🗄️ 因子管理'])

    # ==================== Tab1: 因子配置 ====================
    with tab1:
        st.header('因子权重配置')

        # 根据模板初始化权重
        if template != '自定义':
            default_weights = STRATEGY_TEMPLATES[template]['weights']
        else:
            default_weights = {k: v['default_weight'] for k, v in FACTOR_DEFINITIONS.items()}

        # 权重输入
        weights = {}
        cols = st.columns(2)

        for i, (fname, fdef) in enumerate(FACTOR_DEFINITIONS.items()):
            col = cols[i % 2]
            with col:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{fdef['icon']} {fdef['name']}**")
                        st.caption(fdef['desc'])
                    with c2:
                        w = st.number_input(
                            '权重',
                            min_value=0.0,
                            max_value=1.0,
                            value=default_weights.get(fname, 0.1),
                            step=0.05,
                            key=f'weight_{fname}',
                            label_visibility='collapsed'
                        )
                        weights[fname] = w

        # 权重总和检查
        total_weight = sum(weights.values())
        st.markdown('---')
        weight_col1, weight_col2, weight_col3 = st.columns([2, 1, 1])
        with weight_col1:
            st.metric('权重总和', f'{total_weight:.2f}')
        with weight_col2:
            if abs(total_weight - 1.0) > 0.01:
                st.error('⚠️ 权重总和应为1.0')
            else:
                st.success('✅ 权重配置正常')
        with weight_col3:
            if st.button('🔄 重置权重'):
                st.rerun()

        # 权重可视化
        st.subheader('权重分布图')
        weight_df = pd.DataFrame([
            {'因子': FACTOR_DEFINITIONS[k]['name'], '权重': v, '颜色': FACTOR_DEFINITIONS[k]['color']}
            for k, v in weights.items() if v > 0
        ])

        if len(weight_df) > 0:
            fig = px.pie(
                weight_df,
                values='权重',
                names='因子',
                color='因子',
                color_discrete_map={FACTOR_DEFINITIONS[k]['name']: FACTOR_DEFINITIONS[k]['color']
                                   for k in weights.keys() if weights[k] > 0},
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                height=400,
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=-0.2)
            )
            st.plotly_chart(fig, use_container_width=True)

    # ==================== Tab2: 选股结果 ====================
    with tab2:
        st.header('选股结果')

        # 初始化session state
        if 'factor_df' not in st.session_state:
            st.session_state.factor_df = None
        if 'scored_df' not in st.session_state:
            st.session_state.scored_df = None
        if 'all_data' not in st.session_state:
            st.session_state.all_data = None
        if 'raw_factor_df' not in st.session_state:
            st.session_state.raw_factor_df = None
        if 'factor_calc_date' not in st.session_state:
            st.session_state.factor_calc_date = None

        # 构建因子配置（用于打分）
        factor_config = {}
        for fname, w in weights.items():
            factor_config[fname] = {
                'direction': FACTOR_DEFINITIONS[fname]['direction'],
                'weight': w
            }

        # 从数据库加载因子
        if selected_date not in ['recalculate', 'load_from_db'] and run_button:
            with st.spinner(f'从数据库加载 {selected_date} 的因子...'):
                factor_df = load_factors(selected_date)
                if not factor_df.empty:
                    st.session_state.raw_factor_df = factor_df.copy()
                    st.session_state.factor_calc_date = selected_date
                    st.success(f'从数据库加载 {len(factor_df)} 只股票的因子')
                else:
                    st.error('数据库中没有该日期的因子数据')

        # 重新打分（仅用已有因子，不重新计算）
        if rescore_button and st.session_state.raw_factor_df is not None:
            with st.spinner('正在重新打分...'):
                factor_df = st.session_state.raw_factor_df[
                    (st.session_state.raw_factor_df['close'] >= min_price) &
                    (st.session_state.raw_factor_df['close'] <= max_price)
                ]
                scored_df = score_stocks(factor_df, factor_config)
                st.session_state.factor_df = factor_df
                st.session_state.scored_df = scored_df
                st.success(f'重新打分完成！共 {len(scored_df)} 只股票')

        # 保存因子到数据库
        if st.session_state.get('save_factors') and st.session_state.raw_factor_df is not None:
            calc_date = end_date if isinstance(end_date, str) else str(end_date)
            with st.spinner(f'保存因子到数据库 (日期: {calc_date})...'):
                count = batch_save_factors(st.session_state.raw_factor_df, calc_date)
                st.success(f'已保存 {count} 只股票的因子到数据库')
                st.session_state.factor_calc_date = calc_date
                st.session_state['save_factors'] = False

        # 完整计算（加载数据 + 计算因子）
        if run_button and (selected_date == 'recalculate' or st.session_state.raw_factor_df is None):
            if abs(total_weight - 1.0) > 0.01:
                st.error('请先调整权重总和为1.0')
            else:
                # 加载数据
                with st.spinner('正在加载数据...'):
                    all_data = load_stock_data(str(start_date), str(end_date))
                    st.session_state.all_data = all_data

                if not all_data:
                    st.error('未加载到数据，请检查数据库连接和日期范围')
                else:
                    st.success(f'成功加载 {len(all_data)} 只股票数据')

                    # 计算因子
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def update_progress(current, total, code):
                        progress_bar.progress(current / total)
                        status_text.text(f'计算因子: {code} ({current}/{total})')

                    factor_df = batch_calc_factors(all_data, update_progress)

                    # 保存原始因子（未筛选）
                    st.session_state.raw_factor_df = factor_df.copy()
                    st.session_state.factor_calc_date = str(end_date)

                    progress_bar.empty()
                    status_text.empty()

                    if factor_df.empty:
                        st.error('因子计算失败')
                    else:
                        # 价格筛选
                        factor_df = factor_df[
                            (factor_df['close'] >= min_price) &
                            (factor_df['close'] <= max_price)
                        ]

                        # 打分
                        scored_df = score_stocks(factor_df, factor_config)
                        st.session_state.factor_df = factor_df
                        st.session_state.scored_df = scored_df
                        st.success(f'因子计算完成！共 {len(scored_df)} 只股票')

        # 显示结果
        if st.session_state.scored_df is not None:
            scored_df = st.session_state.scored_df

            # 统计卡片
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric('股票总数', len(scored_df))
            with col2:
                st.metric('选股数量', min(top_n, len(scored_df)))
            with col3:
                top_avg_score = scored_df.head(top_n)['score'].mean()
                st.metric('Top-N平均得分', f'{top_avg_score:.4f}')
            with col4:
                st.metric('得分标准差', f'{scored_df["score"].std():.4f}')

            st.markdown('---')

            # Top-N结果表格
            st.subheader(f'🏆 Top-{top_n} 股票')

            display_cols = ['score', 'close', 'momentum_20d', 'momentum_60d',
                           'volatility', 'rsi_14', 'adx_14', 'turnover_ratio', 'price_position']

            top_df = scored_df.head(top_n)[display_cols].copy()
            top_df.index.name = '股票代码'
            top_df = top_df.reset_index()
            top_df['score'] = top_df['score'].round(4)
            top_df['排名'] = range(1, len(top_df) + 1)

            # 格式化显示
            format_dict = {
                'close': '{:.2f}',
                'momentum_20d': '{:+.2f}%',
                'momentum_60d': '{:+.2f}%',
                'volatility': '{:.4f}',
                'rsi_14': '{:.1f}',
                'adx_14': '{:.1f}',
                'turnover_ratio': '{:.2f}',
                'price_position': '{:.3f}'
            }

            st.dataframe(
                top_df.style.format(format_dict).background_gradient(
                    subset=['score'], cmap='RdYlGn'
                ),
                use_container_width=True,
                hide_index=True
            )

            # 得分分布图
            st.subheader('得分分布')
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=scored_df['score'],
                nbinsx=50,
                marker_color='#667eea',
                opacity=0.75
            ))
            fig.update_layout(
                xaxis_title='综合得分',
                yaxis_title='股票数量',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info('👆 请在侧边栏配置参数后点击"开始选股"')

    # ==================== Tab3: 因子分析 ====================
    with tab3:
        st.header('因子分析')

        if st.session_state.factor_df is not None:
            factor_df = st.session_state.factor_df

            # 因子相关性热力图
            st.subheader('因子相关性')
            factor_cols = list(FACTOR_DEFINITIONS.keys())
            corr_matrix = factor_df[factor_cols].corr()

            fig = px.imshow(
                corr_matrix,
                labels=dict(color='相关性'),
                color_continuous_scale='RdBu_r',
                aspect='auto'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            # 因子分布箱线图
            st.subheader('因子分布')
            selected_factors = st.multiselect(
                '选择要展示的因子',
                options=factor_cols,
                default=['momentum_20d', 'volatility', 'rsi_14'],
                format_func=lambda x: FACTOR_DEFINITIONS[x]['name']
            )

            if selected_factors:
                fig = go.Figure()
                for fname in selected_factors:
                    fig.add_trace(go.Box(
                        y=factor_df[fname],
                        name=FACTOR_DEFINITIONS[fname]['name'],
                        marker_color=FACTOR_DEFINITIONS[fname]['color']
                    ))
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

            # 因子统计描述
            st.subheader('因子统计')
            stats_df = factor_df[factor_cols].describe().T
            stats_df['因子'] = stats_df.index.map(lambda x: FACTOR_DEFINITIONS[x]['name'])
            st.dataframe(stats_df[['因子', 'count', 'mean', 'std', 'min', 'max']], use_container_width=True)

        else:
            st.info('请先运行选股获取因子数据')

    # ==================== Tab4: 数据导出 ====================
    with tab4:
        st.header('数据导出')

        if st.session_state.scored_df is not None:
            scored_df = st.session_state.scored_df

            col1, col2 = st.columns(2)

            with col1:
                st.subheader('导出格式')
                export_format = st.radio('选择格式', ['CSV', 'Excel'])

                st.subheader('导出范围')
                export_range = st.radio(
                    '选择范围',
                    [f'Top-{top_n}', '全部股票']
                )

            with col2:
                st.subheader('导出预览')
                if export_range == f'Top-{top_n}':
                    preview_df = scored_df.head(top_n)
                else:
                    preview_df = scored_df

                st.dataframe(preview_df.head(10), use_container_width=True)

            # 导出按钮
            st.markdown('---')
            if st.button('📥 导出数据', type='primary'):
                # 准备导出数据
                export_df = scored_df.copy()
                export_df.index.name = 'stock_code'
                export_df = export_df.reset_index()

                if export_format == 'CSV':
                    csv = export_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label='下载 CSV',
                        data=csv,
                        file_name=f'multi_factor_stocks_{datetime.now().strftime("%Y%m%d")}.csv',
                        mime='text/csv'
                    )
                else:
                    from io import BytesIO
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        export_df.to_excel(writer, index=False, sheet_name='选股结果')
                    buffer.seek(0)
                    st.download_button(
                        label='下载 Excel',
                        data=buffer,
                        file_name=f'multi_factor_stocks_{datetime.now().strftime("%Y%m%d")}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )

            # 策略配置导出
            st.markdown('---')
            st.subheader('策略配置')
            config_str = f"""# 多因子选股配置
# 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# 因子权重
FACTOR_WEIGHTS = {{
{chr(10).join(f"    '{k}': {v}," for k, v in weights.items())}
}}

# 筛选条件
MIN_PRICE = {min_price}
MAX_PRICE = {max_price}
TOP_N = {top_n}
"""
            st.code(config_str, language='python')

            if st.button('📋 复制配置'):
                st.success('配置已复制到剪贴板!')

        else:
            st.info('请先运行选股获取数据')

    # ==================== Tab5: 因子管理 ====================
    with tab5:
        st.header('🗄️ 因子数据管理')

        # 初始化表
        st.subheader('1. 初始化因子表')
        if st.button('创建/检查因子表', type='primary'):
            try:
                create_factor_table()
                st.success('✅ 因子表已就绪')
            except Exception as e:
                st.error(f'创建失败: {e}')

        st.markdown('---')

        # 已有因子数据
        st.subheader('2. 已有因子数据')
        try:
            dates = get_factor_dates()
            if dates:
                st.write(f"共 {len(dates)} 个日期的因子数据")

                # 转换为DataFrame显示
                dates_df = pd.DataFrame(dates)
                dates_df['calc_date'] = pd.to_datetime(dates_df['calc_date'])
                dates_df = dates_df.sort_values('calc_date', ascending=False)
                dates_df.columns = ['计算日期', '股票数量']

                st.dataframe(
                    dates_df.head(20),
                    use_container_width=True,
                    hide_index=True
                )

                # 删除功能
                st.markdown('**删除因子数据**')
                col_del1, col_del2 = st.columns([2, 1])
                with col_del1:
                    delete_date = st.selectbox(
                        '选择要删除的日期',
                        options=[d['calc_date'] for d in dates]
                    )
                with col_del2:
                    if st.button('🗑️ 删除', type='secondary'):
                        deleted = delete_factors_by_date(delete_date)
                        st.warning(f'已删除 {delete_date} 的 {deleted} 条记录')
                        st.rerun()
            else:
                st.info('暂无因子数据，请先计算并保存')
        except Exception as e:
            st.warning(f'查询失败: {e}（可能表不存在）')

        st.markdown('---')

        # 批量计算历史因子
        st.subheader('3. 批量计算历史因子')
        st.info('选择日期范围，批量计算并保存历史因子数据')

        col_hist1, col_hist2 = st.columns(2)
        with col_hist1:
            hist_start = st.date_input('开始日期', value=datetime.now() - timedelta(days=365))
        with col_hist2:
            hist_end = st.date_input('结束日期', value=datetime.now())

        if st.button('🔢 批量计算并保存', type='primary'):
            st.info('此功能需要较长时间，建议在后台运行脚本完成')
            st.code(f"""
# 批量计算脚本
from factor_storage import batch_save_factors
from multi_factor_selector import load_stock_data, batch_calc_factors

# 加载数据
all_data = load_stock_data('{hist_start}', '{hist_end}')

# 计算因子
factor_df = batch_calc_factors(all_data)

# 保存到数据库
batch_save_factors(factor_df, '{hist_end}')
""", language='python')

        st.markdown('---')

        # 当前会话因子信息
        st.subheader('4. 当前会话因子')
        if st.session_state.get('raw_factor_df') is not None:
            factor_df = st.session_state.raw_factor_df
            calc_date = st.session_state.get('factor_calc_date', '未保存')

            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric('股票数量', len(factor_df))
            with col_info2:
                st.metric('因子数量', len([c for c in factor_df.columns if c != 'close']))
            with col_info3:
                st.metric('计算日期', calc_date)

            # 保存当前因子
            if st.button('💾 保存当前因子到数据库', type='primary'):
                save_date = end_date if isinstance(end_date, str) else str(end_date)
                count = batch_save_factors(factor_df, save_date)
                st.success(f'已保存 {count} 条记录到数据库 (日期: {save_date})')
                st.session_state.factor_calc_date = save_date
        else:
            st.info('当前会话尚未计算因子')


if __name__ == '__main__':
    main()
