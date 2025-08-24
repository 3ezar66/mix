@echo off
title SHBHHBSH - نصب سیستم تشخیص ماینر واقعی
color 0A

echo.
echo ========================================
echo    SHBHHBSH - سیستم تشخیص ماینر واقعی
echo ========================================
echo.
echo در حال شروع نصب...
echo.

REM بررسی وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo خطا: Python یافت نشد!
    echo لطفا Python 3.8+ را نصب کنید
    pause
    exit /b 1
)

echo Python یافت شد. در حال نصب وابستگی‌ها...
echo.

REM نصب کتابخانه‌های اصلی
echo نصب کتابخانه‌های اصلی...
pip install numpy scipy pandas matplotlib
if errorlevel 1 (
    echo خطا در نصب کتابخانه‌های اصلی
    pause
    exit /b 1
)

REM نصب کتابخانه‌های اسکن صوتی واقعی
echo نصب کتابخانه‌های اسکن صوتی واقعی...
pip install pyaudio librosa sounddevice
if errorlevel 1 (
    echo هشدار: برخی کتابخانه‌های صوتی نصب نشدند
)

REM نصب کتابخانه‌های اسکن RF واقعی
echo نصب کتابخانه‌های اسکن RF واقعی...
pip install rtlsdr
if errorlevel 1 (
    echo هشدار: RTL-SDR نصب نشد
)
pip install hackrf uhd sdrplay
if errorlevel 1 (
    echo هشدار: برخی کتابخانه‌های RF نصب نشدند
)

REM نصب کتابخانه‌های اسکن حرارتی واقعی
echo نصب کتابخانه‌های اسکن حرارتی واقعی...
pip install opencv-python
if errorlevel 1 (
    echo خطا در نصب OpenCV
    pause
    exit /b 1
)
pip install flirpy seekcamera
if errorlevel 1 (
    echo هشدار: برخی کتابخانه‌های حرارتی نصب نشدند
)

REM نصب کتابخانه‌های اسکن برق واقعی
echo نصب کتابخانه‌های اسکن برق واقعی...
pip install python-kasa pyserial
if errorlevel 1 (
    echo هشدار: برخی کتابخانه‌های برق نصب نشدند
)
pip install wmi
if errorlevel 1 (
    echo هشدار: WMI نصب نشد (فقط Windows)
)

REM نصب کتابخانه‌های اسکن شبکه واقعی
echo نصب کتابخانه‌های اسکن شبکه واقعی...
pip install python-nmap scapy psutil GPUtil
if errorlevel 1 (
    echo خطا در نصب کتابخانه‌های شبکه
    pause
    exit /b 1
)

REM نصب کتابخانه‌های نقشه و موقعیت‌یابی
echo نصب کتابخانه‌های نقشه و موقعیت‌یابی...
pip install folium geopy requests
if errorlevel 1 (
    echo خطا در نصب کتابخانه‌های نقشه
    pause
    exit /b 1
)

REM نصب کتابخانه‌های رابط کاربری
echo نصب کتابخانه‌های رابط کاربری...
pip install tkinter-tooltip Pillow
if errorlevel 1 (
    echo هشدار: برخی کتابخانه‌های رابط کاربری نصب نشدند
)

REM نصب کتابخانه‌های پردازش سیگنال پیشرفته
echo نصب کتابخانه‌های پردازش سیگنال پیشرفته...
pip install scikit-learn scikit-image
if errorlevel 1 (
    echo هشدار: برخی کتابخانه‌های پردازش سیگنال نصب نشدند
)

REM نصب کتابخانه‌های مدیریت سیستم
echo نصب کتابخانه‌های مدیریت سیستم...
pip install python-dateutil configparser colorlog
if errorlevel 1 (
    echo هشدار: برخی کتابخانه‌های مدیریت سیستم نصب نشدند
)

REM نصب کتابخانه‌های پردازش موازی
echo نصب کتابخانه‌های پردازش موازی...
pip install concurrent-futures
if errorlevel 1 (
    echo هشدار: concurrent-futures نصب نشد
)

REM نصب کتابخانه‌های امنیت
echo نصب کتابخانه‌های امنیت...
pip install cryptography
if errorlevel 1 (
    echo هشدار: cryptography نصب نشد
)

REM نصب رابط‌های سخت‌افزاری اضافی
echo نصب رابط‌های سخت‌افزاری اضافی...
pip install pyusb hidapi pyserial-asyncio
if errorlevel 1 (
    echo هشدار: برخی رابط‌های سخت‌افزاری نصب نشدند
)

REM نصب کتابخانه‌های پردازش تصویر پیشرفته
echo نصب کتابخانه‌های پردازش تصویر پیشرفته...
pip install imageio imageio-ffmpeg
if errorlevel 1 (
    echo هشدار: برخی کتابخانه‌های پردازش تصویر نصب نشدند
)

REM نصب رابط‌های شبکه پیشرفته
echo نصب رابط‌های شبکه پیشرفته...
pip install aiohttp websockets
if errorlevel 1 (
    echo هشدار: برخی رابط‌های شبکه نصب نشدند
)

echo.
echo ========================================
echo    نصب وابستگی‌ها تکمیل شد!
echo ========================================
echo.
echo نکات مهم:
echo 1. برای اسکن RF واقعی: RTL-SDR یا HackRF نصب کنید
echo 2. برای اسکن حرارتی واقعی: FLIR یا Seek Thermal نصب کنید
echo 3. برای اسکن برق واقعی: Smart Plug یا Power Meter نصب کنید
echo 4. برای اسکن صوتی واقعی: میکروفون با کیفیت بالا نصب کنید
echo.
echo در حال راه‌اندازی سیستم...
echo.

REM اجرای سیستم
python SHBHHBSH_LAUNCHER.py

if errorlevel 1 (
    echo.
    echo خطا در راه‌اندازی سیستم
    echo لطفا فایل‌های پروژه را بررسی کنید
    pause
    exit /b 1
)

echo.
echo سیستم با موفقیت راه‌اندازی شد!
pause