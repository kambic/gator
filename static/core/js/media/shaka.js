import shaka from "shaka-player";

window.shaka = shaka;
console.log("[Vendor:Media] Shaka Player loaded:", !!shaka);
// static/core/js/media/shaka.js
export function shakaPlayer() {
  return {
    // Refs & state
    player: null,
    manifest: null,
    subtitleTracks: [],
    videoTracks: [],

    get config() {
      return this.player
        ? JSON.stringify(this.player.getConfiguration(), null, 2)
        : "{}";
    },

    /**
     * Initialize Shaka Player
     */
    async init() {
      if (!shaka.Player.isBrowserSupported()) {
        console.error("Shaka Player is not supported in this browser.");
        return;
      }

      // Reference the video element
      const video = this.$refs.video;
      if (!video) {
        console.error("Video element not found.");
        return;
      }

      // Initialize Shaka Player
      this.player = new shaka.Player(video);

      // Initialize Alpine store if it doesn't exist
      if (!Alpine.store("shaka")) {
        Alpine.store("shaka", {
          player: null,
          isLoaded: false,
          showMetrics: false,
        });
      }
      const store = Alpine.store("shaka");
      store.player = Alpine.raw(this.player);
      store.isLoaded = true;
      store.showMetrics = true;

      // Listen for Shaka errors
      this.player.addEventListener("error", this.onErrorEvent);

      console.log("[Shaka] Player initialized");
    },

    /**
     * Load a video stream
     */
    async loadStream() {
      if (!this.player) return console.error("Player not initialized");

      const url = this.manifest || this.manifestUri;
      if (!url) return console.error("No stream URL specified");

      const updatedUrl = url
        .replace("https://rr.sdn.si", "http://ew-backend-01.tv.telekom.si")
        .replace("__op/mss-pr", "__op/dash-default")
        .replace("__op/dash-wv", "__op/dash-default")
        .replace("__op/hls-fp", "__op/dash-default")
        .replace("/Manifest", "/manifest.mpd");

      try {
        console.log(`[Shaka] Player loaded: ${updatedUrl}`);
        await this.player.load(updatedUrl);
        this.player.setTextTrackVisibility(true);

        // Populate tracks for UI
        this.subtitleTracks = this.player.getTextTracks();
        this.videoTracks = this.player.getVariantTracks();

        console.log("[Shaka] Stream loaded", updatedUrl);
      } catch (err) {
        console.error("[Shaka] Video load failed:", err);
      }
    },

    /**
     * Toggle ABR (Adaptive Bitrate)
     */
    toggleAbr() {
      if (!this.player) return;
      const current = this.player.getConfiguration().abr.enabled;
      this.player.configure({ abr: { enabled: !current } });
    },

    /**
     * Change subtitle track
     */
    changeSubtitle(index) {
      if (!this.player) return;
      if (index === "" || this.subtitleTracks.length === 0) {
        this.player.setTextTrackVisibility(false);
        return;
      }
      const track = this.subtitleTracks[index];
      if (track) {
        this.player.selectTextTrack(track);
        this.player.setTextTrackVisibility(true);
      }
    },

    /**
     * Change video quality
     */
    changeQuality(index) {
      if (!this.player) return;
      if (index === "auto") {
        this.player.configure({ abr: { enabled: true } });
        return;
      }
      const selectedTrack = this.videoTracks[index];
      if (!selectedTrack) return;

      this.player.configure({ abr: { enabled: false } });
      this.player.selectVariantTrack(selectedTrack, true);
    },

    /**
     * Handle custom subtitle upload (.vtt)
     */
    handleSubtitleUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      if (!file.name.endsWith(".vtt")) {
        alert("Please upload a valid .vtt file.");
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        const blob = new Blob([reader.result], { type: "text/vtt" });
        const blobUrl = URL.createObjectURL(blob);
        const label = file.name.replace(".vtt", "");
        this.player.addTextTrack(blobUrl, "en", "subtitle", "vtt", label);

        // Refresh tracks
        this.subtitleTracks = this.player.getTextTracks();
        console.log("[Shaka] Subtitle added:", label);
      };
      reader.readAsText(file);
    },

    /**
     * Shaka Player error handler
     */
    onErrorEvent(ev) {
      console.error("[Shaka] Error:", ev.detail);
    },
  };
}

export function shakaMetrics() {
  return {
    // configuration
    pollIntervalSec: 1,
    pollIntervalMs: 1000,
    maxPoints: 120, // keep ~2 minutes at 1s
    // internal
    timer: null,
    player: null,
    latestJSON: "",
    // chart objects
    charts: { bandwidth: null, buffer: null, bitrate: null },

    init() {
      // create charts
      this.$watch("$store.shaka.isLoaded", (val) => {
        if (val) {
          this.player = window.shakaApp.player; // safe direct reference                    console.log('Metrics bound to player', val)
          this.createCharts();

          // this.startPolling()
        }
      });
    },

    updateInterval() {
      this.pollIntervalMs = Math.round(this.pollIntervalSec * 1000);
      this.stopPolling();
      this.startPolling();
    },

    startPolling() {
      // poll immediately and then on interval
      this.poll();
      this.timer = setInterval(() => this.poll(), this.pollIntervalMs);
    },

    stopPolling() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
    },

    forceSnapshot() {
      this.poll();
    },

    clearData() {
      const empty = (chart) => {
        chart.data.labels = [];
        chart.data.datasets.forEach((ds) => (ds.data = []));
        chart.update();
      };
      empty(this.charts.bandwidth);
      empty(this.charts.buffer);
      empty(this.charts.bitrate);
      this.latestJSON = "";
    },

    poll() {
      // pick player if it was created after init
      if (!this.player) {
        // no player — nothing to do
        this.latestJSON =
          "No shaka player available (set window.shakaPlayer = yourPlayer)";
        return;
      }

      // get snapshot stats
      let stats = {};
      try {
        stats = this.player.getStats() || {};
      } catch (e) {
        console.error("getStats failed", e);
        this.latestJSON = "getStats() error: " + e;
        return;
      }

      // buffer: try player.getBufferedInfo() if available; fallback to video element
      let bufferLen = null;
      try {
        if (typeof this.player.getBufferedInfo === "function") {
          const bi = this.player.getBufferedInfo();
          // bi.total is an intersection that represents playable ranges;
          // calculate buffer ahead from currentTime (naive)
          const currentTime =
            (this.player.getMediaElement &&
              this.player.getMediaElement().currentTime) ||
            0;
          // when bi.total has ranges, find end of range that contains currentTime
          bufferLen = 0;
          if (bi && bi.total && bi.total.length) {
            for (const r of bi.total) {
              if (currentTime >= r.start && currentTime <= r.end) {
                bufferLen = Math.max(0, r.end - currentTime);
                break;
              }
            }
          } else {
            // fallback: try HTMLMediaElement buffered
            const m = this.player.getMediaElement();
            if (m && m.buffered && m.buffered.length) {
              for (let i = 0; i < m.buffered.length; i++) {
                if (
                  currentTime >= m.buffered.start(i) &&
                  currentTime <= m.buffered.end(i)
                ) {
                  bufferLen = Math.max(0, m.buffered.end(i) - currentTime);
                  break;
                }
              }
            }
          }
        } else {
          // fallback to the HTMLMediaElement buffered ranges
          const m = this.player.getMediaElement();
          const currentTime = (m && m.currentTime) || 0;
          bufferLen = 0;
          if (m && m.buffered && m.buffered.length) {
            for (let i = 0; i < m.buffered.length; i++) {
              if (
                currentTime >= m.buffered.start(i) &&
                currentTime <= m.buffered.end(i)
              ) {
                bufferLen = Math.max(0, m.buffered.end(i) - currentTime);
                break;
              }
            }
          }
        }
      } catch (e) {
        console.warn("buffer calc failed", e);
        bufferLen = null;
      }

      // estimated bandwidth (Shaka reports bytes/sec or bits/sec? in practice it's bits/sec)
      // JSDoc shows estimated bandwidth field; we'll treat it as bits/sec and convert to Mbps.
      const estBw =
        stats.estimatedBandwidth != null
          ? stats.estimatedBandwidth / 1_000_000
          : null;
      // current video bitrate: look at variant/track info if available
      // We'll attempt to read active variant track bitrate (videoBandwidth) from getVariantTracks
      let currentBitrateKbps = null;
      try {
        if (this.player.getVariantTracks) {
          const tracks = this.player.getVariantTracks();
          // find active track
          const active = (tracks && tracks.find((t) => t.active)) || null;
          if (active) {
            // videoBandwidth might be bytes/sec or bits/sec; many Shaka externs use bits/sec
            currentBitrateKbps =
              active.videoBandwidth != null
                ? Math.round(active.videoBandwidth / 1000)
                : null;
          } else if (stats.streamBandwidth) {
            currentBitrateKbps = Math.round(
              (stats.streamBandwidth || 0) / 1000,
            );
          }
        }
      } catch (e) {
        console.warn("current bitrate read failed", e);
      }

      // timestamp label
      const label = new Date().toLocaleTimeString();

      // push to charts
      this.pushPoint(
        this.charts.bandwidth,
        label,
        estBw !== null ? Number(estBw.toFixed(2)) : null,
      );
      this.pushPoint(
        this.charts.buffer,
        label,
        bufferLen !== null ? Number(bufferLen.toFixed(2)) : null,
      );
      this.pushPoint(
        this.charts.bitrate,
        label,
        currentBitrateKbps !== null ? currentBitrateKbps : null,
      );

      // show latest JSON snapshot (trim non-serializable)
      const toShow = {
        time: new Date().toISOString(),
        estimatedBandwidth: stats.estimatedBandwidth,
        bufferLen: bufferLen,
        currentBitrateKbps: currentBitrateKbps,
        statsKeys: Object.keys(stats || {}),
      };
      this.latestJSON = JSON.stringify(toShow, null, 2);
    },

    pushPoint(chart, label, value) {
      if (!chart) return;
      chart.data.labels.push(label);
      chart.data.datasets[0].data.push(value);
      // trim
      while (chart.data.labels.length > this.maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets.forEach((ds) => ds.data.shift());
      }
      chart.update("none"); // fast update
    },

    createCharts() {
      // bandwidth chart (Mbps)
      const bwCtx = document.getElementById("bandwidthChart").getContext("2d");
      this.charts.bandwidth = new Chart(bwCtx, {
        type: "line",
        data: {
          labels: [],
          datasets: [
            {
              label: "Estimated bandwidth (Mbps)",
              data: [],
              spanGaps: true,
              tension: 0.2,
              pointRadius: 0,
              borderWidth: 2,
            },
          ],
        },
        options: {
          animation: false,
          scales: {
            x: { display: true },
            y: { beginAtZero: true, title: { display: true, text: "Mbps" } },
          },
          plugins: { legend: { display: false } },
        },
      });

      // buffer chart (seconds)
      const bufCtx = document.getElementById("bufferChart").getContext("2d");
      this.charts.buffer = new Chart(bufCtx, {
        type: "line",
        data: {
          labels: [],
          datasets: [
            {
              label: "Buffer length (s)",
              data: [],
              fill: true,
              tension: 0.25,
              pointRadius: 0,
              borderWidth: 1,
            },
          ],
        },
        options: {
          animation: false,
          scales: {
            x: { display: true },
            y: { beginAtZero: true, title: { display: true, text: "Seconds" } },
          },
          plugins: { legend: { display: false } },
        },
      });

      // bitrate chart (kbps)
      const brCtx = document.getElementById("bitrateChart").getContext("2d");
      this.charts.bitrate = new Chart(brCtx, {
        type: "line",
        data: {
          labels: [],
          datasets: [
            {
              label: "Video bitrate (kbps)",
              data: [],
              spanGaps: true,
              tension: 0.15,
              pointRadius: 0,
            },
          ],
        },
        options: {
          animation: false,
          scales: {
            x: { display: true },
            y: { beginAtZero: true, title: { display: true, text: "kbps" } },
          },
          plugins: { legend: { display: false } },
        },
      });
    },
  };
}
