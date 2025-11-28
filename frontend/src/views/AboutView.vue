<script setup lang="ts">
import DashPlayer from '@/components/DashPlayer.vue'

const streamUrl = 'https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd'
// Big Buck Bunny test stream (public domain)

let playerInstance: dashjs.MediaPlayerClass | null = null

const onPlayerLoaded = (player: dashjs.MediaPlayerClass) => {
  playerInstance = player
  console.log('Player ready!', player.getVersion())
}

const seekForward = () => {
  if (playerInstance) {
    const time = playerInstance.time() + 10
    playerInstance.seek(time)
  }
}
</script>

<template>
  <div class="player-page">
    <h1>Vue 3 + dash.js Player</h1>

    <DashPlayer
      :url="streamUrl"
      autoplay
      controls
      width="100%"
      height="600px"
      @loaded="onPlayerLoaded"
      @playbackStarted="() => console.log('Started playing!')"
      @error="(e) => console.error('Player error:', e)"
    />

    <div class="controls" style="margin-top: 20px;">
      <button @click="seekForward">+10s</button>
      <button @click="playerInstance?.pause()">Pause</button>
      <button @click="playerInstance?.play()">Play</button>
    </div>
  </div>
</template>
