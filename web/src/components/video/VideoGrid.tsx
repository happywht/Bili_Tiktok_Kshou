import React from 'react'
import { VideoCard } from './VideoCard'
import { VideoItem } from '@/types/video'
import { Skeleton } from '@/components/ui/Skeleton'

interface VideoGridProps {
  videos: VideoItem[]
  loading: boolean
}

const VideoSkeleton: React.FC = () => (
  <div className="rounded-xl border border-border/50 overflow-hidden">
    <Skeleton className="aspect-video" />
    <div className="p-3 space-y-2">
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-3 w-2/3" />
      <Skeleton className="h-3 w-1/2" />
    </div>
  </div>
)

export const VideoGrid: React.FC<VideoGridProps> = ({ videos, loading }) => {
  // 首次加载骨架屏
  if (loading && videos.length === 0) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <VideoSkeleton key={i} />
        ))}
      </div>
    )
  }

  // 空状态
  if (!loading && videos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <div className="text-6xl mb-4">🔍</div>
        <p className="text-lg">暂无搜索结果</p>
        <p className="text-sm mt-2">尝试更换关键词或筛选条件</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
      {videos.map((video, index) => (
        <VideoCard key={video.bvid} video={video} index={index} />
      ))}
      {/* 加载更多骨架屏 */}
      {loading && videos.length > 0 && (
        <>
          {Array.from({ length: 4 }).map((_, i) => (
            <VideoSkeleton key={`loading-${i}`} />
          ))}
        </>
      )}
    </div>
  )
}
