@echo off
title SHBHHBSH - سیستم تشخیص ماینر
color 0B

echo.
echo ========================================
echo    SHBHHBSH - سیستم تشخیص ماینر
echo ========================================
echo.
echo در حال راه‌اندازی سیستم...
echo.

REM اجرای راه‌انداز اصلی
python SHBHHBSH_LAUNCHER.py

if errorlevel 1 (
    echo.
    echo خطا در اجرای سیستم
    echo لطفاً وابستگی‌ها را نصب کنید: install_SHBHHBSH.bat
    echo.
    pause
)