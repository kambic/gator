<template>
  <div class="dash-analyzer">
    <div class="controls">
      <input v-model="manifestUrl" placeholder="Enter DASH MPD URL" />
      <button @click="loadManifest">Load & Initialize</button>
      <label><input type="checkbox" v-model="autoplay" /> Autoplay</label>
      <button @click="clearLogs">Clear Logs</button>
    </div>

    <div class="main">
      <div class="player-wrap">
        <video ref="videoEl" controls playsinline preload="metadata" :autoplay="autoplay"></video>
        <div class="quick-stats">
          <div>Buffer: {{ bufferLevelString }}</div>
          <div>Current Quality (video): {{ currentQualityIndex }}</div>
          <div>Available representations: {{ representations.length }}</div>
        </div>

        <div class="representation-controls" v-if="representations.length">
          <label>Manual video quality:</label>
          <select v-model.number="selectedQualityIndex" @change="setManualQuality">
            <option :value="-1">Auto</option>
            <option v-for="(r, idx) in representations" :key="idx" :value="idx">
              {{ idx }} — {{ r.height }}p @ {{ formatBitrate(r.bitrate) }}
            </option>
          </select>
        </div>
      </div>

      <div class="analysis">
        <section>
          <h3>Manifest / Info</h3>
          <div v-if="manifestLoaded">
            <div><strong>MPD:</strong> {{ manifestUrl }}</div>
            <div><strong>Period count:</strong> {{ mpdInfo.periodCount }}</div>
            <div><strong>Duration (s):</strong> {{ mpdInfo.duration }}</div>
          </div>
          <pre v-else>Load a DASH MPD to inspect.</pre>
        </section>

        <section>
          <h3>Representations (video)</h3>
          <table v-if="representations.length">
            <thead>
              <tr>
                <th>#</th>
                <th>Bandwidth</th>
                <th>Width</th>
                <th>Height</th>
                <th>Codec</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(r, idx) in representations" :key="idx">
                <td>{{ idx }}</td>
                <td>{{ formatBitrate(r.bitrate) }}</td>
                <td>{{ r.width || '-' }}</td>
                <td>{{ r.height || '-' }}</td>
                <td>{{ r.codecs || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <section>
          <h3>Event Log</h3>
          <div class="log" ref="logBox">
            <div v-for="(l, idx) in logs" :key="idx" class="log-line">
              [{{ l.time }}] <strong>{{ l.event }}</strong> — {{ l.summary }}
            </div>
          </div>
        </section>

        <section>
          <h3>Other tools & quick links</h3>
          <ul>
            <li>
              dash.js — reference MPEG-DASH web client (use for standard compliance & event
              debugging)
            </li>
            <li>Shaka Player — broader format/DRM testing and multi-format workflows</li>
            <li>Video.js + contrib-dash — customizable UI + plugin ecosystem</li>
            <li>
              Network inspector (browser DevTools) — HAR capture to analyze segment timing and sizes
            </li>
            <li>MPD inspectors (online / CLI) — static MPD validation and manifest diffs</li>
          </ul>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>

import { ref, reactive,  onBeforeUnmount,  nextTick, computed } from 'vue'
import dashjs from 'dashjs'

const videoEl = ref(null)
const manifestUrl = ref('')
const autoplay = ref(false)
const logs = reactive([])

const playerRef = ref(null)
const manifestLoaded = ref(false)
const mpdInfo = reactive({ periodCount: 0, duration: 0 })
const representations = ref([])
const selectedQualityIndex = ref(-1)
const currentQualityIndex = ref(-1)
const bufferLevel = ref(0)

function pushLog(event, summary = '') {
  const t = new Date().toLocaleTimeString()
  logs.push({ time: t, event, summary })
  // keep last 500
  if (logs.length > 500) logs.shift()
  nextTick(() => {
    const box = document.querySelector('.log')
    if (box) box.scrollTop = box.scrollHeight
  })
}

function formatBitrate(b) {
  if (b == null) return '-'
  if (b >= 1000000) return (b / 1000000).toFixed(2) + ' Mbps'
  return Math.round(b / 1000) + ' kbps'
}

function clearLogs() {
  logs.splice(0, logs.length)
}

function setManualQuality() {
  const p = playerRef.value
  if (!p) return
  const idx = selectedQualityIndex.value
  if (idx === -1) {
    pushLog('QUALITY', 'Switching to auto ABR')
    p.setAutoSwitchQualityFor('video', true)
  } else {
    pushLog('QUALITY', `Forcing video quality to index ${idx}`)
    p.setAutoSwitchQualityFor('video', false)
    p.setQualityFor('video', idx)
  }
}

function loadManifest() {
  if (!manifestUrl.value) return pushLog('ERROR', 'No MPD URL provided')
  if (playerRef.value) {
    try {
      playerRef.value.reset()
    } catch (e) {}
    playerRef.value = null
    representations.value = []
    manifestLoaded.value = false
  }

  const video = videoEl.value
  const player = dashjs.MediaPlayer().create()
  playerRef.value = player

  // Useful default config for analysis
  player.updateSettings({
    streaming: { fastSwitchEnabled: true, buffer: { stableBufferTime: 20 } },
  })

  // Attach event listeners for inspection
  const E = dashjs.MediaPlayer.events
  const handlers = {
    [E.STREAM_INITIALIZED]: () => pushLog('STREAM_INITIALIZED', 'Stream ready'),
    [E.BUFFER_LEVEL_UPDATED]: (e) => {
      bufferLevel.value = e?.bufferLevel ?? bufferLevel.value
      pushLog('BUFFER_LEVEL_UPDATED', `level=${(bufferLevel.value || 0).toFixed(2)}s`)
    },
    [E.PLAYBACK_STARTED]: () => pushLog('PLAYBACK_STARTED'),
    [E.PLAYBACK_PLAYING]: () => pushLog('PLAYBACK_PLAYING'),
    [E.PLAYBACK_PAUSED]: () => pushLog('PLAYBACK_PAUSED'),
    [E.QUALITY_CHANGE_RENDERED]: (e) => {
      currentQualityIndex.value = e?.newQuality
      pushLog('QUALITY_RENDERED', `new=${e?.newQuality} old=${e?.oldQuality}`)
    },
    [E.FRAGMENT_LOADING_STARTED]: (e) => {
      pushLog('FRAGMENT_LOADING_STARTED', e?.request?.url || JSON.stringify(e?.request?._url || {}))
    },
    [E.FRAGMENT_LOADING_COMPLETED]: (e) => {
      pushLog('FRAGMENT_LOADING_COMPLETED', e?.request?.url || '')
    },
    [E.ERROR]: (e) => {
      pushLog('ERROR', JSON.stringify(e))
    },
  }

  for (const k in handlers) player.on(k, handlers[k])

  // initialize player
  player.initialize(video, manifestUrl.value, autoplay.value)

  // small delay and then read manifest-derived info
  setTimeout(() => {
    try {
      manifestLoaded.value = true
      // basic MPD info (best-effort)
      const dashMetrics = player.getDashMetrics && player.getDashMetrics()
      mpdInfo.periodCount =
        (player.getDashManifest && player.getDashManifest()?.Period?.length) || 1
      mpdInfo.duration = player.duration || (player.getDuration ? player.getDuration() : 0)

      // representations (video) — use dash.js API to read bitrate list
      const list = player.getBitrateInfoListFor && player.getBitrateInfoListFor('video')
      if (list && list.length) {
        representations.value = list.map((item) => ({
          bitrate: item.bandwidth ?? item.bitrate ?? item.bandwidthEstimate ?? null,
          width: item.width,
          height: item.height,
          codecs: item.codecs || item.mimeType,
        }))
      }

      // current quality
      currentQualityIndex.value = player.getQualityFor ? player.getQualityFor('video') : -1

      pushLog('MANIFEST_PARSED', `representations=${representations.value.length}`)
    } catch (err) {
      pushLog('ERROR', 'Failed to read manifest info: ' + (err && err.message))
    }
  }, 800)
}

onBeforeUnmount(() => {
  try {
    playerRef.value && playerRef.value.reset()
  } catch (e) {

  }
})

const bufferLevelString = computed(() =>
  bufferLevel.value != null ? bufferLevel.value.toFixed(2) + 's' : '-',
)
</script>

<style scoped>
.dash-analyzer {
  font-family:
    system-ui,
    -apple-system,
    'Segoe UI',
    Roboto,
    'Helvetica Neue',
    Arial;
}
.controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  padding: 0.5rem;
}
.controls input {
  flex: 1;
  padding: 0.4rem;
}
.main {
  display: flex;
  gap: 1rem;
  padding: 0.5rem;
}
.player-wrap {
  flex: 1;
  max-width: 60%;
}
.player-wrap video {
  width: 100%;
  height: auto;
  background: #000;
}
.quick-stats {
  display: flex;
  gap: 1rem;
  margin-top: 0.4rem;
}
.analysis {
  flex: 1;
  overflow: auto;
  max-height: 70vh;
}
.analysis section {
  margin-bottom: 1rem;
  background: #fafafa;
  padding: 0.6rem;
  border-radius: 6px;
}
.log {
  max-height: 200px;
  overflow: auto;
  background: #111;
  color: #eee;
  padding: 0.5rem;
  font-family: monospace;
}
.log-line {
  padding: 0.15rem 0;
}
.representation-controls {
  margin-top: 0.5rem;
}
table {
  width: 100%;
  border-collapse: collapse;
}
td,
th {
  padding: 0.3rem;
  border-bottom: 1px solid #eee;
  text-align: left;
}
</style>
