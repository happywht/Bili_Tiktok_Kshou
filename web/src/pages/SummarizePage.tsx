import React, { useState } from 'react'
import { summaryApi, SummaryResult } from '@/api/summary'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Loader2, Sparkles, AlertCircle, CheckCircle2, Home, Search } from 'lucide-react'
import { VideoSummaryDialog } from '@/components/video/VideoSummaryDialog'

export const SummarizePage: React.FC = () => {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SummaryResult | null>(null)
  const [showDialog, setShowDialog] = useState(false)

  const isValidUrl = (value: string) => {
    try {
      const url = new URL(value)
      const hostname = url.hostname
      return (
        hostname.includes('bilibili.com') ||
        hostname.includes('douyin.com') ||
        hostname.includes('xiaohongshu.com')
      )
    } catch {
      return false
    }
  }

  const handleSummarize = async () => {
    if (!url.trim() || !isValidUrl(url)) {
      setError('请输入有效的视频URL（支持B站、抖音、小红书）')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await summaryApi.summarize(url.trim())
      setResult(data)
      setShowDialog(true)
    } catch (e: any) {
      const message = e.response?.data?.message || e.message || '总结失败'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const exampleUrls = [
    { label: 'B站示例', url: 'https://www.bilibili.com/video/BV1rpWjevEip' },
    { label: '抖音示例', url: 'https://www.douyin.com/video/7380154625771054386' },
    { label: '小红书示例', url: 'https://www.xiaohongshu.com/explore/65f8a8e8000000001e03a7e7' },
  ]

  return (
    <div className="container mx-auto max-w-4xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-primary" />
          AI 视频内容总结
        </h1>
        <p className="text-muted-foreground">
          输入视频链接，自动提取字幕并生成 AI 内容总结（支持 B站、抖音、小红书）
        </p>
      </div>

      <div className="bg-card rounded-xl border border-border p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">视频 URL</h2>
        <div className="space-y-4">
          <div className="space-y-2">
            <Input
              placeholder="粘贴视频链接（例如：https://www.bilibili.com/video/BVxxxxxx）"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value)
                setError(null)
              }}
              onKeyDown={(e) => e.key === 'Enter' && handleSummarize()}
              className="w-full"
            />
            {url && !isValidUrl(url) && (
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                请输入有效的 B站/抖音/小红书 视频链接
              </p>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleSummarize}
              disabled={loading || !url.trim()}
              className="flex-1"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  正在分析...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  开始总结
                </>
              )}
            </Button>
            {url && (
              <Button
                variant="outline"
                onClick={() => {
                  setUrl('')
                  setError(null)
                  setResult(null)
                }}
              >
                清空
              </Button>
            )}
          </div>

          {error && (
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 text-destructive p-3 text-sm">
              {error}
            </div>
          )}

          {result && (
            <div className="rounded-lg bg-green-50 border border-green-200 text-green-800 p-3 text-sm">
              <CheckCircle2 className="inline h-4 w-4 mr-2" />
              总结完成！{result.subtitle_length} 字字幕已分析
            </div>
          )}
        </div>
      </div>

      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="text-lg font-semibold mb-4">使用说明</h2>
        <div className="space-y-4 text-sm text-muted-foreground">
          <div>
            <h3 className="font-semibold text-foreground mb-2">支持的链接格式：</h3>
            <ul className="space-y-1 ml-4 list-disc">
              <li>B站：<code className="bg-muted px-1 py-0.5 rounded">https://www.bilibili.com/video/BVxxxxxx</code></li>
              <li>抖音：<code className="bg-muted px-1 py-0.5 rounded">https://www.douyin.com/video/xxxxxx</code></li>
              <li>小红书：<code className="bg-muted px-1 py-0.5 rounded">https://www.xiaohongshu.com/explore/xxxxxx</code></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-foreground mb-2">注意事项：</h3>
            <ul className="space-y-1 ml-4 list-disc">
              <li>需要配置智谱AI Key（在 .env 文件中设置 LLM_API_KEY）</li>
              <li>视频需要有字幕/CC字幕才能生成总结</li>
              <li>总结生成需要 15-30 秒，请耐心等待</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-foreground mb-2">快速示例：</h3>
            <div className="grid gap-2">
              {exampleUrls.map((ex) => (
                <div key={ex.label} className="flex items-center gap-2">
                  <Button
                    variant="link"
                    size="sm"
                    className="h-auto p-0 text-xs"
                    onClick={() => setUrl(ex.url)}
                  >
                    {ex.label}
                  </Button>
                  <code className="text-xs bg-muted px-2 py-1 rounded flex-1 truncate">
                    {ex.url}
                  </code>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <VideoSummaryDialog
        url={url}
        title="视频总结"
        open={showDialog}
        onClose={() => setShowDialog(false)}
      />
    </div>
  )
}

export default SummarizePage
