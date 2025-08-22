import json

province = input("استان را وارد کنید: ")
city = input("شهر را وارد کنید: ")
ip_range = input("رنج IP (مثلاً 192.168.100.0/24): ")

db = {
    "province": province,
    "city": city,
    "ip_range": ip_range
}

with open("target_location.json", "w", encoding="utf-8") as f:
    json.dump(db, f, indent=4, ensure_ascii=False)

print("فایل target_location.json ساخته شد.")