import React from 'react'
import { useSearchStore } from '@/store/searchStore'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'

export const PlatformSelector: React.FC = () => {
  const { currentPlatform, platforms, setPlatform } = useSearchStore()

  return (
    <div className="flex items-center gap-2">
      {platforms.map((platform) => (
        <button
          key={platform.id}
          onClick={() => platform.status === 'available' && setPlatform(platform.id)}
          disabled={platform.status === 'coming_soon'}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all",
            currentPlatform === platform.id
              ? "bg-primary text-primary-foreground shadow-lg shadow-primary/30"
              : platform.status === 'available'
                ? "bg-secondary/50 text-foreground hover:bg-secondary"
                : "bg-secondary/30 text-muted-foreground cursor-not-allowed opacity-60"
          )}
        >
          <span>{platform.icon}</span>
          <span>{platform.name}</span>
          {platform.status === 'coming_soon' && (
            <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-4 ml-1">
              即将推出
            </Badge>
          )}
        </button>
      ))}
    </div>
  )
}
