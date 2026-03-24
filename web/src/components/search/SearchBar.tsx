import React, { useState, useCallback } from 'react'
import { Search, Loader2 } from 'lucide-react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useSearchStore } from '@/store/searchStore'

export const SearchBar: React.FC = () => {
  const [inputValue, setInputValue] = useState('')
  const { keyword, loading, search } = useSearchStore()

  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      search({ keyword: inputValue.trim() })
    }
  }, [inputValue, search])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch(e)
    }
  }

  return (
    <form onSubmit={handleSearch} className="w-full max-w-3xl mx-auto">
      <div className="relative flex items-center">
        <Search className="absolute left-4 h-5 w-5 text-muted-foreground pointer-events-none" />
        <Input
          type="search"
          placeholder="搜索B站视频、UP主、关键词..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          className="h-12 pl-12 pr-4 text-base bg-secondary/50 border-border/50
                     focus:border-primary focus:ring-primary/20
                     rounded-xl transition-all duration-200"
        />
        <Button
          type="submit"
          disabled={loading || !inputValue.trim()}
          className="absolute right-2 h-8 px-4 rounded-lg bg-primary hover:bg-primary/90"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            '搜索'
          )}
        </Button>
      </div>
    </form>
  )
}
