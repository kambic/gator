<template>
  <div class="min-h-screen bg-base-200 p-4">
    <div class="max-w-7xl mx-auto space-y-4">
      <div class="card bg-base-100 shadow">
        <div class="card-body gap-4">
          <h1 class="card-title">VIDRA Analyzer</h1>
          <div class="flex gap-2">
            <input
              v-model="manifestUrl"
              class="input input-bordered flex-1"
              placeholder="Enter DASH MPD URL"
            />
            <button class="btn btn-primary" @click="initPlayer">Load</button>
            <button class="btn" @click="clearData">Reset</button>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- Player -->
            <div class="card bg-base-200">
              <div class="card-body">
                <video ref="video" controls class="w-full bg-black"></video>
                <div class="stats shadow mt-3">
                  <div class="stat">
                    <div class="stat-title">Buffer</div>
                    <div class="stat-value text-sm">{{ buffer.toFixed(2) }} s</div>
                  </div>
                  <div class="stat">
                    <div class="stat-title">Video Quality</div>
                    <div class="stat-value text-sm">{{ currentQuality }}</div>
                  </div>
                  <div class="stat">
                    <div class="stat-title">Video Bitrate</div>
                    <div class="stat-value text-sm">{{ currentBitrate }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Charts -->
            <div class="card bg-base-200">
              <div class="card-body space-y-4">
                <h2 class="card-title text-lg">Playback Metrics</h2>

                <div>
                  <div class="text-sm mb-1">Buffer Level (s)</div>
                  <canvas ref="bufferChart"></canvas>
                </div>

                <div>
                  <div class="text-sm mb-1">Selected Video Bitrate (kbps)</div>
                  <canvas ref="bitrateChart"></canvas>
                </div>
              </div>
            </div>
          </div>

          <!-- Logs -->
          <div class="card bg-base-200">
            <div class="card-body">
              <h2 class="card-title text-lg">Event Log</h2>
              <div class="mockup-code max-h-64 overflow-auto">
                <pre v-for="(l, i) in logs" :key="i"><code>[{{l.t}}] {{l.m}}</code></pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { MediaPlayer } from 'dashjs'

const video = ref()
const manifestUrl = ref(
  'https://livesim.dashif.org/livesim/chunkdur_1/ato_7/testpic4_8s/Manifest.mpd',
)
const logs = ref([])

let player
let bufferChart
let bitrateChart

const buffer = ref(0)
const currentQuality = ref('-')
const currentBitrate = ref('-')

function log(msg) {
  logs.value.unshift({ t: new Date().toLocaleTimeString(), m: msg })
  if (logs.value.length > 200) logs.value.pop()
}

function initPlayer() {
  if (!manifestUrl.value) return
  clearData()

  player = MediaPlayer().create()
  player.initialize(video.value, manifestUrl.value, true)

  log('Player initialized')
}

function clearData() {
  if (player) {
    try {
      player.reset()
    } catch {
      log('Player reset failed')
    }
  }
  logs.value = []
  buffer.value = 0
  currentQuality.value = '-'
  currentBitrate.value = '-'

}
</script>
