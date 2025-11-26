import Alpine from "alpinejs";
import "flowbite";
import "../css/style.css";

console.log("VOD frontend loaded");

// Video.js + plugins
import videojs from "video.js";
import "video.js/dist/video-js.css";
import "videojs-hotkeys";
import "videojs-mobile-ui";

// Optional: Beautiful theme (highly recommended)
// import "videojs-theme-forest/dist/videojs-theme-forest.css"; // or any theme

window.Alpine = Alpine;
Alpine.start();

// Auto dark mode
if (
  localStorage.theme === "dark" ||
  (!localStorage.theme &&
    window.matchMedia("(prefers-color-scheme: dark)").matches)
) {
  document.documentElement.classList.add("dark");
}

// Initialize Video.js player when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  return;
  const player = videojs("my-video", {
    controls: true,
    autoplay: false,
    preload: "metadata",
    fluid: true,
    responsive: true,
    playbackRates: [0.5, 0.75, 1, 1.25, 1.5, 2],
    plugins: {
      hotkeys: {
        volumeStep: 0.1,
        seekStep: 5,
        enableModifiersForNumbers: false,
      },
      mobileUi: true,
      hlsQualitySelector: {
        displayCurrentQuality: true,
      },
    },
  });

  // Optional: Add quality selector button for HLS

  window.player = player; // for debugging
});
