import { createLongTimeoutClient } from './client'

export interface SummaryResult {
  platform: string
  url: string
  extraction_method: string
  subtitle_length: number
  subtitle_preview: string
  ai_summary: string
}

const summaryClient = createLongTimeoutClient(120000)

export const summaryApi = {
  summarize: async (url: string): Promise<SummaryResult> => {
    return summaryClient.post('/summarize', null, {
      params: { url },
    })
  },
}
