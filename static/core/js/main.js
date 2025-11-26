// static/core/js/main.js
import "vite/modulepreload-polyfill";
import "../css/style.css";
import Alpine from "alpinejs";
import { shakaPlayer } from "./media/shaka.js";

window.Alpine = Alpine;
// Register the global app store FIRST
// Start Alpine AFTER store is ready
// Initialize Alpine Data object
document.addEventListener("alpine:init", () => {
  Alpine.data("shakaPlayer", shakaPlayer); // Name it explicitly

  Alpine.store("shaka", {
    player: null,
    isLoaded: false,
    showMetrics: false,
  });

  Alpine.data(shakaPlayer);
  // File Explorer Component Data (Refactored from inline script)
});
Alpine.start();
