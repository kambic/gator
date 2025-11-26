// vite.config.js (project root)
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import { resolve } from "path";

export default defineConfig({
  plugins: [tailwindcss()],
  base: "/static/",
  server: {
    port: 5173,
    strictPort: true,
  },

  build: {
    manifest: "manifest.json",
    outDir: resolve(__dirname, "assets"),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        // Keep your existing admin bundle
        admin: resolve(__dirname, "static/core/js/main.js"),

        // New: VOD modern frontend
        vod: resolve(__dirname, "static/vod/js/main.js"),
      },
      output: {
        entryFileNames: "js/[name].[hash].js",
        chunkFileNames: "js/chunks/[name].[hash].js",
        assetFileNames: "assets/[name].[hash][extname]",
      },
    },
  },
});
