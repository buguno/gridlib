export interface SystemStatus {
  cpu_percent: number
  memory: {
    total_mb: number
    used_mb: number
    percent: number
  }
  temperature_c: number | null
  disk: {
    total_gb: number
    used_gb: number
    percent: number
  }
  services: {
    kiwix: {
      active: boolean
      port: number
    }
  }
  zims: string[]
  maps: string[]
}
