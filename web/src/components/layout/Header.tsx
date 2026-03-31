import React from 'react'
import { Search, Sparkles, Home, FileText } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { PlatformSelector } from './PlatformSelector'
import { cn } from '@/lib/utils'

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo + 导航 */}
        <div className="flex items-center gap-6">
          <a href="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30 group-hover:shadow-purple-500/50 transition-shadow">
              <Search className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text hidden sm:inline">
              VideoHub
            </span>
          </a>

          {/* 导航菜单 */}
          <nav className="hidden md:flex items-center gap-4">
            <NavLink
              to="/"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 text-sm font-medium transition-colors hover:text-foreground',
                  isActive ? 'text-foreground' : 'text-muted-foreground'
                )
              }
            >
              <Home className="h-4 w-4" />
              首页
            </NavLink>
            <NavLink
              to="/search"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 text-sm font-medium transition-colors hover:text-foreground',
                  isActive ? 'text-foreground' : 'text-muted-foreground'
                )
              }
            >
              <Search className="h-4 w-4" />
              视频搜索
            </NavLink>
            <NavLink
              to="/digest"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 text-sm font-medium transition-colors hover:text-foreground',
                  isActive ? 'text-foreground' : 'text-muted-foreground'
                )
              }
            >
              <FileText className="h-4 w-4" />
              视频推送
            </NavLink>
            <NavLink
              to="/summarize"
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 text-sm font-medium transition-colors hover:text-foreground',
                  isActive ? 'text-foreground' : 'text-muted-foreground'
                )
              }
            >
              <Sparkles className="h-4 w-4" />
              AI 总结
            </NavLink>
          </nav>
        </div>

        {/* 平台选择器 */}
        <PlatformSelector />
      </div>
    </header>
  )
}
