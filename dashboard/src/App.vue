<script setup lang="ts">
import { provide } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useStatus, StatusKey } from '@/composables/useStatus'
import { formatTime } from '@/utils/colors'

const statusData = useStatus()
provide(StatusKey, statusData)

const { error, lastUpdate } = statusData
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="logo">
        <div class="logo-mark">GL</div>
        <div class="logo-text">
          <h1>GridLib</h1>
          <p>Offline Knowledge Hub</p>
        </div>
      </div>

      <nav class="nav">
        <RouterLink to="/" class="nav-link">Dashboard</RouterLink>
        <RouterLink to="/library" class="nav-link">Library</RouterLink>
        <RouterLink to="/maps" class="nav-link">Maps</RouterLink>
        <RouterLink to="/setup" class="nav-link">Setup</RouterLink>
      </nav>

      <div class="header-right">
        <span class="live-badge" :class="error ? 'error' : 'ok'">
          <span class="live-dot" />
          {{ error ? 'Error' : 'Live' }}
        </span>
        <span class="update-time" v-if="lastUpdate">{{ formatTime(lastUpdate) }}</span>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.5rem;
  border-bottom: 1px solid var(--border);
  gap: 1rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-mark {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--blue), var(--purple));
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 800;
  color: #fff;
  flex-shrink: 0;
}

.logo-text h1 {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.logo-text p {
  font-size: 0.68rem;
  color: var(--muted);
}

.nav {
  display: flex;
  gap: 0.25rem;
}

.nav-link {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--muted);
  transition: all 0.15s;
}

.nav-link:hover {
  color: var(--text);
  background: var(--surface2);
}

.nav-link.router-link-active {
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border);
}

.header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  flex-shrink: 0;
}

.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.live-badge.ok    { background: rgba(16, 185, 129, 0.15); color: var(--green); }
.live-badge.error { background: rgba(239, 68, 68, 0.15);  color: var(--red);   }

.live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.live-badge.ok .live-dot {
  animation: blink 2s infinite;
}

.update-time {
  font-size: 0.68rem;
  color: var(--muted);
}

.main {
  flex: 1;
}

.container {
  max-width: 960px;
  margin: 0 auto;
  padding: 1.25rem;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.25; }
}
</style>
