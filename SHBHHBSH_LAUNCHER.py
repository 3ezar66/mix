#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHBHHBSH Launcher - نقطه ورودی اصلی اجرایی
سیستم جامع تخصصی جستجو و شناسایی و کشف و تشخیص واقعی دستگاه های استخراج رمزارز
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time

def check_dependencies():
    """بررسی دسترسی‌پذیری تمام وابستگی‌های مورد نیاز"""
    required_packages = [
        'numpy', 'scipy', 'pandas', 'matplotlib', 'tkinter',
        'pyaudio', 'librosa', 'sounddevice', 'rtlsdr', 'nmap',
        'scapy', 'psutil', 'GPUtil', 'serial', 'cv2', 'folium',
        'geopy', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'cv2':
                import cv2
            elif package == 'serial':
                import serial
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """نصب وابستگی‌های مفقود"""
    try:
        import pip
        print("در حال نصب وابستگی‌های مفقود...")
        
        # نصب بسته‌های اصلی
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy", "scipy", "pandas", "matplotlib"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio", "librosa", "sounddevice"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rtlsdr", "python-nmap", "scapy"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "GPUtil", "pyserial"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python", "folium", "geopy", "requests"])
        
        print("وابستگی‌ها با موفقیت نصب شدند!")
        return True
        
    except Exception as e:
        print(f"نصب وابستگی‌ها ناموفق بود: {e}")
        return False

def show_splash_screen():
    """نمایش صفحه شروع در حین بارگذاری"""
    splash = tk.Tk()
    splash.title("SHBHHBSH")
    splash.geometry("600x400")
    splash.configure(bg='#1e1e1e')
    
    # مرکز قرار دادن پنجره
    splash.update_idletasks()
    width = splash.winfo_width()
    height = splash.winfo_height()
    x = (splash.winfo_screenwidth() // 2) - (width // 2)
    y = (splash.winfo_screenheight() // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")
    
    # عنوان
    title_label = tk.Label(
        splash,
        text="🔍 SHBHHBSH",
        font=('Arial', 24, 'bold'),
        bg='#1e1e1e',
        fg='#3498db'
    )
    title_label.pack(pady=50)
    
    subtitle_label = tk.Label(
        splash,
        text="سیستم جامع تخصصی جستجو و شناسایی و کشف و تشخیص واقعی دستگاه های استخراج رمزارز",
        font=('Arial', 12),
        bg='#1e1e1e',
        fg='white',
        wraplength=500
    )
    subtitle_label.pack(pady=20)
    
    subtitle2_label = tk.Label(
        splash,
        text="Comprehensive Professional Cryptocurrency Mining Device Detection System",
        font=('Arial', 10),
        bg='#1e1e1e',
        fg='#95a5a6'
    )
    subtitle2_label.pack(pady=10)
    
    # نوار پیشرفت
    progress_var = tk.DoubleVar()
    progress_bar = tk.ttk.Progressbar(
        splash,
        variable=progress_var,
        maximum=100
    )
    progress_bar.pack(pady=20, padx=50, fill=tk.X)
    
    # برچسب وضعیت
    status_var = tk.StringVar(value="در حال راه‌اندازی...")
    status_label = tk.Label(
        splash,
        textvariable=status_var,
        bg='#1e1e1e',
        fg='#95a5a6'
    )
    status_label.pack(pady=10)
    
    # اطلاعات نسخه
    version_label = tk.Label(
        splash,
        text="نسخه 2.0.0 | تیم امنیت پیشرفته",
        font=('Arial', 8),
        bg='#1e1e1e',
        fg='#7f8c8d'
    )
    version_label.pack(side=tk.BOTTOM, pady=10)
    
    return splash, progress_var, status_var

def main():
    """تابع اصلی راه‌انداز"""
    try:
        # نمایش صفحه شروع
        splash, progress_var, status_var = show_splash_screen()
        
        def update_progress():
            """به‌روزرسانی نوار پیشرفت"""
            for i in range(101):
                if splash.winfo_exists():
                    progress_var.set(i)
                    if i < 30:
                        status_var.set("در حال بررسی وابستگی‌ها...")
                    elif i < 60:
                        status_var.set("در حال بارگذاری ماژول‌ها...")
                    elif i < 90:
                        status_var.set("در حال راه‌اندازی سیستم...")
                    else:
                        status_var.set("آماده!")
                    splash.update()
                    time.sleep(0.05)
                else:
                    break
        
        # شروع به‌روزرسانی پیشرفت
        progress_thread = threading.Thread(target=update_progress)
        progress_thread.start()
        
        # بررسی وابستگی‌ها
        missing_packages = check_dependencies()
        
        if missing_packages:
            splash.destroy()
            
            # پرسیدن از کاربر برای نصب وابستگی‌ها
            root = tk.Tk()
            root.withdraw()
            
            result = messagebox.askyesno(
                "وابستگی‌های مفقود",
                f"بسته‌های زیر مفقود هستند:\n{', '.join(missing_packages)}\n\nآیا می‌خواهید آنها را به طور خودکار نصب کنید؟"
            )
            
            if result:
                if install_dependencies():
                    messagebox.showinfo("موفقیت", "وابستگی‌ها با موفقیت نصب شدند! لطفاً برنامه را مجدداً راه‌اندازی کنید.")
                else:
                    messagebox.showerror("خطا", "نصب وابستگی‌ها ناموفق بود. لطفاً آنها را به صورت دستی نصب کنید.")
            else:
                messagebox.showwarning("هشدار", "برخی ویژگی‌ها بدون وابستگی‌های مورد نیاز کار نخواهند کرد.")
            
            root.destroy()
            return
        
        # انتظار برای تکمیل پیشرفت
        progress_thread.join()
        
        # بستن صفحه شروع
        splash.destroy()
        
        # وارد کردن و اجرای برنامه اصلی
        try:
            from SHBHHBSH_GUI import ModernMiningDetectorGUI
            
            root = tk.Tk()
            app = ModernMiningDetectorGUI(root)
            
            # مرکز قرار دادن پنجره
            root.update_idletasks()
            width = root.winfo_width()
            height = root.winfo_height()
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry(f"{width}x{height}+{x}+{y}")
            
            root.mainloop()
            
        except ImportError as e:
            messagebox.showerror("خطای وارد کردن", f"وارد کردن برنامه اصلی ناموفق بود: {e}")
        except Exception as e:
            messagebox.showerror("خطای اجرا", f"خطای برنامه: {e}")
            
    except Exception as e:
        print(f"خطای راه‌انداز: {e}")
        messagebox.showerror("خطای راه‌انداز", f"راه‌اندازی برنامه ناموفق بود: {e}")

if __name__ == "__main__":
    main()