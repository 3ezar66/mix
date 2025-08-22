import os
import requests
import sqlite3
import json
from typing import List, Dict, Optional, Any

# لیست تقسیمات کشوری استان ایلام با مختصات هر شهر/بخش (نمونه کامل)
ILAM_DIVISIONS = {
    "ایلام": {
        "مختصات": [33.6386, 46.4227],
        "شهرستان‌ها": {
            "ایلام": [
                {"name": "ایلام", "coords": [33.6386, 46.4227]},
                {"name": "چوار", "coords": [33.6931, 46.2972]},
                {"name": "سیوان", "coords": [33.4967, 46.5631]},
                {"name": "میمه", "coords": [33.7756, 46.1517]}
            ],
            "دهلران": [
                {"name": "دهلران", "coords": [32.6956, 47.2672]},
                {"name": "موسیان", "coords": [32.4622, 47.2192]},
                {"name": "پهله", "coords": [32.3822, 47.3772]},
                {"name": "زرین‌آباد", "coords": [32.7261, 47.4206]}
            ],
            "آبدانان": [
                {"name": "آبدانان", "coords": [32.9931, 47.4192]},
                {"name": "سراب‌باغ", "coords": [32.8572, 47.6011]},
                {"name": "مورموری", "coords": [32.7267, 47.6739]}
            ],
            "دره‌شهر": [
                {"name": "دره‌شهر", "coords": [33.1442, 47.3781]},
                {"name": "ماژین", "coords": [33.0492, 47.5639]},
                {"name": "بدل‌آباد", "coords": [33.2100, 47.5000]}
            ],
            "ملکشاهی": [
                {"name": "ارکواز", "coords": [33.3881, 46.8281]},
                {"name": "دلگشا", "coords": [33.3500, 46.9000]}
            ],
            "مهران": [
                {"name": "مهران", "coords": [33.1222, 46.1642]},
                {"name": "صالح‌آباد", "coords": [33.3833, 46.2333]}
            ],
            "چرداول": [
                {"name": "سرابله", "coords": [33.7631, 46.5631]},
                {"name": "زنگوان", "coords": [33.8000, 46.6000]},
                {"name": "شباب", "coords": [33.9000, 46.7000]}
            ],
            "ایوان": [
                {"name": "ایوان", "coords": [33.8272, 46.3092]},
                {"name": "زرنه", "coords": [33.9000, 46.2000]}
            ]
        }
    }
}

DIVISIONS_FILE = "ilam_divisions.json"
IRAN_JSON_PATH = os.path.join(
    os.path.dirname(__file__),
    '..', '..', '.config', 'iran', 'iran-1.0.2', 'dist', 'iran.json'
)

def load_ilam_divisions():
    """
    تلاش برای بارگذاری تقسیمات کشوری استان ایلام از فایل iran.json (آفلاین)، سپس فایل محلی، سپس مقدار پیش‌فرض
    """
    global ILAM_DIVISIONS
    # تلاش برای بارگذاری از iran.json
    if os.path.exists(IRAN_JSON_PATH):
        try:
            with open(IRAN_JSON_PATH, "r", encoding="utf-8") as f:
                all_cities = json.load(f)
            ilam_cities = [c for c in all_cities if c.get("province_name") == "ایلام"]
            divisions = {"ایلام": {"مختصات": [33.6386, 46.4227], "شهرستان‌ها": {}}}
            for city in ilam_cities:
                county = city.get("county_name")
                city_name = city.get("city_name")
                district = city.get("district_name")
                if not county or not city_name:
                    continue
                if county not in divisions["ایلام"]["شهرستان‌ها"]:
                    divisions["ایلام"]["شهرستان‌ها"][county] = []
                divisions["ایلام"]["شهرستان‌ها"][county].append({
                    "name": city_name,
                    "district": district,
                    "coords": None  # مختصات در این منبع موجود نیست
                })
            ILAM_DIVISIONS = divisions
            print("تقسیمات کشوری استان ایلام از iran.json بارگذاری شد.")
            return
        except Exception as e:
            print(f"خطا در خواندن iran.json: {e}")
    # تلاش برای بارگذاری از فایل محلی
    if os.path.exists(DIVISIONS_FILE):
        try:
            with open(DIVISIONS_FILE, "r", encoding="utf-8") as f:
                ILAM_DIVISIONS = json.load(f)
            print("تقسیمات کشوری از فایل محلی بارگذاری شد.")
            return
        except Exception as e:
            print(f"خطا در خواندن فایل تقسیمات: {e}")
    print("فایل تقسیمات کشوری محلی یا iran.json یافت نشد. استفاده از مقدار پیش‌فرض.")

# منابع رسمی جایگزین
ONLINE_SOURCES = [
    "https://raw.githubusercontent.com/erfanrajabi/iran-geojson/master/ilam.json",
    "https://raw.githubusercontent.com/ghodsizadeh/iran-geojson/master/ilam.json",
    "https://raw.githubusercontent.com/hamidrezakp/iran-geojson/master/ilam.json",
    "https://raw.githubusercontent.com/iranopendata/iran-geojson/master/ilam.json",
    "https://raw.githubusercontent.com/evandhq/iran-geojson/master/ilam.json"
]

def geojson_to_internal_structure(geojson):
    """
    تبدیل داده GeoJSON به ساختار داخلی ILAM_DIVISIONS
    """
    divisions = {"ایلام": {"مختصات": [33.6386, 46.4227], "شهرستان‌ها": {}}}
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        county = props.get("county") or props.get("shahrestan")
        city = props.get("name") or props.get("city")
        coords = None
        # مرکز هندسی چندضلعی به عنوان مختصات شهر/بخش
        if feature.get("geometry") and feature["geometry"]["type"] == "Polygon":
            poly = feature["geometry"]["coordinates"][0]
            lat = sum([p[1] for p in poly]) / len(poly)
            lon = sum([p[0] for p in poly]) / len(poly)
            coords = [lat, lon]
        if county and city:
            if county not in divisions["ایلام"]["شهرستان‌ها"]:
                divisions["ایلام"]["شهرستان‌ها"][county] = []
            divisions["ایلام"]["شهرستان‌ها"][county].append({"name": city, "coords": coords})
    return divisions

def update_ilam_divisions_from_online():
    """
    تلاش برای دریافت تقسیمات کشوری و مختصات از منابع آنلاین رسمی و ذخیره در فایل محلی
    """
    for url in ONLINE_SOURCES:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # اگر GeoJSON بود، تبدیل شود
                if "features" in data:
                    divisions = geojson_to_internal_structure(data)
                else:
                    divisions = data
                with open(DIVISIONS_FILE, "w", encoding="utf-8") as f:
                    json.dump(divisions, f, ensure_ascii=False, indent=2)
                print(f"تقسیمات کشوری و مختصات از {url} ذخیره شد.")
                return  # موفقیت
            else:
                print(f"دریافت داده از {url} ناموفق بود.")
        except Exception as e:
            print(f"خطا در دریافت داده آنلاین از {url}: {e}")
    print("هیچ منبع رسمی آنلاین قابل استفاده نبود.")

def persian_print(text):
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        print(get_display(reshaped))
    except Exception:
        print(text)

def select_geographical_area():
    persian_print("انتخاب منطقه جغرافیایی استان ایلام:")
    persian_print("1. کل استان ایلام")
    counties = list(ILAM_DIVISIONS["ایلام"]["شهرستان‌ها"].keys())
    for idx, county in enumerate(counties, 2):
        try:
            county_en = county.encode('ascii')
        except Exception:
            county_en = None
        label = f"{idx}. شهرستان {county}"
        persian_print(label)
    choice = int(input("شماره مورد نظر را وارد کنید: "))
    if choice == 1:
        return {"name": "ایلام", "coords": ILAM_DIVISIONS["ایلام"]["مختصات"]}
    else:
        county = counties[choice-2]
        cities = ILAM_DIVISIONS["ایلام"]["شهرستان‌ها"][county]
        persian_print(f"شهر/بخش‌های شهرستان {county}:")
        for i, city in enumerate(cities, 1):
            label = f"{i}. {city['name']}"
            persian_print(label)
        city_choice = int(input("شماره شهر/بخش را وارد کنید (یا 0 برای کل شهرستان): "))
        if city_choice == 0:
            return {"name": county, "coords": None}
        else:
            city = cities[city_choice-1]
            return {"name": city["name"], "coords": city["coords"]}

# مثال استفاده از انتخاب منطقه و تنظیم خودکار پارامترها
if __name__ == "__main__":
    load_ilam_divisions()
    update_ilam_divisions_from_online()
    load_ilam_divisions()  # پس از بروزرسانی آنلاین مجدد بارگذاری شود
    area = select_geographical_area()
    print(f"منطقه انتخاب شده: {area['name']}")
