import React, { useState } from 'react'
import { Play, Heart, Eye, Clock, User, ImageOff, MessageCircle, Share2 } from 'lucide-react'
import { VideoItem } from '@/types/video'
import { formatCount, formatDuration, formatDate } from '@/utils/format'
import { cn } from '@/lib/utils'

interface VideoCardProps {
  video: VideoItem
  index: number
}

// 平台配置
const PLATFORM_CONFIG = {
  bilibili: { name: 'B站', color: 'bg-pink-500', icon: '📺' },
  douyin: { name: '抖音', color: 'bg-black', icon: '🎵' },
  xiaohongshu: { name: '小红书', color: 'bg-red-500', icon: '📕' },
}

// 获取代理后的图片URL（绕过防盗链）
function getProxiedImageUrl(url: string, platform?: string): string {
  if (!url) return ''
  // 如果已经是代理URL，直接返回
  if (url.includes('/proxy-image')) return url
  // 抖音和小红书的 CDN 图片可以直接加载（设置 referrerpolicy）
  // B站图片需要代理
  if (platform === 'douyin' || platform === 'xiaohongshu') return url
  return `/api/v1/proxy-image?url=${encodeURIComponent(url)}`
}

export const VideoCard: React.FC<VideoCardProps> = ({ video, index }) => {
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)

  // 获取平台信息
  const platform = video.platform || 'bilibili'
  const platformConfig = PLATFORM_CONFIG[platform as keyof typeof PLATFORM_CONFIG] || PLATFORM_CONFIG.bilibili

  // 使用video_url或根据平台构建链接
  const videoUrl = video.video_url || video.url ||
    (platform === 'bilibili' ? `https://www.bilibili.com/video/${video.bvid}` :
     platform === 'douyin' ? `https://www.douyin.com/video/${video.id || video.bvid}` : '#')

  // 使用代理后的封面URL
  const rawCoverUrl = video.cover_url || ''
  const coverUrl = rawCoverUrl ? getProxiedImageUrl(rawCoverUrl, platform) : ''
  const showImage = coverUrl && !imageError

  return (
    <a
      href={videoUrl}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        "group cursor-pointer overflow-hidden rounded-xl border border-border/50 bg-card",
        "hover:border-primary/50 hover:shadow-xl hover:shadow-primary/10",
        "transition-all duration-300 animate-fade-in"
      )}
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {/* 封面区 */}
      <div className="relative aspect-video overflow-hidden bg-secondary">
        {/* 封面图片 */}
        {showImage && (
          <>
            {/* 加载骨架 */}
            {imageLoading && (
              <div className="absolute inset-0 bg-muted animate-pulse" />
            )}
            <img
              src={coverUrl}
              alt={video.title}
              referrerPolicy={platform === 'douyin' || platform === 'xiaohongshu' ? 'no-referrer' : undefined}
              className={cn(
                "w-full h-full object-cover group-hover:scale-105 transition-transform duration-500",
                imageLoading && "opacity-0",
                !imageLoading && "opacity-100 transition-opacity duration-300"
              )}
              loading="lazy"
              onLoad={() => setImageLoading(false)}
              onError={() => {
                setImageLoading(false)
                setImageError(true)
              }}
            />
          </>
        )}

        {/* 无封面占位符 */}
        {!showImage && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground/50">
            <ImageOff className="h-12 w-12 mb-2" />
            <span className="text-xs">暂无封面</span>
          </div>
        )}
        {/* 渐变遮罩 */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        {/* 平台标识 */}
        <span className={cn(
          "absolute top-2 left-2 text-white text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1",
          platformConfig.color
        )}>
          <span>{platformConfig.icon}</span>
          <span>{platformConfig.name}</span>
        </span>
        {/* 时长标签 */}
        {video.duration && (
          <span className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-0.5 rounded flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {formatDuration(video.duration)}
          </span>
        )}
        {/* 悬停播放按钮 */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="w-14 h-14 rounded-full bg-primary/90 flex items-center justify-center shadow-lg shadow-primary/30">
            <Play className="h-6 w-6 text-white fill-white ml-1" />
          </div>
        </div>
      </div>

      {/* 信息区 */}
      <div className="p-3 space-y-2">
        <h3 className="font-semibold text-sm line-clamp-2 leading-snug group-hover:text-primary transition-colors">
          {video.title}
        </h3>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <User className="h-3 w-3" />
          <span className="truncate">{video.author}</span>
          {video.pubdate && (
            <>
              <span>·</span>
              <span>{formatDate(video.pubdate)}</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
          <span className="flex items-center gap-1">
            <Eye className="h-3 w-3" />
            {formatCount(video.play_count || 0)}
          </span>
          <span className="flex items-center gap-1">
            <Heart className="h-3 w-3 text-pink-500" />
            {formatCount(video.like_count || 0)}
          </span>
          {video.comment_count !== undefined && video.comment_count > 0 && (
            <span className="flex items-center gap-1">
              <MessageCircle className="h-3 w-3" />
              {formatCount(video.comment_count)}
            </span>
          )}
          {video.share_count !== undefined && video.share_count > 0 && (
            <span className="flex items-center gap-1">
              <Share2 className="h-3 w-3" />
              {formatCount(video.share_count)}
            </span>
          )}
        </div>

        {/* 标签 */}
        {video.tags && video.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {video.tags.slice(0, 3).map((tag, i) => (
              <span
                key={i}
                className="text-[10px] px-1.5 py-0.5 rounded-full bg-secondary text-muted-foreground"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </a>
  )
}
