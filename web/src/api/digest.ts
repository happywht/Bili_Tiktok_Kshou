import apiClient from './client'

export interface DigestResult {
  keywords: string[]
  total_found: number
  after_filter: number
  final_count: number
  markdown: string
  videos: Array<{
    bvid: string
    title: string
    author: string
    play_count: number
    like_count: number
    url: string
  }>
}

export interface DigestParams {
  keywords: string[]
  per_keyword?: number
  min_play?: number
  min_like?: number
  max_videos?: number
  sort_by?: 'score' | 'play' | 'like'
}

export const digestApi = {
  // 创建综合视频推送
  createDigest: async (params: DigestParams): Promise<DigestResult> => {
    // 构建查询参数
    const queryParts: string[] = []
    
    // 添加关键词（多个值）
    params.keywords.forEach(keyword => {
      queryParts.push(`keywords=${encodeURIComponent(keyword)}`)
    })
    
    // 添加可选参数
    if (params.per_keyword) queryParts.push(`per_keyword=${params.per_keyword}`)
    if (params.min_play !== undefined) queryParts.push(`min_play=${params.min_play}`)
    if (params.min_like !== undefined) queryParts.push(`min_like=${params.min_like}`)
    if (params.max_videos) queryParts.push(`max_videos=${params.max_videos}`)
    if (params.sort_by) queryParts.push(`sort_by=${params.sort_by}`)
    
    const queryString = queryParts.join('&')
    const url = queryString ? `/digest?${queryString}` : '/digest'
    
    const response = await apiClient.post(url)
    return response.data
  },
}
