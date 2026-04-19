<script setup lang="ts">
import { inject, onMounted, onUnmounted, ref, watch, computed } from 'vue'
import { RouterLink } from 'vue-router'
import maplibregl from 'maplibre-gl'
import { Protocol } from 'pmtiles'
import * as protomaps from 'protomaps-themes-base'
import { StatusKey } from '@/composables/useStatus'
import 'maplibre-gl/dist/maplibre-gl.css'

const { status } = inject(StatusKey)!

const mapContainer = ref<HTMLElement | null>(null)
const selectedMap = ref<string | null>(null)
let map: maplibregl.Map | null = null

const availableMaps = computed(() => status.value?.maps ?? [])

const displayName = (filename: string) =>
  filename.replace('.pmtiles', '').replace(/_\d{4}-\d{2}$/, '').replace(/_/g, ' ')

function buildStyle(filename: string): maplibregl.StyleSpecification {
  const url = `pmtiles://${window.location.origin}/maps/${filename}`
  return {
    version: 8,
    glyphs: 'https://cdn.protomaps.com/fonts/pbf/{fontstack}/{range}.pbf',
    sprite: 'https://cdn.protomaps.com/sprites/v4/light',
    sources: {
      protomaps: {
        type: 'vector',
        url,
        attribution: '© <a href="https://openstreetmap.org" target="_blank">OpenStreetMap</a>',
      },
    },
    layers: protomaps.layers('protomaps', protomaps.namedTheme('light'), { lang: 'en' }) as maplibregl.LayerSpecification[],
  }
}

function initMap(filename: string) {
  map?.remove()
  map = null
  if (!mapContainer.value) return

  map = new maplibregl.Map({
    container: mapContainer.value,
    style: buildStyle(filename),
    center: [0, 20],
    zoom: 2,
    attributionControl: false,
  })

  map.addControl(new maplibregl.NavigationControl(), 'top-right')
  map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left')
  map.addControl(new maplibregl.FullscreenControl(), 'top-right')
}

watch(selectedMap, (filename) => {
  if (filename) initMap(filename)
})

watch(
  availableMaps,
  (maps) => {
    if (maps.length && !selectedMap.value) selectedMap.value = maps[0] ?? null
  },
  { immediate: true },
)

onMounted(() => {
  const protocol = new Protocol()
  maplibregl.addProtocol('pmtiles', protocol.tile)
})

onUnmounted(() => {
  map?.remove()
  map = null
  maplibregl.removeProtocol('pmtiles')
})
</script>

<template>
  <!-- No maps installed -->
  <div class="empty-state" v-if="!status || availableMaps.length === 0">
    <div class="empty-icon">🗺️</div>
    <h2>No maps installed</h2>
    <p>Download a map region from the Library to start exploring offline.</p>
    <RouterLink to="/library" class="btn-primary">Go to Library</RouterLink>
  </div>

  <!-- Map viewer -->
  <div class="map-page" v-else>
    <div class="map-toolbar">
      <select v-model="selectedMap" class="map-select">
        <option v-for="m in availableMaps" :key="m" :value="m">
          {{ displayName(m) }}
        </option>
      </select>
    </div>
    <div ref="mapContainer" class="map-container" />
  </div>
</template>

<style scoped>
/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 0.75rem;
  text-align: center;
  color: var(--muted);
}

.empty-icon { font-size: 3rem; }

.empty-state h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
}

.empty-state p { font-size: 0.875rem; }

.btn-primary {
  margin-top: 0.5rem;
  padding: 0.5rem 1.25rem;
  background: var(--blue);
  border-radius: 8px;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  transition: opacity 0.15s;
}

.btn-primary:hover { opacity: 0.85; }

/* Map layout — break out of .container padding */
.map-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 57px); /* subtract header height */
  margin: -1.25rem; /* undo container padding */
}

.map-toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  z-index: 10;
}

.map-select {
  padding: 0.35rem 0.625rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 0.8rem;
  cursor: pointer;
}

.map-container {
  flex: 1;
}

/* Override MapLibre attribution to match dark theme */
:deep(.maplibregl-ctrl-attrib) {
  background: rgba(10, 15, 30, 0.75) !important;
  color: var(--muted) !important;
}

:deep(.maplibregl-ctrl-attrib a) {
  color: var(--blue) !important;
}
</style>
