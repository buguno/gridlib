<script setup lang="ts">
defineProps<{
  label: string
  value: string
  sub: string
  percent: number
  color: string
}>()
</script>

<template>
  <div class="card">
    <div class="card-label">{{ label }}</div>
    <div class="card-value" :style="{ color }">{{ value }}</div>
    <div class="card-sub">{{ sub }}</div>
    <div class="progress">
      <div class="progress-fill" :style="{ width: percent + '%', background: color }" />
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
}

.card-label {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  margin-bottom: 0.5rem;
}

.card-value {
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.4rem;
}

.card-sub {
  font-size: 0.7rem;
  color: var(--muted);
  margin-bottom: 0.625rem;
}

.progress {
  height: 4px;
  background: var(--surface2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.6s ease;
}
</style>
