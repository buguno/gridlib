<script setup lang="ts">
import { inject, computed } from 'vue'
import { StatusKey } from '@/composables/useStatus'
import StatCard from '@/components/StatCard.vue'
import ServiceCard from '@/components/ServiceCard.vue'
import ZimList from '@/components/ZimList.vue'
import { metricColor, tempColor, tempPercent } from '@/utils/colors'

const { status, error } = inject(StatusKey)!

const host = window.location.hostname
const kiwixUrl = computed(() => `http://${host}:8080`)

const kiwixDetail = computed(() => {
  if (!status.value) return ''
  const s = status.value.services.kiwix
  const count = status.value.zims.length
  return `${s.active ? 'Running' : 'Stopped'} · Port ${s.port} · ${count} ZIM${count !== 1 ? 's' : ''}`
})
</script>

<template>
  <div class="centered" v-if="!status && !error">
    <div class="spinner" />
    <span>Loading system status…</span>
  </div>

  <div class="centered" v-else-if="error && !status">
    <span>⚠ Cannot load status.json</span>
  </div>

  <template v-else-if="status">
    <section>
      <div class="section-title">System Resources</div>
      <div class="grid-4">
        <StatCard
          label="CPU"
          :value="status.cpu_percent + '%'"
          sub="Utilization"
          :percent="status.cpu_percent"
          :color="metricColor(status.cpu_percent)"
        />
        <StatCard
          label="Memory"
          :value="status.memory.percent + '%'"
          :sub="`${status.memory.used_mb} / ${status.memory.total_mb} MB`"
          :percent="status.memory.percent"
          :color="metricColor(status.memory.percent)"
        />
        <StatCard
          v-if="status.temperature_c !== null"
          label="Temperature"
          :value="status.temperature_c + '°C'"
          sub="SoC"
          :percent="tempPercent(status.temperature_c)"
          :color="tempColor(status.temperature_c)"
        />
        <StatCard
          v-else
          label="Temperature"
          value="N/A"
          sub="SoC"
          :percent="0"
          color="var(--muted)"
        />
        <StatCard
          label="Disk"
          :value="status.disk.percent + '%'"
          :sub="`${status.disk.used_gb} / ${status.disk.total_gb} GB`"
          :percent="status.disk.percent"
          :color="metricColor(status.disk.percent)"
        />
      </div>
    </section>

    <section>
      <div class="section-title">Services</div>
      <ServiceCard
        name="Kiwix"
        :active="status.services.kiwix.active"
        :detail="kiwixDetail"
        :href="kiwixUrl"
      />
    </section>

    <section>
      <div class="section-title">ZIM Library ({{ status.zims.length }})</div>
      <ZimList :zims="status.zims" />
    </section>
  </template>
</template>

<style scoped>
section {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: var(--muted);
  margin-bottom: 0.625rem;
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

@media (max-width: 640px) {
  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}

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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
