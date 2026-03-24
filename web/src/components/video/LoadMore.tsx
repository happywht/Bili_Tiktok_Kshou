import React from 'react'
import { Button } from '@/components/ui/Button'
import { Loader2 } from 'lucide-react'
import { useSearchStore } from '@/store/searchStore'

export const LoadMore: React.FC = () => {
  const { videos, hasMore, loading, loadMore } = useSearchStore()

  if (videos.length === 0 || !hasMore) return null

  return (
    <div className="flex justify-center py-8">
      <Button
        variant="outline"
        onClick={loadMore}
        disabled={loading}
        className="min-w-[120px]"
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            加载中...
          </>
        ) : (
          '加载更多'
        )}
      </Button>
    </div>
  )
}
