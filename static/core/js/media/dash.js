// dashPlayer.js (cleaned + Alpine.js + Bootstrap 5 + Chart.js compatible)

import {MediaPlayer} from "dashjs";

export function dashPlayer() {
    return {
        player: null,
        subtitleTracks: [],
        videoRepList: [],
        chart: null,
        maxPoints: 30,
        manifest: null,


        init() {
            const video = this.$refs.video;
            this.player = MediaPlayer().create();


        },
        async loadStream() {
            console.log(`[Media] Shaka Player loading stream for stream ${this.manifest}`)
            const url = this.manifest
            const updatedUrl = url.replace('https://rr.sdn.si', 'http://ew-backend-01.tv.telekom.si')
                .replace('__op/mss-pr', '__op/mss-default')
                .replace('__op/dash-wv', '__op/dash-default')
                .replace('__op/hls-fp', '__op/hls-default')

            try {
                this.player.initialize(video, "https://dash.akamaized.net/envivio/EnvivioDash3/manifest.mpd", true);

                this.player.on(MediaPlayer.events.STREAM_INITIALIZED, () => {
                    this.videoRepList = this.player.getTracksFor("video");
                });
            } catch (err) {
                console.error('Video load failed:', err);
            }
        },


        changeQuality(index) {
            if (index === "auto") {
                this.player.updateSettings({streaming: {abr: {autoSwitchBitrate: {video: true}}}});
            } else {
                this.player.updateSettings({streaming: {abr: {autoSwitchBitrate: {video: false}}}});
                const rep = this.videoRepList[index];
                if (rep) this.player.setQualityFor("video", rep.index);
            }
        },

        handleSubtitleUpload(event) {
            const file = event.target.files[0];
            if (!file || !file.name.endsWith(".vtt")) return alert("Upload a valid .vtt file");

            const reader = new FileReader();
            reader.onload = () => {
                const blobUrl = URL.createObjectURL(new Blob([reader.result], {type: "text/vtt"}));
                const track = document.createElement("track");
                track.kind = "subtitles";
                track.label = file.name.replace(".vtt", "");
                track.srclang = "en";
                track.src = blobUrl;
                this.$refs.video.appendChild(track);
                this.reloadSubtitleTracks();
            };
            reader.readAsText(file);
        },

        reloadSubtitleTracks() {
            const textTracks = this.$refs.video.textTracks;
            this.subtitleTracks = Array.from(textTracks).map(track => ({
                label: track.label,
                language: track.language,
                trackObj: track
            }));
        },

        changeSubtitle(index) {
            this.subtitleTracks.forEach((t, i) => {
                t.trackObj.mode = (i == index) ? "showing" : "disabled";
            });
        },

        initChart() {
            const ctx = this.$refs.bufferChart.getContext("2d");
            this.chart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: [],
                    datasets: [{
                        label: "Buffer Level (s)",
                        borderColor: "#0d6efd",
                        backgroundColor: "rgba(13,110,253,0.1)",
                        data: []
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {title: {display: true, text: "Time (s)"}},
                        y: {title: {display: true, text: "Buffer (s)"}, min: 0}
                    }
                }
            });
        },

        updateBufferChart() {
            const video = this.$refs.video;
            let buffered = 0;
            if (video.buffered.length > 0) {
                buffered = video.buffered.end(video.buffered.length - 1) - video.currentTime;
            }

            const time = video.currentTime.toFixed(1);
            const labels = this.chart.data.labels;
            const data = this.chart.data.datasets[0].data;

            labels.push(time);
            data.push(buffered.toFixed(2));

            if (labels.length > this.maxPoints) {
                labels.shift();
                data.shift();
            }

            this.chart.update("none");
        }
    };
}
