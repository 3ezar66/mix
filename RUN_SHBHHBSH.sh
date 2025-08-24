#!/bin/bash

echo "========================================"
echo "   SHBHHBSH - سیستم تشخیص ماینر"
echo "========================================"
echo ""
echo "در حال راه‌اندازی سیستم..."
echo ""

# اجرای راه‌انداز اصلی
python3 SHBHHBSH_LAUNCHER.py

if [ $? -ne 0 ]; then
    echo ""
    echo "خطا در اجرای سیستم"
    echo "لطفاً وابستگی‌ها را نصب کنید: ./install_SHBHHBSH.sh"
    echo ""
    read -p "برای ادامه Enter را فشار دهید..."
fi