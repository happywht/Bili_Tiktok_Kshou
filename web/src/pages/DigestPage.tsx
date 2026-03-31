import React, { useState } from 'react'
import { digestApi, DigestResult } from '@/api/digest'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Loader2, FileText, Download, Copy, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react'

export const DigestPage: React.FC = () => {
  const [keywords, setKeywords] = useState(['', '', ''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DigestResult | null>(null)
  const [copied, setCopied] = useState(false)

  // 设置关键词
  const handleKeywordChange = (index: number, value: string) => {
    const newKeywords = [...keywords]
    newKeywords[index] = value
    setKeywords(newKeywords)
  }

  // 添加关键词
  const addKeyword = () => {
    if (keywords.length < 5) {
      setKeywords([...keywords, ''])
    }
  }

  // 删除关键词
  const removeKeyword = (index: number) => {
    if (keywords.length > 2) {
      const newKeywords = keywords.filter((_, i) => i !== index)
      setKeywords(newKeywords)
    }
  }

  // 生成推送
  const handleGenerate = async () => {
    const validKeywords = keywords.filter(k => k.trim())
    
    if (validKeywords.length < 2) {
      setError('请至少输入2个关键词')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await digestApi.createDigest({
        keywords: validKeywords,
        per_keyword: 5,
        min_play: 10000,
        max_videos: 20,
        sort_by: 'score'
      })
      setResult(data)
    } catch (e: any) {
      const message = e.response?.data?.message || e.message || '生成失败'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  // 复制Markdown
  const copyToClipboard = async () => {
    if (!result) return
    
    try {
      await navigator.clipboard.writeText(result.markdown)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('复制失败:', err)
    }
  }

  // 下载Markdown文件
  const downloadMarkdown = () => {
    if (!result) return
    
    const blob = new Blob([result.markdown], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `B站视频推送_${result.keywords.join('_')}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="container mx-auto max-w-5xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-primary" />
          综合视频推送
        </h1>
        <p className="text-muted-foreground">
          输入2-3个关键词，自动检索并生成Markdown格式的优秀视频推送
        </p>
      </div>

      {/* 输入区域 */}
      <div className="bg-card rounded-xl border border-border p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">搜索关键词</h2>
        
        <div className="space-y-3">
          {keywords.map((keyword, index) => (
            <div key={index} className="flex gap-2">
              <Input
                placeholder={`关键词 ${index + 1}`}
                value={keyword}
                onChange={(e) => handleKeywordChange(index, e.target.value)}
                className="flex-1"
              />
              {keywords.length > 2 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => removeKeyword(index)}
                  className="px-3"
                >
                  删除
                </Button>
              )}
            </div>
          ))}
          
          {keywords.length < 5 && (
            <Button
              variant="outline"
              onClick={addKeyword}
              className="w-full"
            >
              + 添加关键词（最多5个）
            </Button>
          )}
        </div>

        <div className="mt-6 flex gap-3">
          <Button
            onClick={handleGenerate}
            disabled={loading || keywords.filter(k => k.trim()).length < 2}
            className="flex-1"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                正在生成...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                生成推送
              </>
            )}
          </Button>
        </div>

        {error && (
          <div className="mt-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive p-3 text-sm flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}
      </div>

      {/* 结果展示 */}
      {result && (
        <div className="space-y-4">
          {/* 统计信息 */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h2 className="text-lg font-semibold mb-3">📊 统计信息</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">搜索关键词：</span>
                <div className="font-medium mt-1">{result.keywords.join('、')}</div>
              </div>
              <div>
                <span className="text-muted-foreground">初始搜索：</span>
                <div className="font-medium mt-1">{result.total_found} 个视频</div>
              </div>
              <div>
                <span className="text-muted-foreground">筛选后：</span>
                <div className="font-medium mt-1">{result.after_filter} 个视频</div>
              </div>
              <div>
                <span className="text-muted-foreground">最终推送：</span>
                <div className="font-medium mt-1">{result.final_count} 个视频</div>
              </div>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={copyToClipboard}
              className="flex-1"
            >
              {copied ? (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  已复制
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  复制Markdown
                </>
              )}
            </Button>
            <Button
              onClick={downloadMarkdown}
              className="flex-1"
            >
              <Download className="mr-2 h-4 w-4" />
              下载Markdown
            </Button>
          </div>

          {/* Markdown预览 */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Markdown 预览
            </h2>
            <pre className="bg-muted/30 rounded-lg p-4 text-sm overflow-x-auto max-h-[600px] overflow-y-auto whitespace-pre-wrap">
              {result.markdown}
            </pre>
          </div>

          {/* 视频列表 */}
          <div className="bg-card rounded-xl border border-border p-6">
            <h2 className="text-lg font-semibold mb-3">精选视频列表</h2>
            <div className="space-y-3">
              {result.videos.map((video, index) => (
                <div key={video.bvid} className="flex items-start gap-3 p-3 rounded-lg bg-muted/20 hover:bg-muted/30 transition-colors">
                  <div className="text-muted-foreground font-bold text-lg">#{index + 1}</div>
                  <div className="flex-1 min-w-0">
                    <a
                      href={video.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium hover:text-primary line-clamp-2"
                    >
                      {video.title}
                    </a>
                    <div className="text-sm text-muted-foreground mt-1">
                      UP主: {video.author} | 播放: {video.play_count.toLocaleString()} | 点赞: {video.like_count.toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DigestPage
