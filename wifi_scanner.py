import subprocess
import re

def scan_wifi():
    result = subprocess.check_output(["sudo", "iwlist", "scan"]).decode("utf-8")
    networks = []
    for block in result.split("Cell ")[1:]:
        mac = re.search(r"Address: ([\\da-fA-F:]{17})", block)
        ssid = re.search(r'ESSID:"(.*)"', block)
        signal = re.search(r"Signal level=(-?\\d+) dBm", block)
        if mac and ssid and signal:
            networks.append({
                "mac": mac.group(1),
                "ssid": ssid.group(1),
                "signal": int(signal.group(1))
            })
    return networks

if __name__ == "__main__":
    nets = scan_wifi()
    for n in nets:
        print(n)