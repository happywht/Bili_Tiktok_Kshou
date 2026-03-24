// 格式化数字（如播放量）
export function formatCount(count: number): string {
  if (count >= 100000000) {
    return (count / 100000000).toFixed(1) + '亿'
  }
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count.toString()
}

// 格式化时长（支持多种格式）
export function formatDuration(duration: string | number | undefined): string {
  if (!duration) return ''

  // 如果是数字，当作秒数处理
  if (typeof duration === 'number') {
    return formatSeconds(duration)
  }

  // 如果是字符串
  if (typeof duration === 'string') {
    // 尝试解析为数字（可能是秒数的字符串形式）
    const num = parseInt(duration, 10)
    if (!isNaN(num) && duration.trim() === String(num)) {
      return formatSeconds(num)
    }

    // 可能是毫秒数
    if (num > 100000) {
      return formatSeconds(Math.floor(num / 1000))
    }

    // 已经是格式化的时间字符串（如 "12:34" 或 "1:23:45"）
    if (/^\d+:\d+(:\d+)?$/.test(duration)) {
      return duration
    }

    // ISO 8601 duration 格式 (PT1H2M3S)
    if (duration.startsWith('PT')) {
      return formatISO8601Duration(duration)
    }

    // 无法解析，返回原值
    return duration
  }

  return ''
}

// 格式化秒数为 HH:MM:SS 或 MM:SS
function formatSeconds(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return ''

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// 解析 ISO 8601 duration (PT1H2M3S)
function formatISO8601Duration(duration: string): string {
  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/)
  if (!match) return duration

  const hours = match[1] ? parseInt(match[1], 10) : 0
  const minutes = match[2] ? parseInt(match[2], 10) : 0
  const seconds = match[3] ? parseInt(match[3], 10) : 0

  const totalSeconds = hours * 3600 + minutes * 60 + seconds
  return formatSeconds(totalSeconds)
}

// 格式化日期（支持多种格式）
export function formatDate(timestamp: string | number | undefined): string {
  if (!timestamp) return ''

  let date: Date

  if (typeof timestamp === 'number') {
    // 判断是秒还是毫秒（毫秒时间戳通常大于这个值）
    const ms = timestamp > 9999999999 ? timestamp : timestamp * 1000
    date = new Date(ms)
  } else if (typeof timestamp === 'string') {
    // 尝试解析字符串
    // 可能是时间戳字符串
    const num = parseInt(timestamp, 10)
    if (!isNaN(num) && timestamp.trim() === String(num)) {
      const ms = num > 9999999999 ? num : num * 1000
      date = new Date(ms)
    } else {
      // ISO 日期字符串或其他格式
      date = new Date(timestamp)
    }
  } else {
    return ''
  }

  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    return ''
  }

  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 如果是未来时间或负数，显示具体日期
  if (diff < 0) {
    return formatAbsoluteDate(date)
  }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes <= 1 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  }
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  if (days < 365) return `${Math.floor(days / 30)}个月前`

  const years = Math.floor(days / 365)
  if (years < 3) return `${years}年前`

  // 超过3年显示具体日期
  return formatAbsoluteDate(date)
}

// 格式化绝对日期
function formatAbsoluteDate(date: Date): string {
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 高亮关键词
export function highlightKeyword(text: string, keyword: string): string {
  if (!keyword) return text
  const regex = new RegExp(`(${keyword})`, 'gi')
  return text.replace(regex, '<mark class="bg-primary/30 text-foreground px-0.5 rounded">$1</mark>')
}
