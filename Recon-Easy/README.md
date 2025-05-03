# Hoasted Toasted 🍞
## Description
This challenge tests your ability to identify and access virtual hosted servers using Apache, TLS SAN fields, and host file manipulation.

## Challenge Story
We have discovered what we believe is a North Torbian public website and have suspicions there is a secret internal-only site hidden there as well. Your goal: Figure out how to connect to the hidden site and find the flag!

## Hints
1. Pay attention to the TLS certificate. Are there other hostnames on there?
2. Certain TLDs cannot be resolved. Place the hostname resolution in your hosts file (`/etc/hosts` or `C:\Windows\system32\drivers\etc\hosts`).


## What you need to do
1. **Visit the public site:**
   Go to https://{{site}}/ in your browser. You will see the what is certainly not a North Torbian satirical homepage.
2. **Inspect the TLS certificate:**
   View the certificate's Subject Alternative Name (SAN) field. There is a hostname with a non-routable TLD (e.g., `.torbia-internal`).
3. **Update your hosts file:**
   Add an entry to your `/etc/hosts` (or `C:\Windows\System32\drivers\etc\hosts`) to point the public IPv4 address of the host.
4. **Access the internal site:**
   Visit https://<internal-hostname>/ in your browser. You will see the flag!

## Flag Submission
Paste the flag from the internal site to complete the challenge!

---

*Inspired by the legendary cyber-misadventures of North Torbia.*
