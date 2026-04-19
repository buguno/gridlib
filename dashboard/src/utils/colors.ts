export function metricColor(pct: number): string {
  if (pct > 85) return 'var(--red)'
  if (pct > 65) return 'var(--orange)'
  return 'var(--green)'
}

export function tempColor(c: number): string {
  if (c > 75) return 'var(--red)'
  if (c > 60) return 'var(--orange)'
  return 'var(--green)'
}

export function tempPercent(c: number): number {
  return Math.min(Math.round((c / 85) * 100), 100)
}

export function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}
