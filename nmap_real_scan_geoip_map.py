import subprocess
import json
import requests
import webbrowser
import tempfile
import time
import re

NMAP_PATH = r"D:\Program Files (x86)\Nmap\nmap.exe"  # مسیر صحیح nmap.exe
MINER_PORTS = "3333,4444,5555,7777,8888,18081,18082,18083,4028,4233,8233"

def run_nmap(ip_range):
    cmd = [
        NMAP_PATH, "-p", MINER_PORTS, "--open", "-T4", "-oG", "-", ip_range
    ]
    print(f"\n[+] Running NMap: {' '.join(cmd)}\n")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    found_hosts = []
    with open("nmap_live_log.txt", "w", encoding="utf-8") as logf:
        for line in iter(proc.stdout.readline, ''):
            print(line, end="")
            logf.write(line)
            if line.startswith("Host:"):
                ip = re.search(r"Host: (\d+\.\d+\.\d+\.\d+)", line)
                ports = []
                if "Ports:" in line:
                    ports = [x.split("/")[0] for x in line.split("Ports:")[1].split(",") if "/open/" in x]
                if ip and ports:
                    found_hosts.append({"ip": ip.group(1), "ports": ports})
    proc.wait()
    return found_hosts

# ... (بقیه کد بدون تغییر)
