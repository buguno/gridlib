import { ref, onMounted, onUnmounted } from 'vue'
import type { Collection, DownloadState, ExtractSpec } from '@/types/collection'

export function useLibrary() {
  const collections = ref<Collection[]>([])
  const installed = ref<Record<string, string[]>>({})
  const downloads = ref<Record<string, DownloadState>>({})
  const loading = ref(true)
  const error = ref<string | null>(null)

  async function fetchCollections() {
    try {
      const res = await fetch('/api/collections')
      if (!res.ok) throw new Error(res.statusText)
      const data = await res.json()
      collections.value = data.collections
      installed.value = data.installed
      error.value = null
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchDownloads() {
    try {
      const res = await fetch('/api/downloads')
      if (!res.ok) return
      downloads.value = await res.json()
    } catch {
      // silently ignore — dashboard still usable
    }
  }

  async function install(url: string | undefined, filename: string, kind: string, size_mb: number, extract?: ExtractSpec) {
    await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, filename, kind, size_mb, extract }),
    })
    await fetchDownloads()
  }

  async function cancel(filename: string) {
    await fetch('/api/download', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename }),
    })
    await fetchDownloads()
  }

  async function uninstall(filename: string, kind: string) {
    await fetch('/api/file', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, kind }),
    })
    await fetchCollections()
    await fetchDownloads()
  }

  function isInstalled(filename: string): boolean {
    return Object.values(installed.value).flat().includes(filename)
  }

  function downloadState(filename: string): DownloadState | null {
    return downloads.value[filename] ?? null
  }

  let timer: ReturnType<typeof setInterval>
  onMounted(async () => {
    await fetchCollections()
    await fetchDownloads()
    timer = setInterval(fetchDownloads, 2000)
  })
  onUnmounted(() => clearInterval(timer))

  return { collections, installed, downloads, loading, error, install, cancel, uninstall, isInstalled, downloadState }
}
