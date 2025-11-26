import os
import subprocess
import threading
import http.server
import socketserver


class DashStreamer:
    def __init__(self, input_source, output_dir="dash_output", live=False, serve=False, port=8080):
        self.input_source = input_source
        self.output_dir = output_dir
        self.live = live
        self.serve = serve
        self.port = port
        self.process = None
        self.server_thread = None

    def _build_ffmpeg_command(self):
        os.makedirs(self.output_dir, exist_ok=True)

        input_flags = ["-re"] if not self.live else []
        input_flags += ["-i", self.input_source]

        output_path = os.path.join(self.output_dir, "manifest.mpd")

        command = [
            "ffmpeg",
            *input_flags,
            "-map",
            "0:v",
            "-map",
            "0:a",
            "-b:v:0",
            "1000k",
            "-s:v:0",
            "640x360",
            "-b:v:1",
            "2000k",
            "-s:v:1",
            "1280x720",
            "-b:a",
            "128k",
            "-use_timeline",
            "1",
            "-use_template",
            "1",
            "-adaptation_sets",
            "id=0,streams=v id=1,streams=a",
            "-f",
            "dash",
            output_path,
        ]

        return command

    def start_encoding(self):
        command = self._build_ffmpeg_command()
        print(f"Starting FFmpeg with command:\n{' '.join(command)}\n")

        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Print FFmpeg output in background
        threading.Thread(target=self._print_ffmpeg_output, daemon=True).start()

        if self.serve:
            self._start_http_server()

    def _print_ffmpeg_output(self):
        for line in iter(self.process.stdout.readline, b""):
            print("[ffmpeg]", line.decode(errors="ignore").strip())

    def _start_http_server(self):
        def run_server():
            os.chdir(self.output_dir)
            handler = http.server.SimpleHTTPRequestHandler
            with socketserver.TCPServer(("", self.port), handler) as httpd:
                print(f"Serving DASH at http://localhost:{self.port}/manifest.mpd")
                httpd.serve_forever()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("FFmpeg process terminated.")

    def launch_shaka_player(self):
        manifest_url = f"http://localhost:{self.port}/manifest.mpd"
        shaka_demo_url = "https://shaka-player-demo.appspot.com/demo/#"
        query_params = {"asset": manifest_url, "autoplay": "true"}
        full_url = shaka_demo_url + urllib.parse.urlencode(query_params)
        print(f"Opening Shaka Player in browser: {full_url}")


streamer = DashStreamer(input_source="video.mp4", live=False, serve=True, port=8080)
streamer.start_encoding()

# streamer = DashStreamer(input_source="/dev/video0", live=True, serve=False)
# streamer.start_encoding()

# streamer.stop()
# # Optional: Wait a bit for encoding and server to start
# import time

# time.sleep(2)

# streamer.launch_shaka_player()
