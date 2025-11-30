// composables/useDashPlayer.ts → Pure logic, no template
import { ref, onMounted, onUnmounted } from 'vue';
import { MediaPlayer } from 'dashjs';
export function useDashPlayer(
  videoEl,
  url: string
) {
  const player = ref(null)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)

  onMounted(() => {
    if (!videoEl.value) return
    player.value = MediaPlayer().create()
    player.value.initialize(videoEl.value, url, true)

    player.value.on('playbackTimeUpdated', () => {
      currentTime.value = player.value!.time()
      duration.value = player.value!.duration()
    })
    player.value.on('playbackPlaying', () => isPlaying.value = true)
    player.value.on('playbackPaused', () => isPlaying.value = false)
  })

  const seek = (time: number) => player.value?.seek(time)
  const togglePlay = () => isPlaying.value ? player.value?.pause() : player.value?.play()

  onUnmounted(() => player.value?.destroy())

  return { player, isPlaying, currentTime, duration, seek, togglePlay }
}
