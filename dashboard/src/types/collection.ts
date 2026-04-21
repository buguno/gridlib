export interface ExtractSpec {
  source: string
  bbox: string
  cmd: string
}

export interface CollectionResource {
  id: string
  version: string
  title: string
  description: string
  url?: string
  filename: string
  size_mb: number
  recommended: boolean
  extract?: ExtractSpec
}

export interface CollectionCategory {
  name: string
  slug: string
  icon: string
  description: string
  resources: CollectionResource[]
}

export interface Collection {
  spec_version: string
  type: 'kiwix' | 'maps'
  name: string
  description: string
  dest_dir: string
  categories: CollectionCategory[]
}

export interface DownloadState {
  status: 'queued' | 'downloading' | 'complete' | 'error' | 'cancelled' | 'pending'
  percent: number
  size_mb: number
  downloaded_mb: number
  kind: string
  error?: string
}
