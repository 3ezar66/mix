import nmap
from typing import List, Dict, Optional
import logging

# اسکنر شبکه واقعی با استفاده از nmap

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.logger = logging.getLogger(__name__)

    def scan_network_nmap(self, network_range: str, ports: str = "22,80,443,3333,5555,7777,8333,18080,4028,3334,3335,3336,3337,3338,3339,4444,5556,6666,8888,9999") -> List[Dict]:
        """
        اسکن شبکه برای شناسایی دستگاه‌های فعال و پورت‌های باز رایج ماینرها
        network_range: محدوده شبکه (مثلاً 192.168.1.0/24)
        ports: لیست پورت‌های رایج ماینینگ
        خروجی: لیست دستگاه‌های شناسایی شده با آی‌پی، مک، پورت باز و ...
        """
        try:
            # اسکن با تنظیمات پیشرفته
            self.nm.scan(
                hosts=network_range,
                ports=ports,
                arguments='-sS -O -sV -T4 --open --max-retries 2'
            )

            devices = []
            for host in self.nm.all_hosts():
                device_info = {
                    "ip": host,
                    "open_ports": [],
                    "mac": None,
                    "device_type": None,
                    "os_match": None,
                    "status": self.nm[host].state()
                }

                # اطلاعات پورت‌های باز
                if self.nm[host].has_tcp():
                    for port in self.nm[host]['tcp']:
                        port_info = self.nm[host]['tcp'][port]
                        if port_info['state'] == 'open':
                            device_info["open_ports"].append({
                                "port": port,
                                "service": port_info['name'],
                                "version": port_info['version'],
                                "product": port_info['product']
                            })

                # اطلاعات MAC و نوع دستگاه
                if 'mac' in self.nm[host]['addresses']:
                    device_info["mac"] = self.nm[host]['addresses']['mac']
                    if 'vendor' in self.nm[host]:
                        device_info["device_type"] = self.nm[host]['vendor'].get(
                            device_info["mac"], "Unknown"
                        )

                # اطلاعات سیستم عامل
                if 'osmatch' in self.nm[host] and len(self.nm[host]['osmatch']) > 0:
                    device_info["os_match"] = {
                        "name": self.nm[host]['osmatch'][0]['name'],
                        "accuracy": self.nm[host]['osmatch'][0]['accuracy']
                    }

                devices.append(device_info)

            return devices

        except Exception as e:
            self.logger.error(f"Error during network scan: {str(e)}")
            return [{"error": str(e)}]

# مثال استفاده
if __name__ == "__main__":
    # تنظیم لاگر
    logging.basicConfig(level=logging.INFO)
    
    # ایجاد نمونه از اسکنر شبکه
    scanner = NetworkScanner()
    
    # محدوده شبکه را بر اساس تقسیمات استان ایلام تنظیم کنید
    network = "192.168.1.0/24"
    
    # اجرای اسکن
    results = scanner.scan_network_nmap(network)
    
    # نمایش نتایج
    for device in results:
        if "error" in device:
            print(f"خطا در اسکن: {device['error']}")
        else:
            print(f"\nدستگاه یافت شده در {device['ip']}:")
            print(f"وضعیت: {device['status']}")
            if device['mac']:
                print(f"آدرس MAC: {device['mac']}")
                print(f"نوع دستگاه: {device['device_type']}")
            if device['os_match']:
                print(f"سیستم عامل: {device['os_match']['name']} (دقت: {device['os_match']['accuracy']}%)")
            if device['open_ports']:
                print("پورت‌های باز:")
                for port in device['open_ports']:
                    print(f"  - پورت {port['port']}: {port['service']} ({port['product']} {port['version']})")
            print("-" * 50)
