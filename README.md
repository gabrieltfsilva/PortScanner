# PortScanner
Port Scanner

Written in python 3. Not tested on legacy versions.\
Tested on Windows 11 and Debian 10.\
\
Usage\
python portscanner.py host -p 80 -v\
host: address to scan.\
\
-h, --help: show help\
-p: ports, [common], all, 80, 20-25\
-v: verbose\
\
Host can be an ip address, a URL, a full range 0/24 or a txt file with a list.\
Ports can be "common", "all", ports "20 21 1433" or ranges "20-25 8000-9000".\
Verbose shows every step.\
