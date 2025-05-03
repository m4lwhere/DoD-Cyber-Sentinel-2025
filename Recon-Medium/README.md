# Screamin' Streamin' 😱

### Description
We've received intel that Juche Jaguar has exposed a network stream on the host {{IP}} between TCP ports 5000 and 10000. Once you find the port, connect to the correct stream name and report back with a flag.

### Hints
1. The open port uses RTSP. Once the port is found, you will need the correct stream name.
2. You will need to enumerate the stream name through some type of brute forcing. Use tools like `ffprobe` to help find the correct stream.
2. Use ffplayer or VLC to connect to the stream once you have the correct RTSP URI. 

### Answer
After scanning the server for open ports, it is noted that port 8554 is open on TCP. When performing service scans, Nmap responds thinking that it may likely be RTSP. 

Once the port is found, we need to enumerate the valid stream name. This is used by RTSP to select the correct information to give back to the client. A simple python script is in the `./solve` folder to use `ffprobe` to validate the name of the correct stream.

Once the correct stream is found, we can connect to it with either VLC or `ffplay`.

```
ffplay -rtsp_transport tcp rtsp://{{IP}}:8774/stream
```

When the stream connects, we can see a video of a man holding the flag on a piece of paper. The flag is `C1{RTSP_you_found_me}`. 

### References
The streaming from video was using code developed by [flaviostutz](https://github.com/flaviostutz/rtsp-relay?tab=readme-ov-file#tips). Sora was used to generate the video looped for this stream.