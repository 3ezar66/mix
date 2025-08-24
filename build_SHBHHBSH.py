#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Script for SHBHHBSH.EXE
اسکریپت ساخت فایل اجرایی SHBHHBSH
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python():
    """بررسی نسخه Python"""
    print("🐍 بررسی Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ مورد نیاز است")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} یافت شد")
    return True

def install_pyinstaller():
    """نصب PyInstaller"""
    try:
        print("🔨 نصب PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller نصب شد")
        return True
    except Exception as e:
        print(f"❌ نصب PyInstaller ناموفق: {e}")
        return False

def check_dependencies():
    """بررسی وابستگی‌های اصلی"""
    print("📦 بررسی وابستگی‌ها...")
    
    required_files = [
        "SHBHHBSH_MAIN.py",
        "SHBHHBSH_GUI.py", 
        "SHBHHBSH_LAUNCHER.py",
        "SHBHHBSH_ADVANCED.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ فایل‌های مفقود: {', '.join(missing_files)}")
        return False
    
    print("✅ تمام فایل‌های مورد نیاز یافت شدند")
    return True

def create_spec_file():
    """ایجاد فایل spec برای PyInstaller"""
    print("📝 ایجاد فایل spec...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['SHBHHBSH_LAUNCHER.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('SHBHHBSH_MAIN.py', '.'),
        ('SHBHHBSH_GUI.py', '.'),
        ('SHBHHBSH_ADVANCED.py', '.'),
        ('requirements_SHBHHBSH.txt', '.'),
        ('README_SHBHHBSH.md', '.'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        'numpy', 'scipy', 'pandas', 'matplotlib',
        'pyaudio', 'librosa', 'sounddevice', 'rtlsdr',
        'nmap', 'scapy', 'psutil', 'GPUtil', 'serial',
        'cv2', 'folium', 'geopy', 'requests',
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
        'tkinter.filedialog', 'tkinter.scrolledtext',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure', 'matplotlib.animation'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SHBHHBSH',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('SHBHHBSH.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ فایل spec ایجاد شد")
    return True

def build_executable():
    """ساخت فایل اجرایی"""
    try:
        print("🔨 شروع ساخت فایل اجرایی...")
        
        # استفاده از فایل spec
        if os.path.exists('SHBHHBSH.spec'):
            print("📋 استفاده از فایل spec موجود...")
            subprocess.check_call([sys.executable, "-m", "PyInstaller", "SHBHHBSH.spec"])
        else:
            print("📋 ساخت با PyInstaller...")
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name=SHBHHBSH",
                "--add-data=SHBHHBSH_MAIN.py;.",
                "--add-data=SHBHHBSH_GUI.py;.",
                "--add-data=SHBHHBSH_ADVANCED.py;.",
                "--add-data=requirements_SHBHHBSH.txt;.",
                "--add-data=README_SHBHHBSH.md;.",
                "--hidden-import=numpy",
                "--hidden-import=scipy",
                "--hidden-import=pandas",
                "--hidden-import=matplotlib",
                "--hidden-import=pyaudio",
                "--hidden-import=librosa",
                "--hidden-import=sounddevice",
                "--hidden-import=rtlsdr",
                "--hidden-import=nmap",
                "--hidden-import=scapy",
                "--hidden-import=psutil",
                "--hidden-import=GPUtil",
                "--hidden-import=serial",
                "--hidden-import=cv2",
                "--hidden-import=folium",
                "--hidden-import=geopy",
                "--hidden-import=requests",
                "--hidden-import=tkinter",
                "--hidden-import=tkinter.ttk",
                "--hidden-import=tkinter.messagebox",
                "--hidden-import=tkinter.filedialog",
                "--hidden-import=tkinter.scrolledtext",
                "--hidden-import=matplotlib.backends.backend_tkagg",
                "--hidden-import=matplotlib.figure",
                "--hidden-import=matplotlib.animation",
                "SHBHHBSH_LAUNCHER.py"
            ]
            
            # اضافه کردن آیکون اگر موجود باشد
            if os.path.exists('icon.ico'):
                cmd.extend(['--icon=icon.ico'])
            
            subprocess.check_call(cmd)
        
        print("✅ ساخت فایل اجرایی تکمیل شد")
        return True
        
    except Exception as e:
        print(f"❌ ساخت فایل اجرایی ناموفق: {e}")
        return False

def verify_build():
    """تأیید ساخت موفق"""
    print("🔍 تأیید ساخت...")
    
    exe_path = None
    if os.path.exists('dist/SHBHHBSH.exe'):
        exe_path = 'dist/SHBHHBSH.exe'
    elif os.path.exists('SHBHHBSH.exe'):
        exe_path = 'SHBHHBSH.exe'
    
    if exe_path and os.path.getsize(exe_path) > 1024 * 1024:  # حداقل 1MB
        print(f"✅ فایل اجرایی ایجاد شد: {exe_path}")
        print(f"📏 اندازه: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
        return True
    else:
        print("❌ فایل اجرایی یافت نشد یا نامعتبر است")
        return False

def create_installer():
    """ایجاد نصب‌کننده"""
    print("📦 ایجاد نصب‌کننده...")
    
    try:
        # کپی فایل‌های مورد نیاز
        dist_dir = Path("dist")
        if not dist_dir.exists():
            dist_dir.mkdir()
        
        # کپی فایل‌های پشتیبانی
        support_files = [
            "requirements_SHBHHBSH.txt",
            "README_SHBHHBSH.md",
            "install_SHBHHBSH.bat",
            "RUN_SHBHHBSH.bat"
        ]
        
        for file in support_files:
            if os.path.exists(file):
                shutil.copy2(file, dist_dir)
                print(f"📋 کپی شد: {file}")
        
        # ایجاد فایل README نصب
        install_readme = """# نصب و راه‌اندازی SHBHHBSH

## روش 1: اجرای مستقیم
فایل SHBHHBSH.exe را مستقیماً اجرا کنید.

## روش 2: نصب کامل
1. فایل install_SHBHHBSH.bat را اجرا کنید
2. منتظر تکمیل نصب وابستگی‌ها باشید
3. فایل RUN_SHBHHBSH.bat را اجرا کنید

## روش 3: نصب دستی
1. Python 3.8+ را نصب کنید
2. pip install -r requirements_SHBHHBSH.txt
3. python SHBHHBSH_LAUNCHER.py

## پشتیبانی
برای اطلاعات بیشتر README_SHBHHBSH.md را مطالعه کنید.
"""
        
        with open(dist_dir / "INSTALL.txt", 'w', encoding='utf-8') as f:
            f.write(install_readme)
        
        print("✅ نصب‌کننده ایجاد شد")
        return True
        
    except Exception as e:
        print(f"❌ ایجاد نصب‌کننده ناموفق: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🚀 SHBHHBSH - ساخت فایل اجرایی")
    print("=" * 50)
    
    # بررسی‌های اولیه
    if not check_python():
        return False
    
    if not check_dependencies():
        return False
    
    # نصب PyInstaller
    if not install_pyinstaller():
        return False
    
    # ایجاد فایل spec
    if not create_spec_file():
        return False
    
    # ساخت فایل اجرایی
    if not build_executable():
        return False
    
    # تأیید ساخت
    if not verify_build():
        return False
    
    # ایجاد نصب‌کننده
    if not create_installer():
        return False
    
    print("\n🎉 ساخت با موفقیت تکمیل شد!")
    print("\n📁 فایل‌های تولید شده:")
    print("   - dist/SHBHHBSH.exe (فایل اجرایی اصلی)")
    print("   - dist/INSTALL.txt (راهنمای نصب)")
    print("   - dist/requirements_SHBHHBSH.txt (وابستگی‌ها)")
    print("   - dist/README_SHBHHBSH.md (مستندات)")
    print("   - dist/install_SHBHHBSH.bat (نصب خودکار)")
    print("   - dist/RUN_SHBHHBSH.bat (اجرای سریع)")
    
    print("\n🚀 برای اجرا:")
    print("   - فایل SHBHHBSH.exe را مستقیماً اجرا کنید")
    print("   - یا از فایل‌های batch استفاده کنید")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ عملیات با موفقیت تکمیل شد!")
        else:
            print("\n❌ عملیات ناموفق بود!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ عملیات توسط کاربر متوقف شد")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 خطای غیرمنتظره: {e}")
        sys.exit(1)