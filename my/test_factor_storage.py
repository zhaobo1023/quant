# -*- coding: utf-8 -*-
"""
因子存储模块单元测试

运行: python test_factor_storage.py
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from factor_storage import (
    create_factor_table, save_factors, batch_save_factors,
    load_factors, load_factors_range, get_latest_factor_date,
    get_factor_dates, delete_factors_by_date
)
from db_config import execute_query, get_connection


class TestFactorStorage(unittest.TestCase):
    """因子存储模块测试"""

    @classmethod
    def setUpClass(cls):
        """测试前准备"""
        print("\n" + "=" * 50)
        print("因子存储模块单元测试")
        print("=" * 50)

        # 确保表存在
        create_factor_table()

        # 测试日期
        cls.test_date = date.today()
        cls.test_date_str = cls.test_date.strftime('%Y-%m-%d')

        # 构造测试数据
        cls.test_factor_df = pd.DataFrame({
            'momentum_20d': [5.5, -3.2, 12.8],
            'momentum_60d': [15.2, -8.5, 25.3],
            'volatility': [0.025, 0.038, 0.019],
            'rsi_14': [55.0, 35.5, 72.0],
            'adx_14': [25.5, 18.2, 32.0],
            'turnover_ratio': [1.2, 0.8, 1.5],
            'price_position': [0.65, 0.25, 0.85],
            'macd_signal': [0.5, -0.3, 0.8],
            'close': [25.50, 18.20, 45.80]
        }, index=['TEST001.SH', 'TEST002.SZ', 'TEST003.SH'])

    def test_01_save_factors(self):
        """测试保存因子"""
        print("\n[TEST 01] 测试保存因子...")

        count = save_factors(self.test_factor_df, self.test_date)
        self.assertEqual(count, 3, "应保存3条记录")
        print(f"  ✅ 保存成功: {count} 条记录")

    def test_02_load_factors(self):
        """测试加载因子"""
        print("\n[TEST 02] 测试加载因子...")

        df = load_factors(self.test_date)
        self.assertEqual(len(df), 3, "应加载3条记录")
        self.assertIn('TEST001.SH', df.index, "应包含TEST001.SH")
        self.assertIn('momentum_20d', df.columns, "应包含momentum_20d列")

        # 验证数值
        self.assertAlmostEqual(
            df.loc['TEST001.SH', 'momentum_20d'], 5.5, places=2,
            msg="momentum_20d值应匹配"
        )
        print(f"  ✅ 加载成功: {len(df)} 条记录")

    def test_03_load_specific_stocks(self):
        """测试加载指定股票"""
        print("\n[TEST 03] 测试加载指定股票...")

        df = load_factors(self.test_date, stock_codes=['TEST001.SH', 'TEST002.SZ'])
        self.assertEqual(len(df), 2, "应加载2条记录")
        print(f"  ✅ 指定股票加载成功: {len(df)} 条记录")

    def test_04_update_factors(self):
        """测试更新因子（同一日期重复保存）"""
        print("\n[TEST 04] 测试更新因子...")

        # 修改数据
        updated_df = self.test_factor_df.copy()
        updated_df.loc['TEST001.SH', 'momentum_20d'] = 8.8

        count = save_factors(updated_df, self.test_date)
        self.assertEqual(count, 3, "应更新3条记录")

        # 验证更新
        df = load_factors(self.test_date)
        self.assertAlmostEqual(
            df.loc['TEST001.SH', 'momentum_20d'], 8.8, places=2,
            msg="momentum_20d应更新为8.8"
        )
        print(f"  ✅ 更新成功")

    def test_05_get_factor_dates(self):
        """测试获取因子日期列表"""
        print("\n[TEST 05] 测试获取因子日期列表...")

        dates = get_factor_dates()
        self.assertIsInstance(dates, list, "应返回列表")
        self.assertTrue(len(dates) >= 1, "应至少有1个日期")

        # 检查是否包含测试日期
        date_strs = [str(d['calc_date']) for d in dates]
        self.assertIn(self.test_date_str, date_strs, f"应包含测试日期 {self.test_date_str}")
        print(f"  ✅ 获取成功: {len(dates)} 个日期")

    def test_06_get_latest_factor_date(self):
        """测试获取最新因子日期"""
        print("\n[TEST 06] 测试获取最新因子日期...")

        latest = get_latest_factor_date()
        self.assertIsNotNone(latest, "应返回日期")
        self.assertEqual(str(latest), self.test_date_str, "最新日期应为测试日期")
        print(f"  ✅ 最新日期: {latest}")

    def test_07_load_factors_range(self):
        """测试加载日期范围"""
        print("\n[TEST 07] 测试加载日期范围...")

        df = load_factors_range(self.test_date, self.test_date)
        self.assertEqual(len(df), 3, "应加载3条记录")
        print(f"  ✅ 日期范围加载成功")

    def test_08_batch_save_factors(self):
        """测试批量保存"""
        print("\n[TEST 08] 测试批量保存...")

        # 构造更多测试数据
        batch_df = pd.DataFrame({
            'momentum_20d': [i * 0.5 for i in range(10)],
            'momentum_60d': [i * 1.0 for i in range(10)],
            'volatility': [0.02 + i * 0.001 for i in range(10)],
            'rsi_14': [50 + i for i in range(10)],
            'adx_14': [20 + i for i in range(10)],
            'turnover_ratio': [1.0 for i in range(10)],
            'price_position': [0.5 for i in range(10)],
            'macd_signal': [0.1 * i for i in range(10)],
            'close': [20 + i for i in range(10)]
        }, index=[f'BATCH{i:03d}.SH' for i in range(10)])

        new_date = date.today()
        count = batch_save_factors(batch_df, new_date, batch_size=5)
        self.assertEqual(count, 10, "应保存10条记录")
        print(f"  ✅ 批量保存成功: {count} 条记录")

    def test_09_data_integrity(self):
        """测试数据完整性"""
        print("\n[TEST 09] 测试数据完整性...")

        df = load_factors(self.test_date)

        # 检查所有因子列都存在
        expected_cols = [
            'momentum_20d', 'momentum_60d', 'volatility', 'rsi_14',
            'adx_14', 'turnover_ratio', 'price_position', 'macd_signal', 'close'
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"应包含 {col} 列")

        # 检查无空值
        for col in expected_cols:
            null_count = df[col].isnull().sum()
            self.assertEqual(null_count, 0, f"{col} 不应有空值")

        print(f"  ✅ 数据完整性验证通过")

    def test_10_delete_factors_by_date(self):
        """测试删除因子"""
        print("\n[TEST 10] 测试删除因子...")

        # 先创建一条待删除的数据
        delete_date = date(2020, 1, 1)
        test_df = pd.DataFrame({
            'momentum_20d': [1.0],
            'momentum_60d': [2.0],
            'volatility': [0.01],
            'rsi_14': [50.0],
            'adx_14': [20.0],
            'turnover_ratio': [1.0],
            'price_position': [0.5],
            'macd_signal': [0.0],
            'close': [10.0]
        }, index=['DELETE_ME.SH'])

        save_factors(test_df, delete_date)

        # 验证已保存
        df = load_factors(delete_date)
        self.assertEqual(len(df), 1, "应保存1条记录")

        # 删除
        deleted = delete_factors_by_date(delete_date)
        self.assertEqual(deleted, 1, "应删除1条记录")

        # 验证已删除
        df = load_factors(delete_date)
        self.assertEqual(len(df), 0, "删除后应为0条记录")

        print(f"  ✅ 删除成功")

    @classmethod
    def tearDownClass(cls):
        """测试后清理"""
        print("\n" + "=" * 50)
        # 清理测试数据
        try:
            delete_factors_by_date(cls.test_date)
            # 清理批量测试数据
            today = date.today()
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trade_stock_factor WHERE stock_code LIKE 'BATCH%'")
            cursor.execute("DELETE FROM trade_stock_factor WHERE stock_code LIKE 'TEST%'")
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ 测试数据已清理")
        except Exception as e:
            print(f"⚠️ 清理测试数据失败: {e}")
        print("=" * 50)


class TestFactorCalculation(unittest.TestCase):
    """因子计算测试"""

    def test_factor_calculation_logic(self):
        """测试因子计算逻辑"""
        print("\n[TEST] 测试因子计算逻辑...")

        # 构造模拟K线数据
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)

        df = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'high': 101 + np.cumsum(np.random.randn(100) * 0.5),
            'low': 99 + np.cumsum(np.random.randn(100) * 0.5),
            'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)

        # 确保high >= close >= low
        df['high'] = df[['open', 'close']].max(axis=1) + np.abs(np.random.randn(100)) * 0.5
        df['low'] = df[['open', 'close']].min(axis=1) - np.abs(np.random.randn(100)) * 0.5

        # 导入计算函数
        from multi_factor_selector import calc_all_factors

        factors = calc_all_factors(df)

        self.assertIsNotNone(factors, "因子计算不应返回None")
        self.assertIn('momentum_20d', factors, "应包含momentum_20d")
        self.assertIn('rsi_14', factors, "应包含rsi_14")
        self.assertIn('close', factors, "应包含close")

        # RSI应在0-100之间
        self.assertGreaterEqual(factors['rsi_14'], 0, "RSI应>=0")
        self.assertLessEqual(factors['rsi_14'], 100, "RSI应<=100")

        # 波动率应大于0
        self.assertGreater(factors['volatility'], 0, "波动率应>0")

        print(f"  ✅ 因子计算测试通过")
        print(f"     momentum_20d: {factors['momentum_20d']:.2f}")
        print(f"     rsi_14: {factors['rsi_14']:.2f}")
        print(f"     volatility: {factors['volatility']:.4f}")


class TestFactorScoring(unittest.TestCase):
    """因子打分测试"""

    def test_scoring_logic(self):
        """测试打分逻辑"""
        print("\n[TEST] 测试打分逻辑...")

        from multi_factor_selector import score_stocks, FACTOR_DEFINITIONS

        # 构造测试因子数据
        factor_df = pd.DataFrame({
            'momentum_20d': [5.0, -5.0, 10.0],
            'momentum_60d': [10.0, -10.0, 20.0],
            'volatility': [0.02, 0.05, 0.01],
            'rsi_14': [60, 30, 70],
            'adx_14': [25, 15, 35],
            'turnover_ratio': [1.5, 0.5, 2.0],
            'price_position': [0.5, 0.1, 0.9],
            'macd_signal': [0.5, -0.5, 1.0],
            'close': [100, 50, 150]
        }, index=['STOCK_A', 'STOCK_B', 'STOCK_C'])

        # 构造因子配置
        factor_config = {
            name: {
                'direction': FACTOR_DEFINITIONS[name]['direction'],
                'weight': FACTOR_DEFINITIONS[name]['default_weight']
            }
            for name in FACTOR_DEFINITIONS.keys()
        }

        scored_df = score_stocks(factor_df, factor_config)

        self.assertIn('score', scored_df.columns, "应包含score列")
        self.assertEqual(len(scored_df), 3, "应有3条记录")

        # 得分应在0-1之间
        self.assertTrue((scored_df['score'] >= 0).all(), "得分应>=0")
        self.assertTrue((scored_df['score'] <= 1).all(), "得分应<=1")

        # 检查排序（得分降序）
        scores = scored_df['score'].values
        self.assertTrue(scores[0] >= scores[1], "应按得分降序排列")

        print(f"  ✅ 打分逻辑测试通过")
        print(f"     得分排序: {list(scored_df.index)}")


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestFactorStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestFactorCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestFactorScoring))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
