import { ref, onUnmounted } from 'vue'
import dashjs from 'dashjs'

export function useDashPlayer(videoEl , url: string) {
  const player =  ref()
  const isPlaying = ref(false)

  const init = () => {
    if (!videoEl.value || !url) return

    const p = dashjs.MediaPlayer().create()
    p.initialize(videoEl.value, url, true)

    p.on(dashjs.MediaPlayer.events.PLAYBACK_STARTED, () => isPlaying.value = true)
    p.on(dashjs.MediaPlayer.events.PLAYBACK_PAUSED, () => isPlaying.value = false)

    player.value = p
  }

  onUnmounted(() => {
    player.value?.destroy()
  })

  return { player, isPlaying, init }
}
