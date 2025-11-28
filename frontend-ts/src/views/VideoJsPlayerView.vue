<!-- src/views/admin/VideoJsPlayerView.vue -->
<script setup>
import { ref } from "vue";
import VideoPlayer from "@/components/VideoPlayer.vue"; // Adjust path if needed
import "video.js/dist/video-js.css";
import { PlayIcon } from "@heroicons/vue/24/solid";

// Mock data (29 streams)
const videos = ref([
  // Add more...
]);

const media = fetch("/api/edgewares/")
  .then((data) => data.json())
  .then((data) => {
    console.log(data);
    console.log("Fetched media:");
    videos.value = data.results;
  });

// Modal state
const modalOpen = ref(false);
const currentVideo = ref(null);

const openPlayer = (video) => {
  const uri = video.streams.filter((s) => s.stream_protocol === "dash")[0].uri;
  currentVideo.value = {
    title: video.title,
    src: `http://ew-backend-01.tv.telekom.si${uri}`,
    type: "application/dash+xml",
  };

  modalOpen.value = true;
};

const closeModal = () => {
  modalOpen.value = false;
  currentVideo.value = null;
};

// Optional: Custom Video.js options
const playerOptions = (src, type) => ({
  controls: true,
  autoplay: true,
  preload: "auto",
  fluid: true,
  responsive: true,
  sources: [{ src, type }],
  html5: {
    vhs: {
      overrideNative: true,
    },
    nativeVideoTracks: false,
    nativeAudioTracks: false,
    nativeTextTracks: false,
  },
});
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold">Video.js Player Admin</h1>
      <span class="badge badge-primary badge-lg">29 Videos</span>
    </div>

    <!-- Grid of video cards -->
    <div
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
    >
      <div
        v-for="video in videos"
        :key="video.id"
        @click="openPlayer(video)"
        class="card bg-base-200 shadow-lg hover:shadow-2xl transition-all cursor-pointer border border-base-300"
      >
        <figure class="bg-base-300 h-48 flex items-center justify-center">
          <PlayIcon class="size-6 text-blue-500" />
        </figure>
        <div class="card-body p-4">
          <h2 class="card-title text-lg">{{ video.title }}</h2>
          <div class="flex gap-2 mt-2">
            <div class="badge badge-sm badge-outline">
              {{ video.title }}
            </div>
            <div v-if="video.badge" class="badge badge-error badge-sm">
              {{ video.badge }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Video.js Modal -->
    <dialog :open="modalOpen" class="modal">
      <div class="modal-box w-11/12 max-w-6xl p-0 overflow-hidden">
        <div
          class="flex justify-between items-center p-4 bg-base-200 border-b border-base-300"
        >
          <h3 class="font-bold text-xl">{{ currentVideo?.title }}</h3>
          <button @click="closeModal" class="btn btn-sm btn-circle btn-ghost">
            <PlayIcon class="size-6 text-blue-500" />
          </button>
        </div>

        <div class="bg-black">
          <VideoPlayer
            v-if="currentVideo"
            :options="playerOptions(currentVideo.src, currentVideo.type)"
            class="vjs-big-play-centered"
          />
        </div>

        <div class="p-4 bg-base-200 text-sm opacity-70">
          Source: <code class="text-xs break-all">{{ currentVideo?.src }}</code>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="closeModal">
        <button>close</button>
      </form>
    </dialog>
  </div>
</template>

<style scoped>
.modal::backdrop {
  background: rgba(0, 0, 0, 0.85);
}
</style>
