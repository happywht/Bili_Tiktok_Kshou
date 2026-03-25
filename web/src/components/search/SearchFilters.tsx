import React from 'react'
import { SlidersHorizontal, RotateCcw } from 'lucide-react'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { useSearchStore } from '@/store/searchStore'
import { SORT_OPTIONS, DOUYIN_SORT_OPTIONS } from '@/types/video'

export const SearchFilters: React.FC = () => {
  const { sortBy, setSortBy, videos, reset, currentPlatform } = useSearchStore()

  if (videos.length === 0) return null

  // 根据平台选择排序选项
  const sortOptions = currentPlatform === 'douyin' ? DOUYIN_SORT_OPTIONS : SORT_OPTIONS

  return (
    <div className="flex flex-wrap items-center gap-3 p-4 bg-secondary/30
                    rounded-lg border border-border/50">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <SlidersHorizontal className="h-4 w-4" />
        <span>筛选</span>
      </div>

      {/* 排序选择器 */}
      <Select
        value={sortBy}
        onChange={(e) => setSortBy(e.target.value)}
        options={sortOptions}
        className="w-32"
      />

      {/* 分隔线 */}
      <div className="h-6 w-px bg-border hidden sm:block" />

      {/* 重置按钮 */}
      <Button
        variant="ghost"
        size="sm"
        onClick={reset}
        className="h-9"
      >
        <RotateCcw className="h-4 w-4 mr-1" />
        重置
      </Button>
    </div>
  )
}
