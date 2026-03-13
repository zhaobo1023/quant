import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Plus, Trash2, Edit2, Save, X, TrendingUp, TrendingDown,
  Wallet, RefreshCw, Filter
} from 'lucide-react'

// 类型定义
interface Position {
  id: number
  stock_code: string
  stock_name: string | null
  shares: number
  cost_price: number
  is_margin: boolean
  account_tag: string
  notes: string | null
  status: number
  created_at: string
  updated_at: string
}

interface PositionFormData {
  stock_code: string
  stock_name: string
  shares: number
  cost_price: number
  is_margin: boolean
  account_tag: string
  notes: string
}

const initialFormData: PositionFormData = {
  stock_code: '',
  stock_name: '',
  shares: 100,
  cost_price: 0,
  is_margin: false,
  account_tag: 'default',
  notes: ''
}

export default function PositionsPage() {
  const [positions, setPositions] = useState<Position[]>([])
  const [accounts, setAccounts] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<PositionFormData>(initialFormData)
  const [filterAccount, setFilterAccount] = useState<string>('')
  const [filterStatus, setFilterStatus] = useState<number | undefined>(1)

  // 获取持仓列表
  const fetchPositions = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (filterAccount) params.append('account_tag', filterAccount)
      if (filterStatus !== undefined) params.append('status', filterStatus.toString())

      const response = await axios.get(`/api/positions?${params.toString()}`)
      setPositions(response.data)
    } catch (error) {
      console.error('获取持仓失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 获取账户列表
  const fetchAccounts = async () => {
    try {
      const response = await axios.get('/api/accounts')
      setAccounts(response.data)
    } catch (error) {
      console.error('获取账户列表失败:', error)
    }
  }

  useEffect(() => {
    fetchPositions()
    fetchAccounts()
  }, [filterAccount, filterStatus])

  // 创建持仓
  const handleCreate = async () => {
    try {
      await axios.post('/api/positions', formData)
      setShowForm(false)
      setFormData(initialFormData)
      fetchPositions()
      fetchAccounts()
      alert('持仓添加成功!')
    } catch (error: any) {
      alert(error.response?.data?.detail || '创建失败')
    }
  }

  // 更新持仓
  const handleUpdate = async (id: number) => {
    try {
      await axios.put(`/api/positions/${id}`, {
        stock_name: formData.stock_name,
        shares: formData.shares,
        cost_price: formData.cost_price,
        is_margin: formData.is_margin,
        account_tag: formData.account_tag,
        notes: formData.notes
      })
      setEditingId(null)
      setFormData(initialFormData)
      fetchPositions()
      fetchAccounts()
      alert('持仓更新成功!')
    } catch (error: any) {
      alert(error.response?.data?.detail || '更新失败')
    }
  }

  // 删除持仓
  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此持仓吗?')) return
    try {
      await axios.delete(`/api/positions/${id}`)
      fetchPositions()
      fetchAccounts()
      alert('持仓已删除!')
    } catch (error) {
      console.error('删除失败:', error)
      alert('删除失败')
    }
  }

  // 开始编辑
  const startEdit = (position: Position) => {
    setEditingId(position.id)
    setFormData({
      stock_code: position.stock_code,
      stock_name: position.stock_name || '',
      shares: position.shares,
      cost_price: position.cost_price,
      is_margin: position.is_margin,
      account_tag: position.account_tag,
      notes: position.notes || ''
    })
    setShowForm(false)
  }

  // 取消编辑/新建
  const cancelEdit = () => {
    setEditingId(null)
    setShowForm(false)
    setFormData(initialFormData)
  }

  // 计算市值
  const calcMarketValue = (shares: number, costPrice: number) => {
    return shares * costPrice
  }

  // 统计
  const totalValue = positions.reduce((sum, p) => sum + calcMarketValue(p.shares, p.cost_price), 0)
  const totalPositions = positions.length

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">持仓管理</h2>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">持仓数量</p>
              <p className="text-2xl font-bold text-gray-900">{totalPositions}</p>
            </div>
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <Wallet className="h-5 w-5 text-blue-500" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">持仓市值</p>
              <p className="text-2xl font-bold text-gray-900">
                ¥{(totalValue / 10000).toFixed(2)}万
              </p>
            </div>
            <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-green-500" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">账户数</p>
              <p className="text-2xl font-bold text-gray-900">{accounts.length || 1}</p>
            </div>
            <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center">
              <Filter className="h-5 w-5 text-purple-500" />
            </div>
          </div>
        </div>
      </div>

      {/* 工具栏 */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center space-x-4">
            <select
              value={filterAccount}
              onChange={(e) => setFilterAccount(e.target.value)}
              className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部账户</option>
              {accounts.map((acc) => (
                <option key={acc} value={acc}>{acc}</option>
              ))}
            </select>
            <select
              value={filterStatus ?? ''}
              onChange={(e) => setFilterStatus(e.target.value ? parseInt(e.target.value) : undefined)}
              className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部状态</option>
              <option value="1">持有中</option>
              <option value="0">已清仓</option>
            </select>
            <button
              onClick={fetchPositions}
              className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              刷新
            </button>
          </div>
          <button
            onClick={() => { setShowForm(true); setEditingId(null); }}
            className="flex items-center px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Plus className="h-4 w-4 mr-2" />
            新增持仓
          </button>
        </div>
      </div>

      {/* 新增/编辑表单 */}
      {(showForm || editingId) && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {editingId ? '编辑持仓' : '新增持仓'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">股票代码 *</label>
              <input
                type="text"
                value={formData.stock_code}
                onChange={(e) => setFormData({ ...formData, stock_code: e.target.value.toUpperCase() })}
                placeholder="如: 600519.SH"
                disabled={!!editingId}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">股票名称</label>
              <input
                type="text"
                value={formData.stock_name}
                onChange={(e) => setFormData({ ...formData, stock_name: e.target.value })}
                placeholder="如: 贵州茅台"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">持仓数量(股) *</label>
              <input
                type="number"
                value={formData.shares}
                onChange={(e) => setFormData({ ...formData, shares: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">成本价 *</label>
              <input
                type="number"
                step="0.01"
                value={formData.cost_price}
                onChange={(e) => setFormData({ ...formData, cost_price: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">账户标签</label>
              <input
                type="text"
                value={formData.account_tag}
                onChange={(e) => setFormData({ ...formData, account_tag: e.target.value })}
                placeholder="如: 融资账户, 主账户"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">是否融资</label>
              <select
                value={formData.is_margin ? '1' : '0'}
                onChange={(e) => setFormData({ ...formData, is_margin: e.target.value === '1' })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="0">否</option>
                <option value="1">是</option>
              </select>
            </div>
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">备注</label>
              <input
                type="text"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="备注信息"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex justify-end space-x-3 mt-4">
            <button
              onClick={cancelEdit}
              className="flex items-center px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              <X className="h-4 w-4 mr-1" />
              取消
            </button>
            <button
              onClick={() => editingId ? handleUpdate(editingId) : handleCreate()}
              disabled={!formData.stock_code || !formData.shares || !formData.cost_price}
              className="flex items-center px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="h-4 w-4 mr-1" />
              保存
            </button>
          </div>
        </div>
      )}

      {/* 持仓列表 */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">加载中...</div>
        ) : positions.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            暂无持仓数据,点击"新增持仓"添加
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">股票代码</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">股票名称</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">持仓数量</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">成本价</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">市值</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">账户</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">融资</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                  <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {positions.map((position) => (
                  <tr key={position.id} className="hover:bg-gray-50">
                    <td className="px-5 py-4 text-sm font-medium text-gray-900">
                      {position.stock_code}
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-600">
                      {position.stock_name || '-'}
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-900">
                      {position.shares.toLocaleString()}
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-900">
                      ¥{position.cost_price.toFixed(2)}
                    </td>
                    <td className="px-5 py-4 text-sm font-medium text-gray-900">
                      ¥{(calcMarketValue(position.shares, position.cost_price) / 10000).toFixed(2)}万
                    </td>
                    <td className="px-5 py-4">
                      <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700">
                        {position.account_tag}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      {position.is_margin ? (
                        <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-orange-100 text-orange-700">
                          融资
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600">
                          普通
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      {position.status === 1 ? (
                        <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
                          持有中
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600">
                          已清仓
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => startEdit(position)}
                          className="p-1.5 text-gray-400 hover:text-blue-500 transition-colors"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(position.id)}
                          className="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
