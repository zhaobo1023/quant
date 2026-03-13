import { useState, useRef } from 'react'
import axios from 'axios'
import { Upload, Camera, Check, X, AlertCircle } from 'lucide-react'

export default function OCRPage() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
      setResult(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setLoading(true)
    try {
      const response = await axios.post('/api/ocr/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(response.data)
    } catch (error) {
      alert('OCR识别失败')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setPreview('')
    setResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">OCR识别</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 上传区域 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">上传持仓截图</h3>

          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
          >
            {preview ? (
              <img src={preview} alt="Preview" className="max-h-64 mx-auto rounded-lg" />
            ) : (
              <>
                <Camera className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">点击上传券商APP持仓截图</p>
                <p className="text-sm text-gray-400 mt-2">支持 JPG、PNG 格式</p>
              </>
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />

          <div className="flex space-x-3 mt-4">
            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                  识别中...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  开始识别
                </>
              )}
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 text-gray-600 hover:text-gray-900"
            >
              重置
            </button>
          </div>
        </div>

        {/* 识别结果 */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">识别结果</h3>

          {!result ? (
            <div className="text-center py-12 text-gray-500">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>上传图片后开始识别</p>
            </div>
          ) : result.success ? (
            <div>
              <div className="flex items-center text-green-600 mb-4">
                <Check className="h-5 w-5 mr-2" />
                识别成功!发现 {result.positions?.length || 0} 个持仓
              </div>

              {result.positions && result.positions.length > 0 && (
                <div className="space-y-3">
                  {result.positions.map((pos: any, idx: number) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">{pos.stock_name}</p>
                          <p className="text-sm text-gray-600">{pos.stock_code}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{pos.shares}股</p>
                          <p className="text-sm text-gray-600">@ ¥{pos.cost_price}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-red-500">
              <X className="h-12 w-12 mx-auto mb-4" />
              <p>{result.error || '识别失败'}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
