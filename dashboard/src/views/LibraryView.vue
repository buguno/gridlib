<script setup lang="ts">
import { inject } from 'vue'
import { LibraryKey } from '@/composables/useLibrary'
import type { CollectionResource } from '@/types/collection'

const { collections, loading, error, install, cancel, uninstall, isInstalled, downloadState } = inject(LibraryKey)!

function formatSize(mb: number): string {
  if (mb >= 1000) return (mb / 1000).toFixed(1) + ' GB'
  return mb + ' MB'
}

function statusLabel(filename: string): string {
  const s = downloadState(filename)
  if (!s) return ''
  if (s.status === 'downloading') return `${s.percent}% — ${formatSize(s.downloaded_mb)} of ${formatSize(s.size_mb)}`
  if (s.status === 'complete') return 'Installed'
  if (s.status === 'error') return `Error: ${s.error}`
  if (s.status === 'cancelled') return 'Cancelled'
  return ''
}

function btnState(resource: CollectionResource, kind: string): 'install' | 'queued' | 'downloading' | 'installed' | 'error' {
  if (isInstalled(resource.filename)) return 'installed'
  const s = downloadState(resource.filename)
  if (!s) return 'install'
  if (s.status === 'queued') return 'queued'
  if (s.status === 'downloading') return 'downloading'
  if (s.status === 'complete') return 'installed'
  if (s.status === 'error') return 'error'
  return 'install'
}

function onInstall(resource: CollectionResource, kind: string) {
  install(resource.url, resource.filename, kind, resource.size_mb, resource.extract)
}
</script>

<template>
  <div class="centered" v-if="loading">
    <div class="spinner" />
    <span>Loading collections…</span>
  </div>

  <div class="centered" v-else-if="error">
    <span>⚠ {{ error }}</span>
  </div>

  <template v-else>
    <div class="collection-block" v-for="col in collections" :key="col.type">
      <div class="col-header">
        <div class="col-title">{{ col.name }}</div>
        <div class="col-desc">{{ col.description }}</div>
      </div>

      <div class="category" v-for="cat in col.categories" :key="cat.slug">
        <div class="cat-title">
          <span>{{ cat.icon }}</span>
          {{ cat.name }}
        </div>

        <div class="resource-list">
          <div class="resource-item" v-for="r in cat.resources" :key="r.id">
            <div class="resource-info">
              <div class="resource-name">
                {{ r.title }}
                <span class="badge recommended" v-if="r.recommended">Recommended</span>
              </div>
              <div class="resource-desc">{{ r.description }}</div>
              <div class="resource-meta">
                {{ formatSize(r.size_mb) }}
                <span v-if="downloadState(r.filename) && downloadState(r.filename)!.status === 'downloading'">
                  · {{ statusLabel(r.filename) }}
                </span>
              </div>

              <!-- Progress bar -->
              <div class="progress" v-if="downloadState(r.filename)?.status === 'downloading'">
                <div
                  class="progress-fill"
                  :style="{ width: downloadState(r.filename)!.percent + '%' }"
                />
              </div>
            </div>

            <!-- Action buttons -->
            <div class="btn-group">
              <button
                v-if="btnState(r, col.type) === 'installed'"
                class="btn-action uninstall"
                @click="uninstall(r.filename, col.type)"
              >
                Uninstall
              </button>
              <button
                v-else
                class="btn-action"
                :class="btnState(r, col.type)"
                @click="['downloading', 'queued'].includes(btnState(r, col.type)) ? cancel(r.filename) : onInstall(r, col.type)"
              >
                <span v-if="btnState(r, col.type) === 'downloading'">✕ Cancel</span>
                <span v-else-if="btnState(r, col.type) === 'queued'">✕ Remove</span>
                <span v-else-if="btnState(r, col.type) === 'error'">Retry</span>
                <span v-else>Install</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
</template>

<style scoped>
.collection-block {
  margin-bottom: 2rem;
}

.col-header {
  margin-bottom: 1rem;
}

.col-title {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.col-desc {
  font-size: 0.78rem;
  color: var(--muted);
  margin-top: 0.2rem;
}

.category {
  margin-bottom: 1.25rem;
}

.cat-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.resource-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-name {
  font-size: 0.875rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.resource-desc {
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 0.2rem;
}

.resource-meta {
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 0.35rem;
}

.badge {
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge.recommended {
  background: rgba(59, 130, 246, 0.15);
  color: var(--blue);
}

.progress {
  height: 3px;
  background: var(--surface2);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--blue);
  border-radius: 2px;
  transition: width 0.5s ease;
}

/* Action button */
.btn-action {
  flex-shrink: 0;
  padding: 0.4rem 0.875rem;
  border-radius: 7px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
  white-space: nowrap;
}

.btn-action.install {
  background: var(--blue);
  color: #fff;
  border-color: var(--blue);
}

.btn-action.install:hover { opacity: 0.85; }

.btn-action.downloading {
  background: transparent;
  border-color: var(--red);
  color: var(--red);
}

.btn-action.downloading:hover { background: rgba(239,68,68,.1); }

.btn-action.queued {
  background: transparent;
  border-color: var(--muted);
  color: var(--muted);
}

.btn-action.queued:hover { background: rgba(255,255,255,.05); }

.btn-action.installed {
  background: rgba(16,185,129,.1);
  border-color: var(--green);
  color: var(--green);
  cursor: default;
}

.btn-action.error {
  background: transparent;
  border-color: var(--orange);
  color: var(--orange);
}

.btn-action.uninstall {
  background: transparent;
  border-color: var(--border);
  color: var(--muted);
}

.btn-action.uninstall:hover {
  border-color: var(--red);
  color: var(--red);
}

.btn-group {
  flex-shrink: 0;
}


/* States */
.centered {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 160px;
  color: var(--muted);
  gap: 0.5rem;
  font-size: 0.875rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border);
  border-top-color: var(--blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
