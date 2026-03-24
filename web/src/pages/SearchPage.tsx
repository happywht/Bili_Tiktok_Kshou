import React from 'react'
import { SearchBar } from '@/components/search/SearchBar'
import { SearchFilters } from '@/components/search/SearchFilters'
import { VideoGrid } from '@/components/video/VideoGrid'
import { LoadMore } from '@/components/video/LoadMore'
import { useSearchStore } from '@/store/searchStore'

const SearchPage: React.FC = () => {
  const { videos, loading, error, keyword, hasMore } = useSearchStore()

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
      <VideoGrid videos={videos} loading={loading} />

      {/* 加载更多 */}
      <LoadMore />
    </div>
  )
}

export default SearchPage
