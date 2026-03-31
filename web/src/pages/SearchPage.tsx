import React, { useState } from 'react'
import { SearchBar } from '@/components/search/SearchBar'
import { SearchFilters } from '@/components/search/SearchFilters'
import { VideoGrid } from '@/components/video/VideoGrid'
import { LoadMore } from '@/components/video/LoadMore'
import { VideoSummaryDialog } from '@/components/video/VideoSummaryDialog'
import { useSearchStore } from '@/store/searchStore'
import { VideoItem } from '@/types/video'

const SearchPage: React.FC = () => {
  const { videos, loading, error, keyword, hasMore } = useSearchStore()
  const [summaryVideo, setSummaryVideo] = useState<VideoItem | null>(null)

  const handleSummarize = (video: VideoItem) => {
    const videoUrl = video.video_url || video.url ||
      (video.platform === 'bilibili' ? `https://www.bilibili.com/video/${video.bvid}` : '')
    if (videoUrl) {
      setSummaryVideo({ ...video, url: videoUrl })
    }
  }

  return (
    <div className="space-y-6">
      {/* 搜索区域 */}
      <div className="py-4">
        <SearchBar />
      </div>

      {/* 筛选器 */}
      <SearchFilters />

      {/* 结果统计 */}
      {videos.length > 0 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            搜索 "{keyword}" 找到 <span className="text-foreground font-medium">{videos.length}</span> 个视频
            {hasMore && ' (还有更多)'}
          </span>
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-center">
          {error}
        </div>
      )}

      {/* 视频网格 */}
      <VideoGrid videos={videos} loading={loading} onSummarize={handleSummarize} />

      {/* 加载更多 */}
      <LoadMore />

      {/* AI 总结弹窗 */}
      <VideoSummaryDialog
        url={summaryVideo?.url || ''}
        title={summaryVideo?.title || ''}
        open={!!summaryVideo}
        onClose={() => setSummaryVideo(null)}
      />
    </div>
  )
}

export default SearchPage
