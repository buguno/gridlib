<script setup lang="ts">
import { provide, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useStatus, StatusKey } from '@/composables/useStatus'
import { useLibrary, LibraryKey } from '@/composables/useLibrary'
import { formatTime } from '@/utils/colors'

const statusData = useStatus()
provide(StatusKey, statusData)

const libraryData = useLibrary()
provide(LibraryKey, libraryData)

const { error, lastUpdate } = statusData

const collapsed = ref(localStorage.getItem('sidebar') === 'collapsed')
function toggle() {
  collapsed.value = !collapsed.value
  localStorage.setItem('sidebar', collapsed.value ? 'collapsed' : 'expanded')
}
</script>

<template>
  <div class="layout" :class="{ collapsed }">

    <aside class="sidebar">
      <!-- Brand -->
      <div class="sidebar-brand">
        <div class="logo-mark">GL</div>
        <Transition name="fade">
          <div class="logo-text" v-if="!collapsed">
            <span class="logo-name">GridLib</span>
            <span class="logo-sub">Offline Knowledge Hub</span>
          </div>
        </Transition>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        <RouterLink to="/" class="nav-item" exact-active-class="active">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
            <rect x="3" y="3" width="7" height="7" rx="1.5"/>
            <rect x="14" y="3" width="7" height="7" rx="1.5"/>
            <rect x="3" y="14" width="7" height="7" rx="1.5"/>
            <rect x="14" y="14" width="7" height="7" rx="1.5"/>
          </svg>
          <Transition name="fade"><span v-if="!collapsed">Dashboard</span></Transition>
        </RouterLink>

        <RouterLink to="/library" class="nav-item" active-class="active">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
            <path d="M4 19V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v13"/>
            <path d="M4 19a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2"/>
            <line x1="9" y1="9" x2="15" y2="9"/>
            <line x1="9" y1="13" x2="15" y2="13"/>
          </svg>
          <Transition name="fade"><span v-if="!collapsed">Library</span></Transition>
        </RouterLink>

        <RouterLink to="/setup" class="nav-item" active-class="active">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/>
            <path d="M12 2v2m0 16v2M2 12h2m16 0h2"/>
          </svg>
          <Transition name="fade"><span v-if="!collapsed">Setup</span></Transition>
        </RouterLink>
      </nav>

      <!-- Bottom: status + toggle -->
      <div class="sidebar-bottom">
        <div class="live-row">
          <span class="live-dot-wrap" :class="error ? 'error' : 'ok'">
            <span class="live-dot" />
          </span>
          <Transition name="fade">
            <div class="live-info" v-if="!collapsed">
              <span class="live-label">{{ error ? 'Error' : 'Live' }}</span>
              <span class="live-time" v-if="lastUpdate">{{ formatTime(lastUpdate) }}</span>
            </div>
          </Transition>
        </div>

        <button class="toggle-btn" @click="toggle" :title="collapsed ? 'Expand' : 'Collapse'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               :style="{ transform: collapsed ? 'rotate(180deg)' : 'none' }">
            <path d="M15 18l-6-6 6-6"/>
          </svg>
        </button>
      </div>
    </aside>

    <main class="main">
      <div class="container">
        <RouterView />
      </div>
    </main>

  </div>
</template>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ─────────────────────────────────────────────── */
.sidebar {
  width: 220px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border);
  background: var(--surface);
  transition: width 0.22s ease;
  overflow: hidden;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
}

.layout.collapsed .sidebar {
  width: 56px;
}

/* Brand */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.125rem 0.875rem;
  border-bottom: 1px solid var(--border);
  min-height: 64px;
  white-space: nowrap;
}

.logo-mark {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, var(--blue), var(--purple));
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 800;
  color: #fff;
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.logo-name {
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
}

.logo-sub {
  font-size: 0.62rem;
  color: var(--muted);
}

/* Nav */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.75rem 0.5rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.625rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--muted);
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
  text-decoration: none;
}

.nav-item svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-item:hover {
  background: var(--surface2);
  color: var(--text);
}

.nav-item.active {
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border);
}

/* Bottom */
.sidebar-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0.625rem;
  border-top: 1px solid var(--border);
  gap: 0.5rem;
  min-height: 52px;
}

.collapsed .sidebar-bottom {
  flex-direction: column;
  justify-content: center;
  gap: 0.625rem;
}

.live-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  flex: 1;
}

.collapsed .live-row {
  flex: unset;
  justify-content: center;
}

.live-dot-wrap {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.live-dot-wrap.ok  { color: var(--green); }
.live-dot-wrap.error { color: var(--red); }

.live-dot-wrap.ok .live-dot {
  animation: blink 2s infinite;
}

.live-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  white-space: nowrap;
  min-width: 0;
  overflow: hidden;
}

.live-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
}

.live-time {
  font-size: 0.65rem;
  color: var(--muted);
  opacity: 0.7;
}

.toggle-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.toggle-btn svg {
  width: 14px;
  height: 14px;
  transition: transform 0.22s ease;
}

.toggle-btn:hover {
  background: var(--surface2);
  color: var(--text);
}

/* Main */
.main {
  flex: 1;
  min-width: 0;
  overflow: auto;
}

.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.25; }
}
</style>
