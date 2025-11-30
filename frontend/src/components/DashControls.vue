<script setup lang="ts">
import type { MediaPlayerClass } from 'dashjs'
import { computed } from 'vue'

interface Props {
  player: MediaPlayerClass | null
  isPlaying: boolean
  currentTime?: number
  duration?: number
}

const props = withDefaults(defineProps<Props>(), {
  currentTime: 0,
  duration: 0,
})

const emit = defineEmits<{
  seek: [time: number]
  toggle: []
}>()

const progress = computed(() => {
  if (!props.duration) return 0
  return (props.currentTime / props.duration) * 100
})

const formatTime = (sec: number) => {
  if (!isFinite(sec)) return '0:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

const seekTo = (e: Event) => {
  const target = e.target as HTMLInputElement
  const time = (Number(target.value) / 100) * props.duration
  emit('seek', time)
}

const seekRelative = (seconds: number) => {
  const newTime = props.currentTime + seconds
  emit('seek', Math.max(0, Math.min(newTime, props.duration)))
}

const toggleMute = () => {
  if (!props.player) return
  props.player.setMute(!props.player.isMuted())
}

const setVolume = (e: Event) => {
  const target = e.target as HTMLInputElement
  props.player?.setVolume(Number(target.value) / 100)
}

const toggleFullscreen = () => {
  const el = document.querySelector('.dash-player-container')
  if (!document.fullscreenElement && el) {
    el.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}
</script>

<template>
  <div class="dash-controls pointer-coarse:pointer-events-none">
    <!-- Progress Bar -->
    <div class="relative h-2 bg-base-300 group">
      <input
        type="range"
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
        :value="progress"
        @input="seekTo"
        min="0"
        max="100"
        step="0.1"
      />
      <div
        class="absolute inset-0 bg-primary transition-all duration-300 rounded-full pointer-events-none"
        :style="{ width: progress + '%' }"
      />
      <div class="absolute inset-0 bg-base-200/50 rounded-full" />
    </div>

    <!-- Bottom Controls Bar -->
    <div
      class="flex items-center justify-between px-4 py-3 bg-gradient-to-t from-black/80 to-transparent"
    >
      <div class="flex items-center gap-3">
        <!-- Play/Pause -->
        <button @click="emit('toggle')" class="btn btn-circle btn-sm btn-ghost text-white">
          <svg
            v-if="isPlaying"
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M6 4h4v16H6zm8 0h4v16h-4z" />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M8 5v14l11-7z" />
          </svg>
        </button>

        <!-- Rewind / Forward -->
        <button @click="seekRelative(-10)" class="btn btn-ghost btn-sm text-white">-10s</button>
        <button @click="seekRelative(10)" class="btn btn-ghost btn-sm text-white">+10s</button>

        <!-- Time -->
        <div class="hidden sm:block text-white font-mono text-sm">
          {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
        </div>
      </div>

      <div class="flex items-center gap-3">
        <!-- Volume -->
        <div class="flex items-center gap-2">
          <button @click="toggleMute" class="btn btn-ghost btn-sm text-white">
            <svg
              v-if="player?.isMuted() || (player?.getVolume() ?? 1) === 0"
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.06c1.48-.73 2.5-2.25 2.5-4.03zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"
              />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.06c1.48-.73 2.5-2.25 2.5-4.03z"
              />
            </svg>
          </button>
          <input
            type="range"
            class="range range-xs range-primary w-20 hidden sm:block"
            :value="player ? player.getVolume() * 100 : 100"
            @input="setVolume"
            min="0"
            max="100"
          />
        </div>

        <!-- Fullscreen -->
        <button @click="toggleFullscreen" class="btn btn-circle btn-sm btn-ghost text-white">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 8V4m0 0h4m-4 0l4 4m12-4v4m0 0h-4m4 0l-4-4M4 16v4m0 0h4m-4 0l4-4m12 4v-4m0 0h-4m4 0l-4 4"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* DaisyUI already handles everything! Minimal custom CSS needed */
.dash-controls {
}

/* Hover to show controls (optional enhancement) */
.dash-player-container:hover .dash-controls {
  @apply opacity-100;
}
.dash-controls {
  @apply opacity-0 transition-opacity duration-300;
}
.dash-player-container:hover .dash-controls,
.dash-controls:hover {
  @apply opacity-100;
}
</style>
