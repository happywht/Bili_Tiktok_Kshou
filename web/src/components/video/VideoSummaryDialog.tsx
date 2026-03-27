import React, { useState } from 'react'
import { X, Loader2, FileText, Sparkles, AlertTriangle } from 'lucide-react'
import { summaryApi, SummaryResult } from '@/api/summary'

interface VideoSummaryDialogProps {
  url: string
  title: string
  open: boolean
  onClose: () => void
}

export const VideoSummaryDialog: React.FC<VideoSummaryDialogProps> = ({
  url, title, open, onClose,
}) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SummaryResult | null>(null)
  const [inputUrl, setInputUrl] = useState(url)

  React.useEffect(() => {
    if (open && url) {
      setInputUrl(url)
      handleSummarize(url)
    } else {
      setResult(null)
      setError(null)
      setLoading(false)
    }
  }, [open, url])

  const handleSummarize = async (targetUrl?: string) => {
    const summaryUrl = targetUrl || inputUrl
    if (!summaryUrl.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await summaryApi.summarize(summaryUrl)
      setResult(data)
    } catch (e: any) {
      const message = e.response?.data?.message || e.message || '总结失败'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-background rounded-2xl shadow-2xl border border-border/50 w-full max-w-2xl max-h-[85vh] overflow-hidden m-4 animate-in fade-in zoom-in-95">
        {/* 标题栏 */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">AI 视频总结</h2>
          </div>
          <button
            onClick={onClose}
            className="rounded-full p-1.5 hover:bg-muted transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="p-4 space-y-4 overflow-y-auto max-h-[calc(85vh-60px)]">
          {/* 视频信息 */}
          <div className="text-sm text-muted-foreground truncate">
            <span className="font-medium text-foreground">{title || '视频总结'}</span>
          </div>

          {/* URL 输入 */}
          <div className="flex gap-2">
            <input
              type="text"
              value={inputUrl}
              onChange={(e) => setInputUrl(e.target.value)}
              placeholder="输入视频URL（B站/抖音/小红书）..."
              className="flex-1 px-3 py-2 text-sm rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
              onKeyDown={(e) => e.key === 'Enter' && handleSummarize()}
            />
            <button
              onClick={() => handleSummarize()}
              disabled={loading || !inputUrl.trim()}
              className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center gap-1.5 transition-colors"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              {loading ? '分析中...' : '总结'}
            </button>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
              <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* 总结结果 */}
          {result && (
            <div className="space-y-4">
              {/* AI 总结 */}
              <div className="rounded-lg border border-border/50 p-4 space-y-3">
                <div className="flex items-center gap-2 text-sm font-medium">
                  <Sparkles className="h-4 w-4 text-primary" />
                  AI 总结
                </div>
                <div className="text-sm leading-relaxed whitespace-pre-wrap">
                  {result.ai_summary}
                </div>
              </div>

              {/* 字幕预览 */}
              <details className="rounded-lg border border-border/50 overflow-hidden">
                <summary className="flex items-center gap-2 px-4 py-3 text-sm font-medium cursor-pointer hover:bg-muted/50 transition-colors">
                  <FileText className="h-4 w-4" />
                  字幕预览
                  <span className="text-muted-foreground font-normal">
                    （{result.extraction_method}，共 {result.subtitle_length} 字）
                  </span>
                </summary>
                <div className="px-4 pb-3">
                  <pre className="text-xs text-muted-foreground bg-muted/30 rounded-lg p-3 max-h-60 overflow-y-auto whitespace-pre-wrap">
                    {result.subtitle_preview}
                  </pre>
                </div>
              </details>
            </div>
          )}

          {/* 加载状态 */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Loader2 className="h-8 w-8 animate-spin mb-3" />
              <p className="text-sm">正在提取字幕并生成 AI 总结...</p>
              <p className="text-xs mt-1">这可能需要 15-30 秒</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
