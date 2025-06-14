# Decryption Conniption 😤🔓😤 

### Description
Uh oh! Our HR team made an oopsie-whoopsie and appears to have hired a North Torbian Python Developer. We know this person was given access to our proprietary code, can you find out if they were able to steal any of it?

Thankfully, we always keep a copy of all network traffic and set the SSLKEYLOGFILE for our employees. Use the Memory Dump and PCAP to find if the source code was stolen. There's a flag inside of that code, if it's stolen we need to know!

Evidence is stored in Google Drive.

Author: m4lwhere

### Hints
1. Check which protocols are used in the capture. Are there any that might indicate remote activity through VNC? 
2. The attacker encrypted the source code with a password in a 7z file, then uploaded it to a file sharing website. You will need to extract the SSLKEYLOGFILE within the memory capture to carve out the file transferred, then decrypt the PCAP to grab the file, then open the 7z file with the password.
3. Carve out the information from the notepad.exe process using the notepad plugin here: https://github.com/spitfirerxf/vol3-plugins to get access to the SSLKEYLOGFILE in memory. Then, decrypt the TLS flows in the PCAP to extract the file upload website gofile[.]io. Decrypt the 7z file with the password entered via plaintext VNC within the PCAP.


### Design
This challenge is designed to have contestants perform a variety of forensic tasks across multiple mediums in order to gather the flag. Contestants will need to carve the SSLKEYLOGFILE from the memory dump, apply it to the PCAP, extract an encrypted ZIP from the TLS stream, and then review the (unencrypted) VNC stream to see the keystrokes used to encrypt the ZIP file. 

This is a Windows 10 VM which has the SSLKEYLOGFILE environment variable set to keep track of all TLS session keys. There's a few moving parts to this:
1. Set up the Windows 10 VM with the SSLKEYLOGFILE variable
2. Set up TightVNCServer on the VM to allow plaintext connections
3. Capture PCAP on the 
4. Dump the memory on the VM

### Solving
To solve this challenge, we first must download both pieces of evidence. When reviewing the PCAP, we can see that there's a VNC session in plaintext. Let's start by looking at the PCAP first.

#### Opening in Wireshark
Double click to open the file, now we want to check which protocols are in the capture. This lets us quickly identify which interesting areas could be used to start. Within this information, we can see that "Virtual Network Computing" is listed in this capture. This indicates that VNC is in use, and we might be able to peek at what is happening.

We additionally see that TLS and QUIC are in use in the PCAP as well. There's DNS requests for many subdomains of `gofile[.]io`, which is an anonymous file hosting service. There is a potential that the attacker uploaded files here to exfil them, but the traffic was encrypted via TLS so we don't know for sure. Let's see what might be in the VNC activity, since there is a chance it is not encrypted.

When looking at only the VNC traffic, we can see there's some entries for a `Key Event`, and looking closer shows that there is a `key` value within it. This appears to be keys pressed by the user when within the interactive VNC session.

```
vnc.client_message_type == 4
```

We can use `tshark` to try and pull this data out. THis helps automate this process, making it much less painful to do by hand.

```
$ tshark -r ./evidence.pcapng -Y 'vnc.client_message_type == 4' -T fields -e vnc.key
0x00000074
0x00000074
0x00000068
0x00000068
0x00000033
0x00000033
0x0000ffe1
0x0000005f
0x0000005f
```

Adding more into our one-liner to decode this hex, we can see some interesting values being provided so far. But this still seems off, so let's continue to dig into it a bit more:

```
$ tshark -r ./evidence.pcapng -Y 'vnc.client_message_type == 4' -T fields -e vnc.key | gawk -F'x' '{ printf "%c", strtonum("0x"$2) } END{ print "" }'
tthh33￡__￡iirr00nn￡__￡ppoottaatt00￡__￡gguuiidd33ss￡__￡uuss￡<<￡33ggoo－－
```

Looking closer at the packets, it seems like there are at least two packets per letter. This is because of the "Key Down" flag in the VNC protocol. With this knowledge, let's isolate only the packets with the keydown within our filter.

```
vnc.client_message_type == 4 && vnc.key_down == 1
```
This gives us some much more promising data so far! The only other outstanding thing is the strange `￡` symbol. 

```
$ tshark -r ./evidence.pcapng -Y 'vnc.client_message_type == 4 && vnc.key_down == 1' -T fields -e vnc.key | awk -F'x' '{ printf "%c", strtonum("0x"$2) } END{ print "" }'
th3￡_ir0n￡_potat0￡_guid3s￡_us￡<3go－
```
Looking closer in the PCAP, these are associated with the Left Shift key. Because of this, we can feel confident to remove them from the string we recovered. Additionally, the `go－` can be removed, as this appears to be associated with reaching the `gofile[.]io` website. We can tell this because of the relative delay between these keystrokes, almost 22 seconds where the password characters were less than a second delta between each.

Looks like the password we might use is:
```
th3_ir0n_potat0_guid3s_us<3
```
Cool!

#### NetworkMiner
Tools like NetworkMiner are great at analyzing PCAPs much more in depth as well. Another cool and less known capability is that NetworkMiner can parse application level information from VNC. This means that things like keystrokes can be reviewed. 

But first, the open source version of NetworkMiner only supports PCAP and not PCAPNG files. We'll need to save a copy of the capture from within Wireshark as PCAP first. In Wireshark, click File > Save As > then change the type from PCAPNG to just PCAP.

After opening the capture in NetworkMiner, click on the Parameters tab and we can see that there's information entered within the `Key pressed` Parameter names. This looks suspiciously close to a password! And great news too, this matches the password we carved out with `tshark` as well.

#### Memory Analysis
But we need the file first, which was transferred over enrypted protocols. The challenge description called out the `SSLKEYLOGFILE` variable, let's see if we can find that file.

```sh
$ strings memory.raw | grep 'SSLKEYLOGFILE'
SSLKEYLOGFILE=C:\Users\c1\keylog.log
SSLKEYLOGFILEG                      
SSLKEYLOGFILE/                      
SSLKEYLOGFILE=C:\Users\c1\keylog.log
```
We can see lots of references to the file being stored at `C:\Users\c1\keylog.log`, but we only have a memory capture and not the disk itself. Let's pivot to see if we can dump files from the memory image using Volatility. 

#### Installing Volatility 3
We must first ensure that we have the correct memory analysis tools installed. The defacto industry standard is Volatility 3. Please note that Volatility 2 has been last updated in Dec 2020 (read: it's old and shouldn't be used anymore). 

To install volatility, use `pip` or `pipx` (I prefer `pipx` because the Python virtual environments are automatically managed on your behalf).

```sh
pipx install volatility3
```

Now we can start to parse the memory itself. Let's start with something simple to try and make sure we can read it properly with a simple `windows.info` plugin. One of the cool parts about Volatility 3 is that we no longer need to supply the profile manually, as it will detect and download the correct symbols file automatically 💅

```sh
$ vol -f ./memory.raw windows.info
Volatility 3 Framework 2.11.0
Progress:  100.00               PDB scanning finished                        
Variable        Value

Kernel Base     0xf8020be00000
DTB     0x1ad000
Symbols file:///home/chris/.local/share/pipx/venvs/volatility3/lib/python3.12/site-packages/volatility3/symbols/windows/ntkrnlmp.pdb/66BCC5C6B532F63C8AB733951BA869B4-1.json.xz
Is64Bit True
IsPAE   False
layer_name      0 WindowsIntel32e
memory_layer    1 FileLayer
KdVersionBlock  0xf8020ca0f3f0
Major/Minor     15.19041
MachineType     34404
KeNumberProcessors      2
SystemTime      2025-05-16 02:22:35+00:00
NtSystemRoot    C:\Windows
NtProductType   NtProductWinNt
NtMajorVersion  10
NtMinorVersion  0
PE MajorOperatingSystemVersion  10
PE MinorOperatingSystemVersion  0
PE Machine      34404
PE TimeDateStamp        Tue Oct  4 17:06:37 2016
```
Uh oh! Based on some of the errors given, it seems like Volatility is having trouble running some plugins. Let's increase the verbosity to troubleshoot this problem:

```sh
vol -f ./memory.raw windows.hashdump -vv
```

Looking at this output, it says it can't find a library to import. Let's check if there are any GitHub issues about this or not:
https://github.com/volatilityfoundation/volatility3/issues/493
https://github.com/volatilityfoundation/volatility3/issues/687

Ok! Since we've installed this through `pipx`, we need to make sure we install the correct libraries in the correct virtual environment. Let's first find where `vol` was installed with the `which vol` command, it will likely be in `~/.local/share/pipx/venvs/volatility3/bin`:
```sh
chris@chris-GE65-Linux:~/.local/share/pipx/venvs/volatility3/bin$ which vol
/home/chris/.local/share/pipx/venvs/volatility3/bin/vol
```
Great! Now let's drop into that directory and see what else is in there. We want to enter the correct Python Virtual Env to make sure we're placing the new libaries in a place where the `pipx` installation for `vol` can read it. 

```sh
~$ cd ~/.local/share/pipx/venvs/volatility3/bin

~/.local/share/pipx/venvs/volatility3/bin$ ll
total 40
drwxrwxr-x 2 chris chris 4096 May 10 08:35 ./
drwxrwxr-x 5 chris chris 4096 May 10 08:35 ../
-rw-r--r-- 1 chris chris 2096 May 10 08:35 activate
-rw-r--r-- 1 chris chris  957 May 10 08:35 activate.csh
-rw-r--r-- 1 chris chris 2232 May 10 08:35 activate.fish
-rw-r--r-- 1 chris chris 9033 May 10 08:35 Activate.ps1
lrwxrwxrwx 1 chris chris    7 May 10 08:35 python -> python3*
lrwxrwxrwx 1 chris chris   16 May 10 08:35 python3 -> /usr/bin/python3*
lrwxrwxrwx 1 chris chris    7 May 10 08:35 python3.12 -> python3* 
-rwxrwxr-x 1 chris chris  256 May 10 08:35 vol*
-rwxrwxr-x 1 chris chris  265 May 10 08:35 volshell*
```

Great! Now we can see a few files labeled `activate`. These are the files we want to import into our shell to make sure we update the correct libraries. Let's complete this with `source ./activate` and your prompt should now change to reflect the venv we've entered:

```sh
~/.local/share/pipx/venvs/volatility3/bin$ source ./activate

(volatility3) ~/.local/share/pipx/venvs/volatility3/bin$
```

Now that we're in the correct venv, when we update libraries we know that it will place them in a location that the `vol` installation will be able to reach. Let's add the following libraries via `pip` within our venv. Remember, if we don't see the `(volatility3)` in our prompt we're not in the venv!

```sh
python -m pip install yara-python pycryptodome capstone
```

You should see some status bars and update progress in this window. Once completed, we should be able to use these plugins properly within `vol` now 🎉

If not, then increase the verbosity on the logging and troubleshoot!

#### Parsing Memory
Let's take a peek at the running processes:

```sh
$ vol -f ./memory.raw windows.pslist
Volatility 3 Framework 2.11.0
Progress:  100.00               PDB scanning finished                        
PID     PPID    ImageFileName   Offset(V)       Threads Handles SessionId       Wow64   CreateTime      ExitTime        File output

4       0       System  0x8b0f86e62040  102     -       N/A     False   2025-05-16 00:34:33.000000 UTC  N/A     Disabled
92      4       Registry        0x8b0f86f0c080  4       -       N/A     False   2025-05-16 00:34:26.000000 UTC  N/A     Disabled
304     4       smss.exe        0x8b0f87f93040  2       -       N/A     False   2025-05-16 00:34:33.000000 UTC  N/A     Disabled
420     412     csrss.exe       0x8b0f8a4d3080  11      -       0       False   2025-05-16 00:34:35.000000 UTC  N/A     Disabled
496     412     wininit.exe     0x8b0f8a58b080  1       -       0       False   2025-05-16 00:34:35.000000 UTC  N/A     Disabled
516     488     csrss.exe       0x8b0f8a510080  12      -       1       False   2025-05-16 00:34:35.000000 UTC  N/A     Disabled
596     488     winlogon.exe    0x8b0f8a5d6080  6       -       1       False   2025-05-16 00:34:35.000000 UTC  N/A     Disabled
636     496     services.exe    0x8b0f8a5ef0c0  6       -       0       False   2025-05-16 00:34:35.000000 UTC  N/A     Disabled
660     496     lsass.exe       0x8b0f8a5f0080  9       -       0       False   2025-05-16 00:34:35.000000 UTC  N/A     Disabled
756     496     fontdrvhost.ex  0x8b0f874be0c0  5       -       0       False   2025-05-16 00:34:35.000000 UTC  N/A     Disabled
[...truncated for brevity...]
6480    512     msedge.exe      0x8b0f8c16a080  16      -       1       False   2025-05-16 02:21:29.000000 UTC  N/A     Disabled
2940    512     msedge.exe      0x8b0f8ceef080  8       -       1       False   2025-05-16 02:21:29.000000 UTC  N/A     Disabled
3620    3400    notepad.exe     0x8b0f8cfa4080  6       -       1       False   2025-05-16 02:21:47.000000 UTC  N/A     Disabled
1968    3400    notepad.exe     0x8b0f8c23c080  6       -       1       False   2025-05-16 02:21:57.000000 UTC  N/A     Disabled
```
Interesting to see that `notepad.exe` is listed as open in two processes. Let's see what else we can find with information within Volatility, we'll start by seeing if we can find the finr information within the dump itself with the `windows.filescan` plugin.

```sh
$ vol -f ./memory.raw windows.filescan | grep -i 'keylog.log'
0x8b0f8d95b880.0\Users\c1\keylog.log
0x8b0f8e42cb20  \Users\c1\keylog.log
```

Great! It looks like there are two files here we can try to carve out, but we don't seem to have much luck. Let's peek closer at the notepad processes. We can try to parse out the information from Notepad with the following Volatility module:

- https://github.com/spitfirerxf/vol3-plugins

Specifically, we want to use the `notepad.py` module to try and read into the `notepad.exe` process further. Remember, this needs to be placed into the correct folder within the `pipx` managed installation path. In my case, it was at `~/.local/share/pipx/venvs/volatility3/lib/python3.12/site-packages/volatility3/plugins/windows`. The `notepad.py` should be placed into this directory in order to be accessed by Volatility properly.

> [!IMPORTANT]  
> The latest version of Volatility 3 (v2.26.0) has a breaking change which will prevent this plugin from working properly. Either downgrade to an earlier version of Volatility 3 (such as v2.11.0). This challenge was developed before the feature parity release of Volatility 3 became available. However, this does not prevent the challenge from being sovleable! 

```
~/.local/share/pipx/venvs/volatility3/lib/python3.12/site-packages/volatility3/plugins/windows$ ll
total 32
drwxrwxr-x 4 chris chris 4096 May 11 22:13 ./
drwxrwxr-x 6 chris chris 4096 May 10 08:35 ../
-rw-rw-r-- 1 chris chris  981 May 10 08:35 __init__.py
-rw-rw-r-- 1 chris chris 4697 May 11 22:13 notepad.py
drwxrwxr-x 2 chris chris 4096 May 11 22:13 __pycache__/
drwxrwxr-x 3 chris chris 4096 May 10 08:35 registry/
-rw-rw-r-- 1 chris chris 3859 May 10 08:35 statistics.py
```

Adding the `--dump` switch will place the notepad content into files for us :)

```
vol -f ./memory.raw windows.notepad --dump
```

This gives us a big blob of information, we'll need to add newlines to the secrets to make sure its parsed properly by Wireshark. First, let's isolate to the things we care about, namely the entries on the SSLKEYLOGFILE itself. There's a ton of extra info in these files we don't care about and should remove. The ones we care about include the `CLIENT_RANDOM`, `EXPORTER_SECRET`, and many more. 

Once these are isolated, let's add them all to newlines to ensure we have it in the correct format.
```
sed -E 's/\s([A-Z])/\n\1/g' ./pid.1968.notepad.dmp > keylog.maybe
```
This should have about 368 entries, similar to the following format now:
```
CLIENT_HANDSHAKE_TRAFFIC_SECRET 5477a54d90619c882bd7573f4e35c5c6412b18e0bd8f7f0e734f847317df3081 be7e9aee9c26b3c6273ffe75f4d8e37006b1c131d688b341c6ce0a4799a65b09c51ccef2d2ea43b4d90a9e26835859ce
SERVER_HANDSHAKE_TRAFFIC_SECRET 5477a54d90619c882bd7573f4e35c5c6412b18e0bd8f7f0e734f847317df3081 e1ac1496979cf9498dc45a96f00b086b6fc1725c0ea02ca14351a0543674c851089eca412b7f60fcdf8ff5652306bff3
CLIENT_RANDOM d06a6cb6814009293cf1781678c1a562de3f78e79a4efd2f036633375b7af283 7abcdd469d5fe07a9d94fc37e5ad8706a2f7444e94534dbe9110a3c74e416f69fb9e5690e158b5f77459d9ba75ca6ccb
CLIENT_TRAFFIC_SECRET_0 5477a54d90619c882bd7573f4e35c5c6412b18e0bd8f7f0e734f847317df3081 b085dbce1369eae00ccd8f651daaacdff67d89855f650e469c56ae29f97812e25b7b0d2318b14ef996c9e57ca4945873
SERVER_TRAFFIC_SECRET_0 5477a54d90619c882bd7573f4e35c5c6412b18e0bd8f7f0e734f847317df3081 4b617636ac502220ad8d1f6c9cd296e0ef7cc39d4e7071ee81ecea92e5c0505bc92bfe7965cb8a82b0aa424275886760
EXPORTER_SECRET 5477a54d90619c882bd7573f4e35c5c6412b18e0bd8f7f0e734f847317df3081 0a65b0855db875a84f5e4898434ed0b1e2ff7bc0c924fafbe908ee88d5a4d3b5136c4c3f48b6d987ac4b543b25fa0e2c
```
#### Strings Works Too
A much less elegant solution is to just search for strings as well. We can look up specific pieces that we know are going to be in the SSLKEYLOGFILE based on some research. One such item inside of there is the string `CLIENT_RANDOM`. When piping `strings` into `grep` for this, we can see there are a few hits. 

```sh
strings ./memory.raw | grep -i 'CLIENT_RANDOM'
```

But note that there is much more than only the `CLIENT_RANDOM` field, so we need to try and extract the entire file. To find out which fields are required, we can set the SSLKEYLOGFILE on a test machine we have. This is a good way to troubleshoot and understand what we might be looking for!

Let's do this by dumping all strings in the memory capture, then finding it based on the line, then extracting only the related keylog files.

> [!IMPORTANT]  
> By default, strings will only search for 8-bit characters and will not properly interpret 16-bit strings. In order to effectively carve out the secrets in memory, we must use the -el switch!

```sh
strings -n 16 -el ./memory.raw | grep -E 'CLIENT_HANDSHAKE|SERVER_HANDSHAKE|CLIENT_TRAFFIC|SERVER_TRAFFIC|EXPORTER_SECRET|CLIENT_RANDOM' >> ../Answers/keylog.log
```

If this ran properly, there should be a significant amount of lines in this file, well over 1,800. Now 

#### Decrypting Streams
Great! Now let's try to see if we can decrypt the TLS steams in the PCAP. Load up Wireshark, then place these into the Edit > Preferences > TLS section as the SSL Keylog file. Once this is added, then click OK, Wireshark will attempt to decrypt TLS streams with this data.

Now that we have these loaded up, we can search for interesting HTTP methods. Since this is focused on exfil, let's check for POST activity with the following filter:
```
http2.header.value == "POST"
```
And we can see that there's a suspicious set of outbound activity. Alternatively, and probably easier, we can search for exportable objects within Wireshark's Export Objects > HTTP interface. This will also let us see the hostnames involved.

We can see that packet 8181 was for the host `upload.gofile[.]io` and with the filename of `uploadfile`. Click on that save button to get a copy of it carved out!

After this, open up the `uploadfile` that we carved out and remove the HTTP metadata. This is because the file extracted through the Wireshark interface has the form boundaries in the POST data. Removing those allows us to focus on the file itself, which appears to be a 7z file. Remvoe the leading and trailing webform boundaries from this file.

Now with only the 7z file isolated, let's run the `file` command to make sure it makes sense. 

```
$ file uploadfile
uploadfile: 7-zip archive data, version 0.4
```

Awesome, this is a good sign so far. Now, let's see if we can open it! For Windows, we can place the `.7z` extension at the end of the file which allows 7zip to open it easily.

It's definitely password protected, and this password is not worth attempting a brute force. Instead, let's peek back at the PCAP to see what else might be there. Looking back at the data we carved out of the VNC protocol, it looks suspiciously close to a password. Let's give that one a try:

```
th3_ir0n_potat0_guid3s_us<3
```
And this password was accepted! Looking at line 20 of the source code shows our flag!

```
# --- Global Constants of Dubious Value ---
QUANTUM_ENTANGLEMENT_THRESHOLD = 0.42 # Anything less is just classical confusion
DIMENSIONAL_SHIFT_PROBABILITY = 0.0001 # Don't worry about it. Or do. We're not sure.
OPTIMAL_TEA_TEMPERATURE_CELSIUS = 98.6 # Crucial for cognitive alignment during refinement
MACRODATA_INGESTION_BUFFER_SIZE_PARSEC = 1.5e-17 # It's bigger on the inside
SECRET_PROJECT_CHIMERA_FLAG = "C1{the_ir0n_p0tat0_checks_r3ferences}"
# ⬆️⬆️⬆️ This is the flag, congrats! ⬆️⬆️⬆️
```



#### Decrypted Strings
The payload is in packet 8181.

### Notes
This challenge was heavily inspired by recent North Korean IT Worker intelligence. 

### To Make it Harder 
We can add the file as an ADS? Or should we append the ZIP file to the end of a PNG?

### Tools
Wireshark, NetworkMiner, Volatility

### References
https://blog.knowbe4.com/how-a-north-korean-fake-it-worker-tried-to-infiltrate-us
https://www.tightvnc.com/download.php

