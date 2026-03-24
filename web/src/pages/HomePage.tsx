import React from 'react'
import { useNavigate } from 'react-router-dom'
import { SearchBar } from '@/components/search/SearchBar'
import { useSearchStore } from '@/store/searchStore'

const HomePage: React.FC = () => {
  const navigate = useNavigate()
  const { keyword } = useSearchStore()

  // 当有搜索关键词时跳转到搜索页
  React.useEffect(() => {
    if (keyword) {
      navigate('/search')
    }
  }, [keyword, navigate])

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh]">
      {/* Hero Section */}
      <div className="text-center mb-12 animate-fade-in">
        <h1 className="text-5xl font-bold mb-4">
          <span className="gradient-text">VideoHub</span>
        </h1>
        <p className="text-xl text-muted-foreground mb-2">
          多平台视频搜索聚合
        </p>
        <p className="text-sm text-muted-foreground">
          一站式搜索 B站、抖音、小红书 等平台视频内容
        </p>
      </div>

      {/* 搜索框 */}
      <div className="w-full max-w-2xl px-4 animate-fade-in" style={{ animationDelay: '100ms' }}>
        <SearchBar />
      </div>

      {/* 热门搜索 */}
      <div className="mt-8 text-center animate-fade-in" style={{ animationDelay: '200ms' }}>
        <p className="text-sm text-muted-foreground mb-3">热门搜索</p>
        <div className="flex flex-wrap justify-center gap-2">
          {['Python教程', '原神', '编程', '美食', '旅行', '音乐'].map((tag) => (
            <button
              key={tag}
              onClick={() => {
                const store = useSearchStore.getState()
                store.setKeyword(tag)
                store.search({ keyword: tag })
              }}
              className="px-4 py-1.5 text-sm rounded-full bg-secondary/50 hover:bg-secondary text-foreground transition-colors"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* 平台图标 */}
      <div className="mt-16 flex items-center gap-8 text-muted-foreground/50 animate-fade-in" style={{ animationDelay: '300ms' }}>
        <div className="flex items-center gap-2">
          <span className="text-2xl">📺</span>
          <span className="text-sm">B站</span>
        </div>
        <div className="flex items-center gap-2 opacity-50">
          <span className="text-2xl">🎵</span>
          <span className="text-sm">抖音</span>
          <span className="text-xs bg-muted px-1.5 py-0.5 rounded">即将支持</span>
        </div>
        <div className="flex items-center gap-2 opacity-50">
          <span className="text-2xl">📕</span>
          <span className="text-sm">小红书</span>
          <span className="text-xs bg-muted px-1.5 py-0.5 rounded">即将支持</span>
        </div>
      </div>
    </div>
  )
}

export default HomePage
