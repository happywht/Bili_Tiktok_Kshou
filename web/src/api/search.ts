import apiClient, { createLongTimeoutClient } from './client'
import { SearchParams, SearchResponse } from '@/types/video'

// 抖音/小红书使用更长的超时（浏览器自动化较慢）
const longClient = createLongTimeoutClient()

export const searchApi = {
  // 搜索视频
  search: async (params: SearchParams): Promise<SearchResponse> => {
    const platform = params.platform || 'bilibili'
    // 抖音和小红书基于浏览器自动化，需要更长超时
    const client = (platform === 'douyin' || platform === 'xiaohongshu') ? longClient : apiClient
    return client.get('/search', { params })
  },

  // 获取平台列表
  getPlatforms: async () => {
    return apiClient.get('/platforms')
  },
}
