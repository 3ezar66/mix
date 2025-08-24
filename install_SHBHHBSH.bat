@echo off
title SHBHHBSH - نصب سیستم تشخیص ماینر
color 0A

echo.
echo ========================================
echo    SHBHHBSH - نصب سیستم تشخیص ماینر
echo ========================================
echo.
echo در حال شروع نصب...
echo.

REM بررسی نصب Python
python --version >nul 2>&1
if errorlevel 1 (
    echo خطا: Python نصب نشده یا در PATH نیست
    echo لطفاً Python 3.8+ را نصب کنید و دوباره تلاش کنید
    pause
    exit /b 1
)

echo Python یافت شد!
echo.

REM نصب وابستگی‌ها
echo در حال نصب وابستگی‌های مورد نیاز...
echo.

echo نصب بسته‌های اصلی...
pip install numpy scipy pandas matplotlib
if errorlevel 1 (
    echo خطا در نصب بسته‌های اصلی
    pause
    exit /b 1
)

echo نصب بسته‌های صوتی...
pip install pyaudio librosa sounddevice
if errorlevel 1 (
    echo هشدار: برخی بسته‌های صوتی نصب نشدند
)

echo نصب بسته‌های RF...
pip install rtlsdr python-nmap scapy
if errorlevel 1 (
    echo هشدار: برخی بسته‌های RF نصب نشدند
)

echo نصب بسته‌های سیستم...
pip install psutil GPUtil pyserial
if errorlevel 1 (
    echo هشدار: برخی بسته‌های سیستم نصب نشدند
)

echo نصب بسته‌های تصویری و نقشه...
pip install opencv-python folium geopy requests
if errorlevel 1 (
    echo هشدار: برخی بسته‌های تصویری نصب نشدند
)

echo.
echo ========================================
echo نصب با موفقیت تکمیل شد!
echo ========================================
echo.
echo برای اجرای سیستم:
echo 1. python SHBHHBSH_MAIN.py  (نسخه خط فرمان)
echo 2. python SHBHHBSH_GUI.py   (نسخه گرافیکی)
echo 3. python SHBHHBSH_LAUNCHER.py (راه‌انداز کامل)
echo.
pause