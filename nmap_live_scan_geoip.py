import subprocess
import json
import requests
import webbrowser
import tempfile
import time

# ---- تنظیمات ----
NMAP_PATH = "nmap"  # اگر nmap در PATH نیست، آدرس کامل nmap.exe را بنویسید
MINER_PORTS = "3333,4444,5555,7777,8888,18081,18082,18083,4028,4233,8233"
GEOIP_API = "http://ip-api.com/json/"  # یا از maxmind, ipinfo و ... هم می‌توانید استفاده کنید

def run_nmap(ip_range):
    # اجرای nmap و گرفتن خروجی زنده
    cmd = [
        NMAP_PATH, "-p", MINER_PORTS, "--open", "-T4", "-oG", "-", ip_range
    ]
    print(f"\n[+] Running NMap: {' '.join(cmd)}\n")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    found_hosts = []
    with open("nmap_live_log.txt", "w", encoding="utf-8") as logf:
        for line in iter(proc.stdout.readline, ''):
            print(line, end="")
            logf.write(line)
            # پارس خروجی nmap برای آی‌پی و پورت‌های باز
            if line.startswith("Host:"):
                # مثال خروجی: Host: 192.168.1.5 ()  Ports: 3333/open/tcp//unknown///
                parts = line.split()
                ip = parts[1]
                ports = [x.split("/")[0] for x in line.split("Ports:")[1].split(",") if "/open/" in x]
                found_hosts.append({'ip': ip, 'ports': ports})
    proc.wait()
    return found_hosts

def geoip_lookup(ip):
    try:
        r = requests.get(GEOIP_API + ip, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

def generate_map(found_hosts):
    # ساخت نقشه با leaflet و مارکرها
    map_points = []
    for host in found_hosts:
        info = geoip_lookup(host["ip"])
        lat = info.get("lat")
        lon = info.get("lon")
        city = info.get("city", "Unknown")
        if lat and lon:
            marker = {
                "lat": lat,
                "lon": lon,
                "popup": f"{host['ip']}<br>Ports: {', '.join(host['ports'])}<br>{city}"
            }
            map_points.append(marker)
        time.sleep(0.5)  # برای جلوگیری از محدودیت API

    # ساخت فایل HTML نقشه
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Miner Map</title>
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
      <style> #map {height: 95vh; width: 100vw;} </style>
    </head>
    <body>
      <h2>Detected Miners on Map</h2>
      <div id="map"></div>
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      <script>
        var map = L.map('map').setView([32.0, 53.0], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    """
    for marker in map_points:
        html += f"""
        L.marker([{marker['lat']}, {marker['lon']}]).addTo(map)
          .bindPopup("{marker['popup']}");
        """
    html += """
      </script>
    </body>
    </html>
    """
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as f:
        f.write(html)
        map_path = f.name
    webbrowser.open(map_path)
    print(f"\n[+] Map with detected miners opened: {map_path}")

# ----------- MAIN ------------
if __name__ == "__main__":
    ip_range = input("Enter IP range (e.g. 192.168.1.0/24 or 10.10.10.1-10.10.10.254): ").strip()
    found_hosts = run_nmap(ip_range)
    print("\n[+] NMap scan finished. Found hosts:", found_hosts)
    if found_hosts:
        print("[+] Looking up GeoIP and generating map...")
        generate_map(found_hosts)
    else:
        print("[!] No open miner ports found in this range.")