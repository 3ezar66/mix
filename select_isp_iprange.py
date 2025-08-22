import json

with open("iran_isp_ip_ranges.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# انتخاب استان
print("\n📍 استان‌های ایران:")
provinces = list(data.keys())
for i, province in enumerate(provinces, 1):
    print(f"{i}. {province}")
province_choice = int(input("شماره استان: "))
province = provinces[province_choice - 1]

# انتخاب شهر
cities = list(data[province].keys())
print(f"\n🏙️ شهرهای استان {province}:")
for i, city in enumerate(cities, 1):
    print(f"{i}. {city}")
city_choice = int(input("شماره شهر: "))
city = cities[city_choice - 1]

# انتخاب ISP
isps = list(data[province][city].keys())
print(f"\n🌐 ISP های شهر {city}:")
for i, isp in enumerate(isps, 1):
    print(f"{i}. {isp}")
isp_choice = int(input("شماره ISP: "))
isp = isps[isp_choice - 1]

# انتخاب رنج IP
ranges = data[province][city][isp]
print(f"\n🛰️ رنج‌های IP تخصیص یافته {isp} در {city}:")
for i, r in enumerate(ranges, 1):
    print(f"{i}. {r}")
range_choice = int(input("شماره رنج IP: "))
selected_range = ranges[range_choice - 1]

print(f"\n✅ رنج انتخاب شده برای اسکن: {selected_range}")