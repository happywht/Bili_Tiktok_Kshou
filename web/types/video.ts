// 视频数据类型
export interface VideoStats {
  view: number
  like: number
  coin?: number
  favorite?: number
  share?: number
  reply?: number
}

export interface VideoItem {
  bvid: string
  title: string
  description: string
  author: string
  author_id: number
  play_count: number
  like_count: number
  duration: string | number  // 支持秒数或格式化字符串
  pubdate: string | number   // 支持时间戳或日期字符串
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

// 播放量筛选选项
export const PLAY_COUNT_OPTIONS = [
  { value: '', label: '不限' },
  { value: '10000', label: '1万+' },
  { value: '100000', label: '10万+' },
  { value: '500000', label: '50万+' },
  { value: '1000000', label: '100万+' },
]

// 时长筛选选项
export const DURATION_OPTIONS = [
  { value: '', label: '不限' },
  { value: '0-300', label: '0-5分钟' },
  { value: '300-600', label: '5-10分钟' },
  { value: '600-1800', label: '10-30分钟' },
  { value: '1800-', label: '30分钟+' },
]
