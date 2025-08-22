import requests
import ipaddress
import socket
import sqlite3
import time
from datetime import datetime

# API KEYS (در محیط امن .env نگهداری شود)
ABUSEIPDB_KEY = "your-abuseipdb-key"
PROXYCHECK_KEY = "your-proxycheck-key"
SHODAN_KEY = "your-shodan-key"
IPINFO_KEY = "your-ipinfo-key"

MINER_PORTS = [3333, 4444, 5555, 7777, 8888, 18081, 18082, 18083, 4028, 4233, 8233, 22, 3389, 9999, 3000, 4000, 5000]

# دیتابیس
conn = sqlite3.connect("ip_mining_scan.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS scan_results (
    ip TEXT PRIMARY KEY,
    proxycheck TEXT,
    abuseipdb TEXT,
    shodan TEXT,
    ipinfo TEXT,
    open_ports TEXT,
    latitude REAL,
    longitude REAL,
    city TEXT,
    country TEXT,
    timestamp TEXT
)
''')
conn.commit()

def scan_ports(ip):
    open_ports = []
    for port in MINER_PORTS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.8)
                if s.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
        except:
            pass
    return open_ports

def call_proxycheck(ip):
    url = f"https://proxycheck.io/v2/{ip}?key={PROXYCHECK_KEY}&vpn=1&asn=1"
    try:
        return requests.get(url, timeout=8).json()
    except:
        return {}

def call_abuseipdb(ip):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": ABUSEIPDB_KEY, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": "90"}
    try:
        return requests.get(url, headers=headers, params=params, timeout=8).json()
    except:
        return {}

def call_shodan(ip):
    url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_KEY}"
    try:
        return requests.get(url, timeout=10).json()
    except:
        return {}

def call_ipinfo(ip):
    url = f"https://ipinfo.io/{ip}?token={IPINFO_KEY}"
    try:
        return requests.get(url, timeout=8).json()
    except:
        return {}

def geoip_latlon_city(ipinfo):
    lat, lon, city, country = None, None, None, None
    if "loc" in ipinfo:
        loc = ipinfo["loc"].split(',')
        if len(loc) == 2:
            lat, lon = float(loc[0]), float(loc[1])
    city = ipinfo.get("city")
    country = ipinfo.get("country")
    return lat, lon, city, country

def is_suspect(ip, proxycheck_res, abuseipdb_res):
    proxy = proxycheck_res.get(ip, {}).get("proxy", "no") if ip in proxycheck_res else "no"
    abuse_score = abuseipdb_res.get("data", {}).get("abuseConfidenceScore", 0)
    return proxy == "yes" or (abuse_score and int(abuse_score) > 30)

def save_result(ip, proxycheck_res, abuseipdb_res, shodan_res, ipinfo_res, open_ports, lat, lon, city, country):
    cursor.execute('''
    INSERT OR REPLACE INTO scan_results 
    (ip, proxycheck, abuseipdb, shodan, ipinfo, open_ports, latitude, longitude, city, country, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ip,
        str(proxycheck_res),
        str(abuseipdb_res),
        str(shodan_res),
        str(ipinfo_res),
        ",".join(map(str, open_ports)),
        lat, lon, city, country,
        datetime.utcnow().isoformat()
    ))
    conn.commit()

def generate_html_report():
    cursor.execute("SELECT * FROM scan_results")
    rows = cursor.fetchall()
    with open("miner_report.html", "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>گزارش کشف ماینر</title></head><body>")
        f.write("<h1>Miner Detection Report</h1><table border=1><tr><th>IP</th><th>Open Ports</th><th>City</th><th>Country</th><th>Lat</th><th>Lon</th><th>Timestamp</th></tr>")
        for row in rows:
            f.write(f"<tr><td>{row[0]}</td><td>{row[5]}</td><td>{row[8]}</td><td>{row[9]}</td><td>{row[6]}</td><td>{row[7]}</td><td>{row[10]}</td></tr>")
        f.write("</table>")
        f.write("""
        <h2>نقشه دستگاه‌های کشف‌شده</h2>
        <div id="map" style="height:600px;width:99vw"></div>
        <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
        <script>
        var map = L.map('map').setView([32.0, 53.0], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        """)
        for row in rows:
            if row[6] and row[7]:
                f.write(f"L.marker([{row[6]}, {row[7]}]).addTo(map).bindPopup('IP: {row[0]}<br>City: {row[8]}<br>Country: {row[9]}<br>Ports: {row[5]}');\n")
        f.write("</script></body></html>")

def main():
    ip_range = input("رنج IP (مثال: 192.168.1.1-192.168.1.254): ").strip()
    try:
        start_ip_str, end_ip_str = ip_range.split("-")
        start_ip = ipaddress.IPv4Address(start_ip_str)
        end_ip = ipaddress.IPv4Address(end_ip_str)
        if start_ip > end_ip:
            print("IP شروع بزرگتر از پایان است.")
            return
    except Exception as e:
        print("ورودی نادرست:", e)
        return

    current_ip = start_ip
    while current_ip <= end_ip:
        ip = str(current_ip)
        print(f"\n🔎 {ip} ...")
        proxycheck_res = call_proxycheck(ip)
        abuseipdb_res = call_abuseipdb(ip)
        shodan_res = call_shodan(ip)
        ipinfo_res = call_ipinfo(ip)
        lat, lon, city, country = geoip_latlon_city(ipinfo_res)
        open_ports = []
        if is_suspect(ip, proxycheck_res, abuseipdb_res):
            print(f"⚠️ مشکوک به ماینر، بررسی پورت‌ها ...")
            open_ports = scan_ports(ip)
            print(f"پورت‌های باز: {open_ports if open_ports else 'هیچ'}")
        else:
            print("IP مشکوک نیست.")
        save_result(ip, proxycheck_res, abuseipdb_res, shodan_res, ipinfo_res, open_ports, lat, lon, city, country)
        time.sleep(1)
        if current_ip == end_ip:
            break
        current_ip += 1

    print("\nاسکن پایان یافت. گزارش در miner_report.html")
    generate_html_report()

if __name__ == "__main__":
    main()