import requests
from typing import Optional, Dict

def get_ip_owner_tci(ip: str, api_key: str) -> Optional[Dict]:
    """
    استعلام مالکیت آی‌پی از API رسمی مخابرات ایران (TCI)
    نیازمند کلید دسترسی معتبر
    """
    try:
        url = "https://api.tci.ir/customer/ip-lookup"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'IlamMinerDetection/1.0'
        }
        payload = {
            'ip_address': ip,
            'request_type': 'owner_lookup',
            'requesting_authority': 'ilam_cybersecurity_unit'
        }
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return {
                    'name': data.get('customer_name'),
                    'family': data.get('customer_family'),
                    'phone': data.get('contact_number'),
                    'national_id': data.get('national_id'),
                    'address': data.get('service_address'),
                    'contract_type': data.get('service_type'),
                    'isp': 'مخابرات ایران',
                    'confidence': 0.95,
                    'source': 'tci_official_api'
                }
        return None
    except Exception as e:
        return {"error": str(e)}

# مثال استفاده
if __name__ == "__main__":
    print(get_ip_owner_tci("8.8.8.8", "API_KEY_HERE"))
