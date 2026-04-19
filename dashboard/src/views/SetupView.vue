<script setup lang="ts">
import { inject, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { StatusKey } from '@/composables/useStatus'
import { metricColor } from '@/utils/colors'

const { status } = inject(StatusKey)!
const router = useRouter()

const step = ref(1)
const TOTAL_STEPS = 4

const RECOMMENDED_ZIMS = [
  {
    name: 'iFixit',
    desc: 'Repair guides for thousands of devices',
    size: '~2 GB',
    url: 'https://download.kiwix.org/zim/ifixit/ifixit_en_all_2025-12.zim',
  },
  {
    name: 'Bitcoin Wiki',
    desc: 'Complete Bitcoin documentation and guides',
    size: '~50 MB',
    url: 'https://download.kiwix.org/zim/other/bitcoin_en_all_maxi_2021-03.zim',
  },
  {
    name: 'Wikipedia (Simple English)',
    desc: 'Simplified Wikipedia, ideal for the Pi',
    size: '~1 GB',
    url: 'https://download.kiwix.org/zim/wikipedia/wikipedia_en_simple_all_mini_2024-06.zim',
  },
]

const checks = computed(() => {
  const s = status.value
  return [
    {
      label: 'Kiwix service installed',
      ok: !!s?.services.kiwix,
    },
    {
      label: 'Content library has ZIM files',
      ok: (s?.zims.length ?? 0) > 0,
    },
    {
      label: `Enough disk space (${s?.disk.total_gb ?? '?'} GB total)`,
      ok: (s?.disk.percent ?? 100) < 90,
    },
    {
      label: `Memory available (${s?.memory.used_mb ?? '?'} / ${s?.memory.total_mb ?? '?'} MB used)`,
      ok: (s?.memory.percent ?? 100) < 85,
    },
  ]
})

const copied = ref<string | null>(null)

function downloadCmd(url: string): string {
  const file = url.split('/').at(-1)
  return `curl -L --continue-at - -o /srv/kiwix/content/${file} \\\n  "${url}"`
}

async function copyCmd(url: string) {
  await navigator.clipboard.writeText(downloadCmd(url))
  copied.value = url
  setTimeout(() => (copied.value = null), 2000)
}

function goToDashboard() {
  router.push('/')
}
</script>

<template>
  <div class="wizard">
    <!-- Progress bar -->
    <div class="progress-track">
      <div class="progress-fill" :style="{ width: (step / TOTAL_STEPS) * 100 + '%' }" />
    </div>
    <div class="step-label">Step {{ step }} of {{ TOTAL_STEPS }}</div>

    <!-- Step 1: Welcome -->
    <div class="step-card" v-if="step === 1">
      <div class="logo-mark">GL</div>
      <h2>Welcome to GridLib</h2>
      <p class="subtitle">Your offline knowledge hub for the Raspberry Pi.<br>Let's get everything configured in a few steps.</p>
      <button class="btn-primary" @click="step++">Get Started →</button>
    </div>

    <!-- Step 2: System Check -->
    <div class="step-card" v-else-if="step === 2">
      <h2>System Check</h2>
      <p class="subtitle">Verifying your Pi is ready.</p>

      <div class="check-list">
        <div
          v-for="c in checks"
          :key="c.label"
          class="check-item"
          :class="c.ok ? 'ok' : 'warn'"
        >
          <span class="check-icon">{{ c.ok ? '✓' : '✗' }}</span>
          <span>{{ c.label }}</span>
        </div>
        <div class="check-item loading" v-if="!status">
          <div class="mini-spinner" />
          <span>Loading system info…</span>
        </div>
      </div>

      <div class="step-actions">
        <button class="btn-secondary" @click="step--">← Back</button>
        <button class="btn-primary" @click="step++">Continue →</button>
      </div>
    </div>

    <!-- Step 3: Content Library -->
    <div class="step-card" v-else-if="step === 3">
      <h2>Content Library</h2>
      <p class="subtitle">Download ZIM files to use Kiwix offline.</p>

      <div class="subsection-title" v-if="status?.zims.length">
        Installed ({{ status.zims.length }})
      </div>
      <div class="installed-zims" v-if="status?.zims.length">
        <div class="zim-chip" v-for="z in status.zims" :key="z">📚 {{ z }}</div>
      </div>

      <div class="subsection-title">Recommended downloads</div>
      <div class="rec-list">
        <div class="rec-item" v-for="r in RECOMMENDED_ZIMS" :key="r.url">
          <div class="rec-info">
            <span class="rec-name">{{ r.name }}</span>
            <span class="rec-desc">{{ r.desc }} · {{ r.size }}</span>
          </div>
          <button
            class="btn-copy"
            :class="{ copied: copied === r.url }"
            @click="copyCmd(r.url)"
          >
            {{ copied === r.url ? '✓ Copied' : 'Copy cmd' }}
          </button>
        </div>
      </div>
      <p class="hint">Paste the command in your Pi terminal to download.</p>

      <div class="step-actions">
        <button class="btn-secondary" @click="step--">← Back</button>
        <button class="btn-primary" @click="step++">Continue →</button>
      </div>
    </div>

    <!-- Step 4: Done -->
    <div class="step-card" v-else-if="step === 4">
      <div class="done-icon">✓</div>
      <h2>You're all set!</h2>
      <p class="subtitle">GridLib is running and ready to use.</p>

      <div class="summary" v-if="status">
        <div class="summary-item">
          <span class="summary-dot" :style="{ background: metricColor(status.cpu_percent) }" />
          CPU at {{ status.cpu_percent }}%
        </div>
        <div class="summary-item">
          <span class="summary-dot" :style="{ background: metricColor(status.memory.percent) }" />
          Memory at {{ status.memory.percent }}%
        </div>
        <div class="summary-item">
          <span class="summary-dot" :style="{ background: status.services.kiwix.active ? 'var(--green)' : 'var(--red)' }" />
          Kiwix {{ status.services.kiwix.active ? 'running' : 'stopped' }}
        </div>
        <div class="summary-item">
          <span class="summary-dot" style="background: var(--blue)" />
          {{ status.zims.length }} ZIM{{ status.zims.length !== 1 ? 's' : '' }} loaded
        </div>
      </div>

      <button class="btn-primary" @click="goToDashboard">Go to Dashboard</button>
    </div>
  </div>
</template>

<style scoped>
.wizard {
  max-width: 520px;
  margin: 0 auto;
}

.progress-track {
  height: 3px;
  background: var(--surface2);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--blue);
  border-radius: 2px;
  transition: width 0.4s ease;
}

.step-label {
  font-size: 0.7rem;
  color: var(--muted);
  text-align: right;
  margin-bottom: 1.5rem;
}

.step-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-start;
}

.logo-mark {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--blue), var(--purple));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 800;
  color: #fff;
}

h2 {
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 0.875rem;
  color: var(--muted);
  line-height: 1.6;
}

/* Checks */
.check-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.875rem;
  border-radius: 8px;
  font-size: 0.825rem;
  background: var(--surface2);
}

.check-item.ok   { color: var(--green); }
.check-item.warn { color: var(--orange); }
.check-item.loading { color: var(--muted); }

.check-icon {
  font-size: 0.875rem;
  font-weight: 700;
  flex-shrink: 0;
}

.mini-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid var(--border);
  border-top-color: var(--blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

/* Recommended ZIMs */
.subsection-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  width: 100%;
}

.installed-zims {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  width: 100%;
}

.zim-chip {
  font-size: 0.72rem;
  font-family: 'SF Mono', 'Fira Code', monospace;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  color: var(--muted);
}

.rec-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.rec-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 0.875rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.rec-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.rec-name {
  font-size: 0.825rem;
  font-weight: 600;
}

.rec-desc {
  font-size: 0.7rem;
  color: var(--muted);
}

.btn-copy {
  flex-shrink: 0;
  padding: 0.3rem 0.625rem;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 0.72rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-copy:hover  { background: var(--border); }
.btn-copy.copied { border-color: var(--green); color: var(--green); }

.hint {
  font-size: 0.72rem;
  color: var(--muted);
}

/* Done */
.done-icon {
  width: 48px;
  height: 48px;
  background: rgba(16, 185, 129, 0.15);
  color: var(--green);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  font-weight: 700;
}

.summary {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.825rem;
  color: var(--muted);
}

.summary-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Actions */
.step-actions {
  display: flex;
  gap: 0.75rem;
  width: 100%;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.btn-primary {
  padding: 0.5rem 1.25rem;
  background: var(--blue);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-primary:hover { opacity: 0.85; }

.btn-secondary {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--muted);
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-secondary:hover { background: var(--surface2); }

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
