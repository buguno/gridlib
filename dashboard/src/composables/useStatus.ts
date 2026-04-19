import { ref, onMounted, onUnmounted, type InjectionKey, type Ref } from 'vue'
import type { SystemStatus } from '@/types/status'

export interface StatusData {
  status: Ref<SystemStatus | null>
  error: Ref<string | null>
  lastUpdate: Ref<Date | null>
  fetchStatus: () => Promise<void>
}

export const StatusKey: InjectionKey<StatusData> = Symbol('status')

export function useStatus(interval = 15_000): StatusData {
  const status = ref<SystemStatus | null>(null)
  const error = ref<string | null>(null)
  const lastUpdate = ref<Date | null>(null)

  async function fetchStatus() {
    try {
      const res = await fetch('/status.json?' + Date.now())
      if (!res.ok) throw new Error(res.statusText)
      status.value = await res.json()
      lastUpdate.value = new Date()
      error.value = null
    } catch (e) {
      error.value = (e as Error).message
    }
  }

  let timer: ReturnType<typeof setInterval>
  onMounted(() => {
    fetchStatus()
    timer = setInterval(fetchStatus, interval)
  })
  onUnmounted(() => clearInterval(timer))

  return { status, error, lastUpdate, fetchStatus }
}
