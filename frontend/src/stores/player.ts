// stores/player.ts
import { defineStore } from 'pinia'

export const usePlayerStore = defineStore('player', () => {
  const currentStream = ref<string>('')
  const volume = ref(1)
  const muted = ref(false)

  function setStream(url: string) {
    currentStream.value = url
  }

  function setVolume(value: number) {
    volume.value = Math.max(0, Math.min(1, value))
  }

  return {
    currentStream: readonly(currentStream),
    volume,
    muted,
    setStream,
    setVolume
  }
})
