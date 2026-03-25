// 视频数据类型（兼容旧接口）
export interface VideoItem {
  bvid?: string
  id?: string
  title: string
  description?: string
  author: string
  author_id?: number | string
  play_count: number
  like_count: number
  comment_count?: number
  share_count?: number
  duration: string
  pubdate?: string
  publish_time?: string
  cover_url: string
  video_url?: string
  url?: string
  tags: string[]
  platform?: string
}

// 通用内容项（新接口）
export interface ContentItem {
  id: string
  title: string
  description: string
  author: string
  author_id: string
  cover_url: string
  url: string
  platform: string
  stats: {
    play_count: number
    like_count: number
    comment_count: number
    share_count: number
    collect_count: number
  }
  tags: string[]
  publish_time: string
  duration: string
  content_type: string
}

export interface SearchParams {
  keyword: string
  page?: number
  page_size?: number
  order?: 'totalrank' | 'click' | 'pubdate' | 'dm'
  platform?: string
  sort_type?: number  // 抖音专用
}

export interface SearchResponse {
  success: boolean
  code: number
  message: string
  platform: string
  data: {
    videos?: VideoItem[]
    items?: ContentItem[]
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

// 抖音排序选项
export const DOUYIN_SORT_OPTIONS: SortOption[] = [
  { value: '0', label: '综合排序' },
  { value: '1', label: '最多点赞' },
  { value: '2', label: '最新发布' },
]
