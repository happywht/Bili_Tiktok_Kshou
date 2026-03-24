import React from 'react'
import { Search } from 'lucide-react'
import { PlatformSelector } from './PlatformSelector'

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <a href="/" className="flex items-center gap-2 group">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30 group-hover:shadow-purple-500/50 transition-shadow">
            <Search className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold gradient-text hidden sm:inline">
            VideoHub
          </span>
        </a>

        {/* 平台选择器 */}
        <PlatformSelector />
      </div>
    </header>
  )
}
