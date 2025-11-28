<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import dashjs from 'dashjs'

interface Props {
  url: string
  autoplay?: boolean
  controls?: boolean
  width?: string
  height?: string
  poster?: string
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: true,
  controls: true,
  width: '100%',
  height: '100%',
})

const emit = defineEmits<{
  loaded: [player: dashjs.MediaPlayerClass]
  error: [event: any]
  playbackStarted: []
}>()

const videoEl = ref<HTMLVideoElement | null>(null)
const container = ref<HTMLElement | null>(null)
let player: dashjs.MediaPlayerClass | null = null

// Initialize dash.js player
const initPlayer = () => {
  if (!videoEl.value || !props.url) return

  // Destroy previous instance if exists
  if (player) {
    player.destroy()
    player = null
  }

  // Create new player instance
  player = dashjs.MediaPlayer().create()

  // Basic configuration
  player.initialize(videoEl.value, props.url, props.autoplay)

  // Recommended settings for better experience
  player.updateSettings({
    streaming: {
      buffer: {
        fastSwitchEnabled: true,           // Abr faster switching
        bufferToKeep: 20,                  // Seconds to keep behind
        stableBufferTime: 12,              // Buffer before play
        bufferTimeAtTopQuality: 30,        // For long-form content
      },
      abr: {
        autoSwitchBitrate: { video: true, audio: true },
      },
    },
  })

  // Event listeners
  player.on(dashjs.MediaPlayer.events.PLAYBACK_STARTED, () => {
    emit('playbackStarted')
  })

  player.on(dashjs.MediaPlayer.events.ERROR, (e: any) => {
    console.error('Dash.js Error:', e)
    emit('error', e)
  })

  player.on(dashjs.MediaPlayer.events.MANIFEST_LOADED, () => {
    console.log('DASH manifest loaded successfully')
  })

  emit('loaded', player)
}

// Handle URL changes
watch(() => props.url, (newUrl) => {
  if (newUrl && player) {
    player.attachSource(newUrl)
  }
})

// Resize video element to container size
const resizePlayer = () => {
  if (!container.value || !videoEl.value) return
  const { clientWidth, clientHeight } = container.value
  videoEl.value.style.width = clientWidth + 'px'
  videoEl.value.style.height = clientHeight + 'px'
}

// Lifecycle
onMounted(async () => {
  await nextTick() // Wait for DOM
  initPlayer()
  resizePlayer()
  window.addEventListener('resize', resizePlayer)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizePlayer)
  if (player) {
    player.destroy()
    player = null
  }
})
</script>

<template>
  <div
    ref="container"
    class="dash-player-container"
    :style="{ width: props.width, height: props.height, position: 'relative', background: '#000' }"
  >
    <video
      ref="videoEl"
      :controls="controls"
      :autoplay="autoplay"
      :poster="poster"
      style="width: 100%; height: 100%; object-fit: contain;"
      playsinline
      webkit-playsinline
    />
    <!-- Optional loading overlay -->
    <div v-if="!videoEl?.readyState" class="loading-overlay">
      <div class="spinner" />
      Loading DASH stream...
    </div>
  </div>
</template>

<style scoped>
.dash-player-container {
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-family: system-ui, sans-serif;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
