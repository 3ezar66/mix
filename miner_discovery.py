import nmap
import scapy.all as scapy

def main_return():
    m = nmap.PortScanner()
    m.scan('192.168.1.0/24', arguments='-p 3333,4444,5555')
    suspects = []
    for host in m.all_hosts():
        for proto in m[host].all_protocols():
            ports = m[host][proto].keys()
            if any(p in [3333, 4444, 5555] for p in ports):
                try:
                    ans, _ = scapy.arping(host, verbose=False, timeout=2)
                    mac = ans[0][1].hwsrc if ans else 'UNKNOWN'
                except Exception:
                    mac = 'UNKNOWN'
                suspects.append({'ip': host, 'mac': mac})
    return suspects

if __name__ == "__main__":
    print("Suspect Miners:", main_return())