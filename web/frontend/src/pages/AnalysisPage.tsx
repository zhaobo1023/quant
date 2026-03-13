import { useState } from 'react'
import axios from 'axios'
import { TrendingUp, Search, RefreshCw } from 'lucide-react'

export default function AnalysisPage() {
  const [stockCode, setStockCode] = useState('')
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const analyzeStock = async () => {
    if (!stockCode) return

    setLoading(true)
    try {
      const response = await axios.get(`/api/reports/stock/${stockCode}`)
      setAnalysis(response.data)
    } catch (error) {
      alert('获取分析失败,请检查股票代码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">技术分析</h2>

      {/* 搜索框 */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <input
              type="text"
              value={stockCode}
              onChange={(e) => setStockCode(e.target.value.toUpperCase())}
              placeholder="输入股票代码,如: 600519.SH"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && analyzeStock()}
            />
          </div>
          <button
            onClick={analyzeStock}
            disabled={loading || !stockCode}
            className="flex items-center px-6 py-2 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Search className="h-4 w-4 mr-2" />
            )}
            分析
          </button>
        </div>
      </div>

      {/* 分析结果 */}
      {analysis && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 基本信息 */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">基本信息</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">股票名称</span>
                <span className="font-medium">{analysis.stock_name || stockCode}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">当前价格</span>
                <span className="font-medium">¥{analysis.current_price?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">风险等级</span>
                <span className={`font-medium ${
                  analysis.risk_level === '低风险' ? 'text-green-600' :
                  analysis.risk_level === '高风险' ? 'text-red-600' : 'text-yellow-600'
                }`}>
                  {analysis.risk_level || 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* 技术指标 */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">技术指标</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">MA20</span>
                <span className="font-medium">{analysis.ma20?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">MACD信号</span>
                <span className="font-medium">{analysis.macd_signal || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">RSI</span>
                <span className="font-medium">{analysis.rsi_6?.toFixed(2) || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!analysis && (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center text-gray-500">
          <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>输入股票代码进行技术分析</p>
        </div>
      )}
    </div>
  )
}
