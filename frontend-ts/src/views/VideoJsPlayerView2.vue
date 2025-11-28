<template>
  <div>
    <video-player :options="videoOptions" />
  </div>
</template>

<script>
import VideoPlayer from '@/components/VideoPlayer.vue';

export default {
  name: 'VideoExample',
  components: {
    VideoPlayer
  },
  data() {
    return {
      videoOptions: {
        autoplay: true,
        controls: true,
        sources: [
          {
            src:
              'https://dash.akamaized.net/akamai/bbb_30s/bbb_30s.mpd',
              type: 'video/mp4'
          }
        ]
      }
    };
  }
};
</script>