import { useState, useEffect } from 'react'
import axios from 'axios'
import { FileText, RefreshCw, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react'

export default function ReportsPage() {
  const [report, setReport] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const fetchReport = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/reports/daily')
      setReport(response.data)
    } catch (error) {
      console.error('获取报告失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReport()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">每日分析报告</h2>
        <button
          onClick={fetchReport}
          className="flex items-center px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          刷新
        </button>
      </div>

      {report ? (
        <div className="space-y-6">
          {/* 汇总卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <p className="text-sm text-gray-500">报告日期</p>
              <p className="text-xl font-bold text-gray-900">{report.report_date}</p>
            </div>
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <p className="text-sm text-gray-500">持仓数量</p>
              <p className="text-xl font-bold text-gray-900">{report.position_count || 0}</p>
            </div>
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <p className="text-sm text-gray-500">总市值</p>
              <p className="text-xl font-bold text-gray-900">
                ¥{((report.total_value || 0) / 10000).toFixed(2)}万
              </p>
            </div>
            <div className="bg-white rounded-xl p-5 shadow-sm">
              <p className="text-sm text-gray-500">总盈亏</p>
              <p className={`text-xl font-bold ${
                (report.total_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {report.total_pnl >= 0 ? '+' : ''}
                ¥{(report.total_pnl || 0).toFixed(2)}
                ({report.total_pnl_pct >= 0 ? '+' : ''}{(report.total_pnl_pct || 0).toFixed(2)}%)
              </p>
            </div>
          </div>

          {/* 持仓详情 */}
          {report.positions && report.positions.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">持仓明细</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 text-sm font-medium text-gray-500">股票</th>
                      <th className="text-right py-3 text-sm font-medium text-gray-500">数量</th>
                      <th className="text-right py-3 text-sm font-medium text-gray-500">成本价</th>
                      <th className="text-right py-3 text-sm font-medium text-gray-500">盈亏</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.positions.map((pos: any, idx: number) => (
                      <tr key={idx} className="border-b last:border-0">
                        <td className="py-3">
                          <p className="font-medium">{pos.stock_name || pos.stock_code}</p>
                          <p className="text-sm text-gray-500">{pos.stock_code}</p>
                        </td>
                        <td className="text-right py-3">{pos.shares}</td>
                        <td className="text-right py-3">¥{pos.cost_price}</td>
                        <td className="text-right py-3">
                          <span className={pos.pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {pos.pnl >= 0 ? '+' : ''}{pos.pnl} ({pos.pnl_pct >= 0 ? '+' : ''}{pos.pnl_pct}%)
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 技术信号 */}
          {report.signals && report.signals.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">技术信号</h3>
              <div className="space-y-3">
                {report.signals.map((signal: any, idx: number) => (
                  <div key={idx} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      signal.signal_type === 'breakout' ? 'bg-green-100' :
                      signal.signal_type === 'breakdown' ? 'bg-red-100' :
                      'bg-yellow-100'
                    }`}>
                      {signal.signal_type === 'breakout' ? (
                        <TrendingUp className="h-5 w-5 text-green-600" />
                      ) : signal.signal_type === 'breakdown' ? (
                        <TrendingDown className="h-5 w-5 text-red-600" />
                      ) : (
                        <AlertTriangle className="h-5 w-5 text-yellow-600" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{signal.title}</p>
                      <p className="text-sm text-gray-600">{signal.description}</p>
                      <p className="text-xs text-gray-400 mt-1">{signal.stock_code}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      signal.signal_strength >= 4 ? 'bg-red-100 text-red-700' :
                      signal.signal_strength >= 3 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      强度: {signal.signal_strength}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500">暂无报告数据</p>
          <p className="text-sm text-gray-400 mt-2">请先添加持仓并同步数据</p>
        </div>
      )}
    </div>
  )
}
