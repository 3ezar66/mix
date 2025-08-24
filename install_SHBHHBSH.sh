#!/bin/bash

echo "========================================"
echo "   SHBHHBSH - نصب سیستم تشخیص ماینر واقعی"
echo "========================================"
echo ""
echo "در حال شروع نصب..."
echo ""

# بررسی وجود Python3
if ! command -v python3 &> /dev/null; then
    echo "خطا: Python3 یافت نشد!"
    echo "لطفا Python 3.8+ را نصب کنید"
    exit 1
fi

echo "Python3 یافت شد. در حال نصب وابستگی‌ها..."
echo ""

# نصب کتابخانه‌های اصلی
echo "نصب کتابخانه‌های اصلی..."
pip3 install numpy scipy pandas matplotlib
if [ $? -ne 0 ]; then
    echo "خطا در نصب کتابخانه‌های اصلی"
    exit 1
fi

# نصب کتابخانه‌های اسکن صوتی واقعی
echo "نصب کتابخانه‌های اسکن صوتی واقعی..."
pip3 install pyaudio librosa sounddevice
if [ $? -ne 0 ]; then
    echo "هشدار: برخی کتابخانه‌های صوتی نصب نشدند"
fi

# نصب کتابخانه‌های اسکن RF واقعی
echo "نصب کتابخانه‌های اسکن RF واقعی..."
pip3 install rtlsdr
if [ $? -ne 0 ]; then
    echo "هشدار: RTL-SDR نصب نشد"
fi
pip3 install hackrf uhd sdrplay
if [ $? -ne 0 ]; then
    echo "هشدار: برخی کتابخانه‌های RF نصب نشدند"
fi

# نصب کتابخانه‌های اسکن حرارتی واقعی
echo "نصب کتابخانه‌های اسکن حرارتی واقعی..."
pip3 install opencv-python
if [ $? -ne 0 ]; then
    echo "خطا در نصب OpenCV"
    exit 1
fi
pip3 install flirpy seekcamera
if [ $? -ne 0 ]; then
    echo "هشدار: برخی کتابخانه‌های حرارتی نصب نشدند"
fi

# نصب کتابخانه‌های اسکن برق واقعی
echo "نصب کتابخانه‌های اسکن برق واقعی..."
pip3 install python-kasa pyserial
if [ $? -ne 0 ]; then
    echo "هشدار: برخی کتابخانه‌های برق نصب نشدند"
fi

# نصب کتابخانه‌های اسکن شبکه واقعی
echo "نصب کتابخانه‌های اسکن شبکه واقعی..."
pip3 install python-nmap scapy psutil GPUtil
if [ $? -ne 0 ]; then
    echo "خطا در نصب کتابخانه‌های شبکه"
    exit 1
fi

# نصب کتابخانه‌های نقشه و موقعیت‌یابی
echo "نصب کتابخانه‌های نقشه و موقعیت‌یابی..."
pip3 install folium geopy requests
if [ $? -ne 0 ]; then
    echo "خطا در نصب کتابخانه‌های نقشه"
    exit 1
fi

# نصب کتابخانه‌های رابط کاربری
echo "نصب کتابخانه‌های رابط کاربری..."
pip3 install tkinter-tooltip Pillow
if [ $? -ne 0 ]; then
    echo "هشدار: برخی کتابخانه‌های رابط کاربری نصب نشدند"
fi

# نصب کتابخانه‌های پردازش سیگنال پیشرفته
echo "نصب کتابخانه‌های پردازش سیگنال پیشرفته..."
pip3 install scikit-learn scikit-image
if [ $? -ne 0 ]; then
    echo "هشدار: برخی کتابخانه‌های پردازش سیگنال نصب نشدند"
fi

# نصب کتابخانه‌های مدیریت سیستم
echo "نصب کتابخانه‌های مدیریت سیستم..."
pip3 install python-dateutil configparser colorlog
if [ $? -ne 0 ]; then
    echo "هشدار: برخی کتابخانه‌های مدیریت سیستم نصب نشدند"
fi

# نصب کتابخانه‌های پردازش موازی
echo "نصب کتابخانه‌های پردازش موازی..."
pip3 install concurrent-futures
if [ $? -ne 0 ]; then
    echo "هشدار: concurrent-futures نصب نشد"
fi

# نصب کتابخانه‌های امنیت
echo "نصب کتابخانه‌های امنیت..."
pip3 install cryptography
if [ $? -ne 0 ]; then
    echo "هشدار: cryptography نصب نشد"
fi

# نصب رابط‌های سخت‌افزاری اضافی
echo "نصب رابط‌های سخت‌افزاری اضافی..."
pip3 install pyusb hidapi pyserial-asyncio
if [ $? -ne 0 ]; then
    echo "هشدار: برخی رابط‌های سخت‌افزاری نصب نشدند"
fi

# نصب کتابخانه‌های پردازش تصویر پیشرفته
echo "نصب کتابخانه‌های پردازش تصویر پیشرفته..."
pip3 install imageio imageio-ffmpeg
if [ $? -ne 0 ]; then
    echo "هشدار: برخی کتابخانه‌های پردازش تصویر نصب نشدند"
fi

# نصب رابط‌های شبکه پیشرفته
echo "نصب رابط‌های شبکه پیشرفته..."
pip3 install aiohttp websockets
if [ $? -ne 0 ]; then
    echo "هشدار: برخی رابط‌های شبکه نصب نشدند"
fi

# نصب وابستگی‌های سیستم
echo "نصب وابستگی‌های سیستم..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y libportaudio2 portaudio19-dev python3-tk
    sudo apt-get install -y libusb-1.0-0-dev libhackrf-dev
    sudo apt-get install -y libopencv-dev python3-opencv
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install -y portaudio-devel python3-tkinter
    sudo yum install -y libusb1-devel
    sudo yum install -y opencv-devel python3-opencv
elif command -v pacman &> /dev/null; then
    # Arch Linux
    sudo pacman -S --noconfirm portaudio python-tk
    sudo pacman -S --noconfirm libusb
    sudo pacman -S --noconfirm opencv python-opencv
fi

echo ""
echo "========================================"
echo "    نصب وابستگی‌ها تکمیل شد!"
echo "========================================"
echo ""
echo "نکات مهم:"
echo "1. برای اسکن RF واقعی: RTL-SDR یا HackRF نصب کنید"
echo "2. برای اسکن حرارتی واقعی: FLIR یا Seek Thermal نصب کنید"
echo "3. برای اسکن برق واقعی: Smart Plug یا Power Meter نصب کنید"
echo "4. برای اسکن صوتی واقعی: میکروفون با کیفیت بالا نصب کنید"
echo ""
echo "در حال راه‌اندازی سیستم..."
echo ""

# اجرای سیستم
python3 SHBHHBSH_LAUNCHER.py

if [ $? -ne 0 ]; then
    echo ""
    echo "خطا در راه‌اندازی سیستم"
    echo "لطفا فایل‌های پروژه را بررسی کنید"
    exit 1
fi

echo ""
echo "سیستم با موفقیت راه‌اندازی شد!"