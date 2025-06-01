# Clear(ed) Text 🔍
## Description
This challenge is designed to test a contestant's ability to review PCAP for sensitive information. Login information sent over plaintext HTTP without encryption threatens most applications and is a realistic threat vector in enterprises. 

## Challenge Story
We have discovered a North Torbian login portal which is not protected by TLS. We've gathered a PCAP of activity, can you determine if a login occurred and what the password might be?

Review the PCAP to find the password that the user logged in with.

Author: m4lwhere

## Evidence
The only item required to complete this challenge is the `login.pcap` file. This has a SHA1 hash of `af1e481dd19f5f19dfb7ec9a39e26647ca5abbfe`.

The `/src` folder is only the Docker container used to host the application that was logged into. It is not required for solving the challenge.

## Hints
1. Open the PCAP with Wireshark and right click the HTTP traffic (highlighted in green) and choose Follow > HTTP Stream.
2. Special characters such as `{}` are URL-encoded. Use tools such as CyberChef to decode them into their values.

## Flag
When reviewing the PCAP, it is noted that there's a POST to login in packet #16. Lookign closer, we can see this packet was sent with the credentials of `username=ironpotatoadmin&password=C1%7Bmaybe_TLS_would_be_nice%7D` in the POST body. 

Decoding the URL encoding for `password` parameter reveals that the flag is `C1{maybe_TLS_would_be_nice}`.