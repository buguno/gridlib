<script setup lang="ts">
defineProps<{
  name: string
  active: boolean
  detail: string
  href?: string
  btnLabel?: string
}>()
</script>

<template>
  <div class="service-card">
    <div class="status-dot" :class="active ? 'active' : 'inactive'" />
    <div class="service-info">
      <div class="service-name">{{ name }}</div>
      <div class="service-detail">{{ detail }}</div>
    </div>
    <a v-if="href && active" :href="href" class="btn" target="_blank">
      {{ btnLabel ?? 'Open' }}
    </a>
  </div>
</template>

<style scoped>
.service-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1.125rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.active {
  background: var(--green);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-dot.inactive {
  background: var(--red);
}

.service-info {
  flex: 1;
  min-width: 0;
}

.service-name {
  font-weight: 600;
  font-size: 0.875rem;
}

.service-detail {
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 0.15rem;
}

.btn {
  flex-shrink: 0;
  padding: 0.35rem 0.75rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  transition: background 0.15s;
  white-space: nowrap;
}

.btn:hover {
  background: var(--border);
}
</style>
