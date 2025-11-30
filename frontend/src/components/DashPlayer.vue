<!-- DashPlayer.vue → Component (has template) -->
<script setup lang="ts">
import { useDashPlayer } from '@/composables/useDashPlayer'
import DashControls from '@/components/DashControls.vue';
import { ref } from 'vue';

const videoEl = ref()
const uris = [
  'https://dash.akamaized.net/envivio/EnvivioDash3.mpd',
  'https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps.mpd',
  'https://media.axprod.net/TestVectors/v9-MultiRes.mpd',
  'https://livesim2.dashif.org/livesim2/periods_60/testpic_2s/Manifest.mpd',
]
const url = uris[1]

const { player, isPlaying, seek, togglePlay } = useDashPlayer(videoEl, url)
</script>

<template>
  <div class="player">
    <video ref="videoEl" />
    <DashControls :player="player" :is-playing="isPlaying" @seek="seek" @toggle="togglePlay" />
  </div>
</template>
