import { create } from 'zustand'
import { VideoItem, SearchParams, Platform, PlatformConfig, SORT_OPTIONS, ContentItem } from '@/types/video'
import { searchApi } from '@/api/search'

interface SearchState {
  // 搜索状态
  keyword: string
  videos: VideoItem[]
  loading: boolean
  error: string | null

  // 分页
  currentPage: number
  hasMore: boolean

  // 筛选
  sortBy: string

  // 平台
  currentPlatform: Platform
  platforms: PlatformConfig[]

  // 操作
  setKeyword: (keyword: string) => void
  setSortBy: (sort: string) => void
  setPlatform: (platform: Platform) => void
  search: (params?: Partial<SearchParams>) => Promise<void>
  loadMore: () => Promise<void>
  reset: () => void
}

const initialState = {
  keyword: '',
  videos: [],
  loading: false,
  error: null,
  currentPage: 1,
  hasMore: false,
  sortBy: SORT_OPTIONS[0].value,
  currentPlatform: 'bilibili' as Platform,
  platforms: [
    { id: 'bilibili', name: 'B站', icon: '📺', status: 'available', features: ['search', 'detail', 'summary'] },
  ],
}

export const useSearchStore = create<SearchState>((set, get) => ({
  ...initialState,

  setKeyword: (keyword) => set({ keyword }),

  setSortBy: (sortBy) => {
    set({ sortBy, currentPage: 1, videos: [] })
    get().search()
  },

  setPlatform: (platform) => {
    const { currentPlatform, keyword } = get()
    if (platform !== currentPlatform) {
      set({
        currentPlatform: platform,
        currentPage: 1,
        videos: [],
        error: null
      })
      if (keyword) {
        get().search()
      }
    }
  },

  search: async (params) => {
    const state = get()
    const keyword = params?.keyword ?? state.keyword

    if (!keyword.trim()) {
      set({ videos: [], error: null })
      return
    }

    set({ loading: true, error: null, keyword })

    try {
      const response = await searchApi.search({
        keyword,
        page: params?.page ?? 1,
        page_size: 20,
        order: params?.order ?? state.sortBy as any,
        platform: state.currentPlatform,
      })

      if (response.success) {
        // 处理不同平台的响应格式
        let newVideos: VideoItem[] = []

        if (response.data.videos) {
          // B站格式
          newVideos = response.data.videos
        } else if (response.data.items) {
          // 通用内容格式（抖音、小红书等）
          newVideos = response.data.items.map((item: ContentItem) => ({
            bvid: item.id,
            title: item.title,
            description: item.description,
            author: item.author,
            author_id: item.author_id,
            play_count: item.stats.play_count,
            like_count: item.stats.like_count,
            comment_count: item.stats.comment_count,
            share_count: item.stats.share_count,
            duration: item.duration,
            pubdate: item.publish_time,
            cover_url: item.cover_url,
            video_url: item.url,
            tags: item.tags,
            platform: item.platform,
          }))
        }

        set({
          videos: params?.page && params.page > 1 ? [...state.videos, ...newVideos] : newVideos,
          currentPage: response.pagination.page,
          hasMore: response.pagination.has_more,
          loading: false,
        })
      } else {
        set({ error: response.message, loading: false })
      }
    } catch (error: any) {
      const message = error.response?.data?.message || error.message || '搜索失败'
      set({ error: message, loading: false })
    }
  },

  loadMore: async () => {
    const { hasMore, loading, currentPage } = get()
    if (!hasMore || loading) return

    await get().search({ page: currentPage + 1 })
  },

  reset: () => set(initialState),
}))
