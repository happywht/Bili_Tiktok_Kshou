// 视频数据类型
export interface VideoItem {
  bvid: string
  title: string
  description?: string
  author: string
  author_id?: number
  play_count: number
  like_count: number
  duration: string
  pubdate: string
  cover_url: string
  video_url: string
  tags: string[]
}

export interface SearchParams {
  keyword: string
  page?: number
  page_size?: number
  order?: 'totalrank' | 'click' | 'pubdate' | 'dm'
  platform?: string
}

export interface SearchResponse {
  success: boolean
  code: number
  message: string
  platform: string
  data: {
    videos: VideoItem[]
  }
  pagination: {
    page: number
    page_size: number
    total?: number
    has_more: boolean
  }
}

// 平台类型
export type Platform = 'bilibili' | 'douyin' | 'xiaohongshu'

export interface PlatformConfig {
  id: Platform
  name: string
  icon: string
  status: 'available' | 'coming_soon'
  features: string[]
}

// 排序选项
export interface SortOption {
  value: string
  label: string
}

export const SORT_OPTIONS: SortOption[] = [
  { value: 'totalrank', label: '综合排序' },
  { value: 'click', label: '播放量' },
  { value: 'pubdate', label: '发布时间' },
  { value: 'dm', label: '弹幕数' },
]
