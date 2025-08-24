#!/bin/bash

echo "========================================"
echo "   SHBHHBSH - نصب سیستم تشخیص ماینر"
echo "========================================"
echo ""
echo "در حال شروع نصب..."
echo ""

# بررسی نصب Python
if ! command -v python3 &> /dev/null; then
    echo "خطا: Python3 نصب نشده"
    echo "لطفاً Python 3.8+ را نصب کنید و دوباره تلاش کنید"
    exit 1
fi

echo "Python3 یافت شد!"
echo ""

# نصب وابستگی‌ها
echo "در حال نصب وابستگی‌های مورد نیاز..."
echo ""

echo "نصب بسته‌های اصلی..."
pip3 install numpy scipy pandas matplotlib
if [ $? -ne 0 ]; then
    echo "خطا در نصب بسته‌های اصلی"
    exit 1
fi

echo "نصب بسته‌های صوتی..."
pip3 install pyaudio librosa sounddevice
if [ $? -ne 0 ]; then
    echo "هشدار: برخی بسته‌های صوتی نصب نشدند"
fi

echo "نصب بسته‌های RF..."
pip3 install rtlsdr python-nmap scapy
if [ $? -ne 0 ]; then
    echo "هشدار: برخی بسته‌های RF نصب نشدند"
fi

echo "نصب بسته‌های سیستم..."
pip3 install psutil GPUtil pyserial
if [ $? -ne 0 ]; then
    echo "هشدار: برخی بسته‌های سیستم نصب نشدند"
fi

echo "نصب بسته‌های تصویری و نقشه..."
pip3 install opencv-python folium geopy requests
if [ $? -ne 0 ]; then
    echo "هشدار: برخی بسته‌های تصویری نصب نشدند"
fi

echo ""
echo "========================================"
echo "نصب با موفقیت تکمیل شد!"
echo "========================================"
echo ""
echo "برای اجرای سیستم:"
echo "1. python3 SHBHHBSH_MAIN.py  (نسخه خط فرمان)"
echo "2. python3 SHBHHBSH_GUI.py   (نسخه گرافیکی)"
echo "3. python3 SHBHHBSH_LAUNCHER.py (راه‌انداز کامل)"
echo ""