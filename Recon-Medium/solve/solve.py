import subprocess
from concurrent.futures import ThreadPoolExecutor

target_ip = "192.168.40.73"  # CHANGE THIS
port = 8554  # Default RTSP port
max_threads = 10

# Add more variations as needed
rtsp_paths = [
    "/live.sdp", "/stream1", "/h264.sdp", "/cam/realmonitor", "/axis-media/media.amp",
    "/live/ch00_0", "/ch1/main", "/media/video1", "/user=admin_password=admin_channel=1_stream=0.sdp",
    "/video/main", "/cam1", "/mpeg4", "/onvif1", "/streaming/channels/101", "/profile1",
    "/h264/ch1/main/av_stream", "/video", "/channel1", "/live0.264", "/dvr", "stream", "/ipcam.sdp",
    "/live/stream0", "/cam0", "/rtsp/live.sdp", "/video1.sdp", "/av0_0", "/av0_1",
    "/h264/ch1/sub/av_stream", "/h264/ch2/main/av_stream", "/ch1", "/ch2", "/live1.sdp",
    "/h265", "/stream", "/realmonitor", "/main", "/sub", "/live", "/h264",
    "/rtsp/stream", "/media.smp", "/video2.sdp", "/cam2", "/channel2", "/streaming",
    "/stream2", "/ch0", "/ch0_0", "/live2.sdp", "/profile2", "/profile3", "/0", "/1", "/2"
]

def check_rtsp(path):
    url = f"rtsp://{target_ip}:{port}{path}"
    try:
        print(f"[*] Checking: {url}")
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-rtsp_transport", "tcp", "-i", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        if result.returncode == 0:
            print(f"[+] VALID STREAM FOUND: {url}")
            with open("valid_rtsp_streams.txt", "a") as f:
                f.write(url + "\n")
    except subprocess.TimeoutExpired:
        print(f"[-] Timeout: {url}")
    except Exception as e:
        print(f"[!] Error checking {url}: {e}")

if __name__ == "__main__":
    with ThreadPoolExecutor(max_threads) as executor:
        executor.map(check_rtsp, rtsp_paths)
