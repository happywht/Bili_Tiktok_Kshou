import apiClient from './client'
import { SearchParams, SearchResponse } from '@/types/video'

export const searchApi = {
  // 搜索视频
  search: async (params: SearchParams): Promise<SearchResponse> => {
    return apiClient.get('/search', { params })
  },

  // 获取平台列表
  getPlatforms: async () => {
    return apiClient.get('/platforms')
  },
}
