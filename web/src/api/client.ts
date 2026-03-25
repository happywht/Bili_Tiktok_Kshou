import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.message || error.message || '网络请求失败'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

// 创建长超时客户端（抖音/小红书浏览器自动化需要）
export function createLongTimeoutClient(timeout = 180000) {
  const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api/v1',
    timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  client.interceptors.request.use(
    (config) => config,
    (error) => Promise.reject(error)
  )

  client.interceptors.response.use(
    (response) => response.data,
    (error) => {
      const message = error.response?.data?.message || error.message || '网络请求失败'
      console.error('API Error:', message)
      return Promise.reject(error)
    }
  )

  return client
}

export default apiClient
