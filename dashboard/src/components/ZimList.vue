<script setup lang="ts">
defineProps<{
  zims: string[]
}>()
</script>

<template>
  <div class="zim-list">
    <div class="zim-item" v-for="zim in zims" :key="zim">
      <span class="zim-icon">📚</span>
      <span class="zim-name">{{ zim }}</span>
    </div>
    <div class="empty" v-if="zims.length === 0">
      No ZIM files installed — run setup to download content.
    </div>
  </div>
</template>

<style scoped>
.zim-list {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.zim-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 1rem;
  border-bottom: 1px solid var(--border);
}

.zim-item:last-child {
  border-bottom: none;
}

.zim-name {
  font-size: 0.78rem;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  color: var(--muted);
  word-break: break-all;
}

.empty {
  padding: 1.5rem 1rem;
  text-align: center;
  font-size: 0.8rem;
  color: var(--muted);
}
</style>
