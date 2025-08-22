import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🚀 Creating Kashif Mining Detector - Complete Standalone Solution...');

// Configuration
const config = {
  appName: 'کاشف شبح حبشی',
  version: '2.0.0',
  description: 'سیستم ملی تشخیص ماینینگ غیرمجاز',
  author: 'Kashif Team',
  port: 5000
};

// Create complete standalone package
function createCompleteStandalone() {
  const standaloneDir = 'kashif-standalone-complete';
  
  // Clean existing directory
  if (fs.existsSync(standaloneDir)) {
    fs.rmSync(standaloneDir, { recursive: true });
  }
  fs.mkdirSync(standaloneDir);
  
  console.log('📁 Creating complete standalone package structure...');
  
  // Create directory structure
  const dirs = [
    'app',
    'app/dist',
    'app/server',
    'app/shared',
    'app/data',
    'app/logs',
    'app/config',
    'app/assets',
    'tools',
    'docs'
  ];
  
  dirs.forEach(dir => {
    fs.mkdirSync(path.join(standaloneDir, dir), { recursive: true });
  });
  
  // Copy built files
  console.log('📦 Copying application files...');
  if (fs.existsSync('dist')) {
    fs.cpSync('dist', path.join(standaloneDir, 'app/dist'), { recursive: true });
  }
  
  // Copy server files
  if (fs.existsSync('server')) {
    fs.cpSync('server', path.join(standaloneDir, 'app/server'), { recursive: true });
  }
  
  // Copy shared files
  if (fs.existsSync('shared')) {
    fs.cpSync('shared', path.join(standaloneDir, 'app/shared'), { recursive: true });
  }
  
  // Copy database
  if (fs.existsSync('ilam_mining.db')) {
    fs.copyFileSync('ilam_mining.db', path.join(standaloneDir, 'app/ilam_mining.db'));
  }
  
  // Copy data files
  if (fs.existsSync('data')) {
    fs.cpSync('data', path.join(standaloneDir, 'app/data'), { recursive: true });
  }
  
  // Copy drizzle migrations
  if (fs.existsSync('drizzle')) {
    fs.cpSync('drizzle', path.join(standaloneDir, 'app/drizzle'), { recursive: true });
  }
  
  // Create startup tools
  createStartupTools(standaloneDir);
  
  // Create configuration files
  createConfigurationFiles(standaloneDir);
  
  // Create documentation
  createCompleteDocumentation(standaloneDir);
  
  // Create installer scripts
  createInstallerScripts(standaloneDir);
  
  // Create system requirements checker
  createSystemChecker(standaloneDir);
  
  console.log('✅ Complete standalone package created successfully!');
  console.log(`📦 Package location: ${standaloneDir}`);
}

// Create startup tools for different platforms
function createStartupTools(standaloneDir) {
  console.log('🔧 Creating startup tools...');
  
  // Windows Launcher
  const windowsLauncher = `@echo off
chcp 65001 >nul
title Kashif Mining Detector - کاشف شبح حبشی

echo ========================================
echo Kashif - Shabah Habashi
echo سیستم ملی تشخیص ماینینگ غیرمجاز
echo ========================================
echo.
echo Version: ${config.version}
echo Port: ${config.port}
echo.

REM Check system requirements
echo Checking system requirements...
call "tools\\check-system.bat"
if %errorlevel% neq 0 (
    echo System requirements not met. Please check the requirements.
    pause
    exit /b 1
)

echo ✅ System requirements met
echo.
echo Starting Kashif Mining Detector...
echo.

REM Set environment variables
set NODE_ENV=production
set PORT=${config.port}
set APP_ROOT=%~dp0app

REM Start the server
cd /d "%APP_ROOT%"
node dist/server/index.js

echo.
echo Server stopped. Press any key to exit...
pause >nul
`;

  fs.writeFileSync(path.join(standaloneDir, 'start.bat'), windowsLauncher);
  
  // Linux/Mac Launcher
  const unixLauncher = `#!/bin/bash

# Kashif Mining Detector - کاشف شبح حبشی
# سیستم ملی تشخیص ماینینگ غیرمجاز

echo "========================================"
echo "Kashif - Shabah Habashi"
echo "سیستم ملی تشخیص ماینینگ غیرمجاز"
echo "========================================"
echo ""
echo "Version: ${config.version}"
echo "Port: ${config.port}"
echo ""

# Check system requirements
echo "Checking system requirements..."
./tools/check-system.sh
if [ $? -ne 0 ]; then
    echo "System requirements not met. Please check the requirements."
    exit 1
fi

echo "✅ System requirements met"
echo ""
echo "Starting Kashif Mining Detector..."
echo ""

# Set environment variables
export NODE_ENV=production
export PORT=${config.port}
export APP_ROOT="$( cd "$( dirname "\${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/app"

# Start the server
cd "\$APP_ROOT"
node dist/server/index.js

echo ""
echo "Server stopped."
`;

  fs.writeFileSync(path.join(standaloneDir, 'start.sh'), unixLauncher);
  
  // Make shell script executable
  try {
    fs.chmodSync(path.join(standaloneDir, 'start.sh'), '755');
  } catch (error) {
    console.log('⚠️  Could not set executable permissions on start.sh');
  }
  
  // PowerShell Launcher
  const powershellLauncher = `# Kashif Mining Detector - کاشف شبح حبشی
# سیستم ملی تشخیص ماینینگ غیرمجاز

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Kashif - Shabah Habashi" -ForegroundColor Yellow
Write-Host "سیستم ملی تشخیص ماینینگ غیرمجاز" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Version: ${config.version}" -ForegroundColor Green
Write-Host "Port: ${config.port}" -ForegroundColor Green
Write-Host ""

# Check system requirements
Write-Host "Checking system requirements..." -ForegroundColor Cyan
& ".\tools\check-system.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "System requirements not met. Please check the requirements." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ System requirements met" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Kashif Mining Detector..." -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:NODE_ENV = "production"
$env:PORT = "${config.port}"
$env:APP_ROOT = (Split-Path -Parent $MyInvocation.MyCommand.Path) + "\app"

# Start the server
Set-Location $env:APP_ROOT
node dist/server/index.js

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
`;

  fs.writeFileSync(path.join(standaloneDir, 'start.ps1'), powershellLauncher);
  
  console.log('✅ Startup tools created');
}

// Create system requirement checkers
function createSystemChecker(standaloneDir) {
  console.log('🔍 Creating system requirement checkers...');
  
  // Windows system checker
  const windowsChecker = `@echo off
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

echo Checking port availability...
netstat -an | find "0.0.0.0:${config.port}" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Port ${config.port} is already in use
    echo Please close other applications using port ${config.port}
    exit /b 1
)

echo Checking disk space...
for /f "tokens=3" %%a in ('dir /-c 2^>nul ^| find "bytes free"') do set free=%%a
if %free% LSS 1000000000 (
    echo ⚠️  Low disk space. At least 1GB free space is recommended.
)

echo ✅ All system requirements met
exit /b 0
`;

  fs.writeFileSync(path.join(standaloneDir, 'tools', 'check-system.bat'), windowsChecker);
  
  // Linux/Mac system checker
  const unixChecker = `#!/bin/bash

echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "Checking port availability..."
if lsof -Pi :${config.port} -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port ${config.port} is already in use"
    echo "Please close other applications using port ${config.port}"
    exit 1
fi

echo "Checking disk space..."
free_space=$(df . | awk 'NR==2 {print $4}')
if [ $free_space -lt 1000000 ]; then
    echo "⚠️  Low disk space. At least 1GB free space is recommended."
fi

echo "✅ All system requirements met"
exit 0
`;

  fs.writeFileSync(path.join(standaloneDir, 'tools', 'check-system.sh'), unixChecker);
  
  // PowerShell system checker
  const powershellChecker = `# System Requirements Checker

Write-Host "Checking Node.js..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Checking port availability..." -ForegroundColor Cyan
$portInUse = Get-NetTCPConnection -LocalPort ${config.port} -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Port ${config.port} is already in use" -ForegroundColor Yellow
    Write-Host "Please close other applications using port ${config.port}" -ForegroundColor Yellow
    exit 1
}

Write-Host "Checking disk space..." -ForegroundColor Cyan
$freeSpace = (Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace
if ($freeSpace -lt 1GB) {
    Write-Host "⚠️  Low disk space. At least 1GB free space is recommended." -ForegroundColor Yellow
}

Write-Host "✅ All system requirements met" -ForegroundColor Green
exit 0
`;

  fs.writeFileSync(path.join(standaloneDir, 'tools', 'check-system.ps1'), powershellChecker);
  
  console.log('✅ System requirement checkers created');
}

// Create configuration files
function createConfigurationFiles(standaloneDir) {
  console.log('⚙️  Creating configuration files...');
  
  // Main configuration file
  const configFile = {
    app: {
      name: config.appName,
      version: config.version,
      description: config.description,
      port: config.port,
      environment: 'production'
    },
    database: {
      path: './ilam_mining.db',
      type: 'sqlite',
      backup: {
        enabled: true,
        interval: '24h',
        maxBackups: 7,
        path: './data/backups'
      }
    },
    logging: {
      level: 'info',
      file: './logs/app.log',
      maxSize: '10m',
      maxFiles: 5,
      rotation: true
    },
    security: {
      sessionSecret: 'kashif-mining-detector-secret-key',
      jwtSecret: 'kashif-jwt-secret-key',
      bcryptRounds: 10,
      rateLimiting: {
        enabled: true,
        windowMs: 15 * 60 * 1000, // 15 minutes
        maxRequests: 100
      }
    },
    features: {
      realTimeScanning: true,
      networkAnalysis: true,
      geolocation: true,
      reporting: true,
      alerts: true,
      rfAnalysis: true,
      thermalAnalysis: true,
      acousticAnalysis: true
    },
    performance: {
      maxConcurrentScans: 10,
      scanTimeout: 30000,
      memoryLimit: '1GB',
      cpuLimit: 80
    }
  };
  
  fs.writeFileSync(
    path.join(standaloneDir, 'app', 'config', 'app.json'), 
    JSON.stringify(configFile, null, 2)
  );
  
  // Environment file
  const envFile = `# Kashif Mining Detector Environment Configuration
NODE_ENV=production
PORT=${config.port}
DATABASE_PATH=./ilam_mining.db
LOG_LEVEL=info
LOG_FILE=./logs/app.log
SESSION_SECRET=kashif-mining-detector-secret-key
JWT_SECRET=kashif-jwt-secret-key
BCRYPT_ROUNDS=10

# Feature flags
ENABLE_REAL_TIME_SCANNING=true
ENABLE_NETWORK_ANALYSIS=true
ENABLE_GEOLOCATION=true
ENABLE_REPORTING=true
ENABLE_ALERTS=true
ENABLE_RF_ANALYSIS=true
ENABLE_THERMAL_ANALYSIS=true
ENABLE_ACOUSTIC_ANALYSIS=true

# Security settings
ENABLE_RATE_LIMITING=true
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX_REQUESTS=100

# Database settings
DB_MIGRATIONS_PATH=./drizzle
DB_BACKUP_PATH=./data/backups
DB_BACKUP_ENABLED=true
DB_BACKUP_INTERVAL=24h
DB_MAX_BACKUPS=7

# Logging settings
LOG_MAX_SIZE=10m
LOG_MAX_FILES=5
LOG_ROTATE=true

# Performance settings
MAX_CONCURRENT_SCANS=10
SCAN_TIMEOUT=30000
MEMORY_LIMIT=1GB
CPU_LIMIT=80
`;
  
  fs.writeFileSync(path.join(standaloneDir, 'app', 'config', '.env'), envFile);
  
  console.log('✅ Configuration files created');
}

// Create installer scripts
function createInstallerScripts(standaloneDir) {
  console.log('🔧 Creating installer scripts...');
  
  // Windows installer
  const windowsInstaller = `@echo off
echo Installing Kashif Mining Detector...
echo.

REM Create program directory
set "INSTALL_DIR=%PROGRAMFILES%\\Kashif Mining Detector"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
xcopy /E /I /Y "app" "%INSTALL_DIR%\\app"
xcopy /E /I /Y "tools" "%INSTALL_DIR%\\tools"
copy "start.bat" "%INSTALL_DIR%\\"
copy "README.md" "%INSTALL_DIR%\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Kashif Mining Detector.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\start.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Kashif Mining Detector" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Kashif Mining Detector"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Kashif Mining Detector\\Kashif Mining Detector.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\start.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo ✅ Installation completed successfully!
echo.
echo Kashif Mining Detector has been installed to: %INSTALL_DIR%
echo Desktop shortcut has been created.
echo Start menu shortcut has been created.
echo.
echo To start the application, double-click the desktop shortcut or run:
echo %INSTALL_DIR%\\start.bat
echo.
pause
`;

  fs.writeFileSync(path.join(standaloneDir, 'install.bat'), windowsInstaller);
  
  // Linux installer
  const linuxInstaller = `#!/bin/bash

echo "Installing Kashif Mining Detector..."
echo ""

# Create installation directory
INSTALL_DIR="/opt/kashif-mining-detector"
sudo mkdir -p "$INSTALL_DIR"

# Copy files
sudo cp -r app "$INSTALL_DIR/"
sudo cp -r tools "$INSTALL_DIR/"
sudo cp start.sh "$INSTALL_DIR/"
sudo cp README.md "$INSTALL_DIR/"

# Set permissions
sudo chmod +x "$INSTALL_DIR/start.sh"
sudo chmod +x "$INSTALL_DIR/tools/check-system.sh"

# Create desktop shortcut
echo "Creating desktop shortcut..."
cat > ~/Desktop/kashif-mining-detector.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Kashif Mining Detector
Comment=سیستم ملی تشخیص ماینینگ غیرمجاز
Exec=$INSTALL_DIR/start.sh
Icon=$INSTALL_DIR/app/assets/icon.png
Terminal=true
Categories=Utility;Security;
EOF

chmod +x ~/Desktop/kashif-mining-detector.desktop

# Create systemd service (optional)
echo "Creating systemd service..."
sudo tee /etc/systemd/system/kashif-mining-detector.service > /dev/null << EOF
[Unit]
Description=Kashif Mining Detector
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "Kashif Mining Detector has been installed to: $INSTALL_DIR"
echo "Desktop shortcut has been created."
echo "Systemd service has been created (optional)."
echo ""
echo "To start the application:"
echo "  Desktop: Double-click the desktop shortcut"
echo "  Terminal: $INSTALL_DIR/start.sh"
echo "  Service: sudo systemctl start kashif-mining-detector"
echo ""
`;

  fs.writeFileSync(path.join(standaloneDir, 'install.sh'), linuxInstaller);
  
  console.log('✅ Installer scripts created');
}

// Create comprehensive documentation
function createCompleteDocumentation(standaloneDir) {
  console.log('📚 Creating comprehensive documentation...');
  
  // Main README
  const readme = `# Kashif Mining Detector - Complete Standalone Solution

## کاشف شبح حبشی - سیستم ملی تشخیص ماینینگ غیرمجاز

### معرفی:
این بسته شامل یک راه‌حل کامل و مستقل برای تشخیص و نظارت بر فعالیت‌های ماینینگ رمزارز است که بدون نیاز به نصب یا تنظیمات پیچیده قابل اجرا است.

### ویژگی‌های کلیدی:
- 🔍 تشخیص پیشرفته دستگاه‌های ماینینگ رمزارز
- 🗺️ نقشه تعاملی با موقعیت جغرافیایی دقیق
- 🌐 تحلیل عمیق ترافیک شبکه
- 📊 گزارش‌گیری جامع و حرفه‌ای
- 🚨 سیستم هشدار پیشرفته و هوشمند
- 🔐 احراز هویت امن و چندلایه
- 📱 رابط کاربری مدرن و واکنش‌گرا
- 🔬 تحلیل سیگنال‌های RF
- 🌡️ تشخیص حرارتی
- 🔊 تحلیل آکوستیک

### نیازمندی‌های سیستم:

#### حداقل نیازمندی‌ها:
- **سیستم‌عامل**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Node.js**: نسخه 18 یا بالاتر
- **RAM**: حداقل 4GB
- **فضای دیسک**: حداقل 2GB
- **شبکه**: دسترسی به اینترنت

#### توصیه شده:
- **RAM**: 8GB یا بیشتر
- **فضای دیسک**: 5GB یا بیشتر
- **پردازنده**: Intel i5 یا AMD Ryzen 5 یا بالاتر

### راهنمای نصب و اجرا:

#### روش 1: اجرای مستقیم (پیشنهادی)
1. فایل مناسب سیستم‌عامل خود را اجرا کنید:
   - **Windows**: `start.bat`
   - **Linux/Mac**: `./start.sh`
   - **PowerShell**: `.\start.ps1`

#### روش 2: نصب کامل
1. فایل نصب مناسب را اجرا کنید:
   - **Windows**: `install.bat`
   - **Linux**: `./install.sh`

### دسترسی به برنامه:
پس از راه‌اندازی سرور، مرورگر را باز کرده و به آدرس زیر بروید:
\`\`\`
http://localhost:${config.port}
\`\`\`

### اطلاعات ورود پیش‌فرض:
- **نام کاربری**: admin
- **رمز عبور**: admin

⚠️ **توجه**: حتماً رمز عبور پیش‌فرض را تغییر دهید.

### ساختار فایل‌ها:
\`\`\`
kashif-standalone-complete/
├── app/                    # فایل‌های اصلی برنامه
│   ├── dist/              # فایل‌های کامپایل شده
│   ├── server/            # کدهای سرور
│   ├── shared/            # فایل‌های مشترک
│   ├── data/              # داده‌ها و پشتیبان‌ها
│   ├── logs/              # فایل‌های لاگ
│   ├── config/            # فایل‌های تنظیمات
│   ├── assets/            # فایل‌های رسانه
│   └── ilam_mining.db     # پایگاه داده
├── tools/                 # ابزارهای کمکی
│   ├── check-system.bat   # بررسی سیستم (Windows)
│   ├── check-system.sh    # بررسی سیستم (Linux/Mac)
│   └── check-system.ps1   # بررسی سیستم (PowerShell)
├── docs/                  # مستندات
├── start.bat              # راه‌اندازی Windows
├── start.sh               # راه‌اندازی Linux/Mac
├── start.ps1              # راه‌اندازی PowerShell
├── install.bat            # نصب Windows
├── install.sh             # نصب Linux
└── README.md              # این فایل
\`\`\`

### تنظیمات پیشرفته:
فایل‌های تنظیمات در پوشه \`app/config\` قرار دارند:
- \`app.json\`: تنظیمات اصلی برنامه
- \`.env\`: متغیرهای محیطی

### عیب‌یابی:

#### مشکل: پورت ${config.port} در حال استفاده است
**راه‌حل**: 
1. برنامه‌های دیگر را که از پورت ${config.port} استفاده می‌کنند ببندید
2. یا پورت را در فایل \`app/config/app.json\` تغییر دهید

#### مشکل: Node.js یافت نشد
**راه‌حل**:
1. Node.js را از https://nodejs.org/ دانلود و نصب کنید
2. مطمئن شوید که Node.js در PATH سیستم قرار دارد

#### مشکل: دسترسی به پایگاه داده
**راه‌حل**:
1. مطمئن شوید که فایل \`ilam_mining.db\` موجود است
2. دسترسی‌های لازم را به پوشه برنامه بدهید

#### مشکل: خطای "Permission denied"
**راه‌حل**:
1. برنامه را با دسترسی Administrator اجرا کنید
2. دسترسی‌های پوشه را بررسی کنید

### ویژگی‌های امنیتی:
- 🔐 احراز هویت چندلایه
- 🛡️ محافظت در برابر حملات
- 🔒 رمزگذاری داده‌ها
- 📝 لاگ‌گیری امن
- 🚫 محدودیت نرخ درخواست

### پشتیبانی:
- **ایمیل**: support@kashif.ir
- **تلفن**: +98-21-XXXXXXXX
- **وب‌سایت**: https://kashif.ir
- **مستندات**: https://docs.kashif.ir

### لایسنس:
این نرم‌افزار تحت لایسنس MIT منتشر شده است.

### تغییرات نسخه ${config.version}:
- بهبود عملکرد و سرعت
- اضافه شدن تحلیل‌های پیشرفته
- بهبود رابط کاربری
- رفع مشکلات امنیتی
- اضافه شدن قابلیت‌های جدید

---
**نسخه**: ${config.version}  
**توسعه‌یافته توسط**: ${config.author}  
**تاریخ انتشار**: ${new Date().toLocaleDateString('fa-IR')}  
**وضعیت**: آماده برای تولید
`;

  fs.writeFileSync(path.join(standaloneDir, 'README.md'), readme);
  
  // Quick start guide
  const quickStart = `# راهنمای سریع - Kashif Mining Detector

## شروع سریع:

### 1. بررسی سیستم:
- **Windows**: \`tools\\check-system.bat\`
- **Linux/Mac**: \`./tools/check-system.sh\`
- **PowerShell**: \`.\tools\\check-system.ps1\`

### 2. راه‌اندازی:
- **Windows**: روی \`start.bat\` دوبار کلیک کنید
- **Linux/Mac**: در ترمینال \`./start.sh\` را اجرا کنید
- **PowerShell**: \`.\start.ps1\` را اجرا کنید

### 3. دسترسی:
- مرورگر را باز کنید
- به آدرس \`http://localhost:${config.port}\` بروید

### 4. ورود:
- نام کاربری: \`admin\`
- رمز عبور: \`admin\`

### 5. تغییر رمز عبور:
- به بخش تنظیمات بروید
- رمز عبور جدید را تنظیم کنید

### 6. شروع اسکن:
- روی "شروع اسکن" کلیک کنید
- مناطق مورد نظر را انتخاب کنید
- نتایج را مشاهده کنید

---
برای اطلاعات بیشتر فایل README.md را مطالعه کنید.
`;

  fs.writeFileSync(path.join(standaloneDir, 'docs', 'QUICK_START.md'), quickStart);
  
  // Troubleshooting guide
  const troubleshooting = `# راهنمای عیب‌یابی - Kashif Mining Detector

## مشکلات رایج و راه‌حل‌ها:

### 1. خطای "Port ${config.port} is already in use"
**علت**: پورت ${config.port} توسط برنامه دیگری استفاده می‌شود
**راه‌حل**:
- برنامه‌های دیگر را ببندید
- یا پورت را در \`app/config/app.json\` تغییر دهید

### 2. خطای "Node.js is not installed"
**علت**: Node.js نصب نشده یا در PATH نیست
**راه‌حل**:
- Node.js را از https://nodejs.org/ دانلود کنید
- نصب کنید و سیستم را راه‌اندازی مجدد کنید

### 3. خطای "Database connection failed"
**علت**: مشکل در دسترسی به پایگاه داده
**راه‌حل**:
- فایل \`ilam_mining.db\` را بررسی کنید
- دسترسی‌های پوشه را بررسی کنید

### 4. خطای "Permission denied"
**علت**: عدم دسترسی کافی
**راه‌حل**:
- برنامه را با دسترسی Administrator اجرا کنید
- دسترسی‌های پوشه را بررسی کنید

### 5. خطای "Module not found"
**علت**: فایل‌های برنامه ناقص است
**راه‌حل**:
- فایل‌ها را مجدداً دانلود کنید
- مطمئن شوید که تمام فایل‌ها موجود هستند

### 6. مشکل در نمایش زبان فارسی
**علت**: تنظیمات زبان سیستم
**راه‌حل**:
- فونت‌های فارسی را نصب کنید
- تنظیمات زبان مرورگر را بررسی کنید

### 7. مشکل در عملکرد کند
**علت**: منابع سیستم ناکافی
**راه‌حل**:
- RAM بیشتری اضافه کنید
- برنامه‌های دیگر را ببندید
- تنظیمات عملکرد را بررسی کنید

## لاگ‌ها:
فایل‌های لاگ در پوشه \`app/logs\` قرار دارند:
- \`app.log\`: لاگ‌های عمومی
- \`error.log\`: لاگ‌های خطا

## تماس با پشتیبانی:
در صورت بروز مشکل:
1. فایل‌های لاگ را بررسی کنید
2. با تیم پشتیبانی تماس بگیرید
3. اطلاعات سیستم و خطا را ارسال کنید

---
برای اطلاعات بیشتر به فایل README.md مراجعه کنید.
`;

  fs.writeFileSync(path.join(standaloneDir, 'docs', 'TROUBLESHOOTING.md'), troubleshooting);
  
  // User manual
  const userManual = `# راهنمای کاربر - Kashif Mining Detector

## فهرست مطالب:

### 1. شروع کار
- نصب و راه‌اندازی
- ورود به سیستم
- تنظیمات اولیه

### 2. رابط کاربری
- داشبورد اصلی
- منوها و نوار ابزار
- تنظیمات نمایش

### 3. اسکن و تشخیص
- شروع اسکن
- تنظیمات اسکن
- مشاهده نتایج

### 4. نقشه و موقعیت
- نقشه تعاملی
- نمایش موقعیت‌ها
- فیلتر کردن نتایج

### 5. گزارش‌گیری
- ایجاد گزارش
- انواع گزارش
- صادر کردن گزارش

### 6. هشدارها
- تنظیم هشدارها
- مدیریت هشدارها
- اعلان‌ها

### 7. مدیریت کاربران
- ایجاد کاربر
- تنظیم دسترسی‌ها
- مدیریت نقش‌ها

### 8. تنظیمات پیشرفته
- تنظیمات سیستم
- تنظیمات شبکه
- تنظیمات امنیتی

### 9. نگهداری
- پشتیبان‌گیری
- به‌روزرسانی
- عیب‌یابی

---
این راهنما در حال تکمیل است.
`;

  fs.writeFileSync(path.join(standaloneDir, 'docs', 'USER_MANUAL.md'), userManual);
  
  console.log('✅ Comprehensive documentation created');
}

// Main execution
async function main() {
  try {
    console.log('🚀 Starting complete standalone solution creation...');
    console.log(`📋 Configuration:`);
    console.log(`  - App Name: ${config.appName}`);
    console.log(`  - Version: ${config.version}`);
    console.log(`  - Port: ${config.port}`);
    
    // Check if build exists
    if (!fs.existsSync('dist')) {
      console.log('🔨 Building project first...');
      execSync('npm run build', { stdio: 'inherit' });
    }
    
    createCompleteStandalone();
    
    console.log('🎉 Complete standalone solution created successfully!');
    console.log('📁 Package location: kashif-standalone-complete/');
    console.log('🚀 To run:');
    console.log('  Windows: Double-click start.bat');
    console.log('  Linux/Mac: ./start.sh');
    console.log('  PowerShell: .\\start.ps1');
    console.log('');
    console.log('📚 Documentation available in:');
    console.log('  - README.md (راهنمای اصلی)');
    console.log('  - docs/QUICK_START.md (شروع سریع)');
    console.log('  - docs/TROUBLESHOOTING.md (عیب‌یابی)');
    console.log('  - docs/USER_MANUAL.md (راهنمای کاربر)');
    console.log('');
    console.log('🔧 Tools available:');
    console.log('  - tools/check-system.* (بررسی سیستم)');
    console.log('  - install.* (نصب کامل)');
    
  } catch (error) {
    console.error('❌ Failed to create complete standalone solution:', error);
    process.exit(1);
  }
}

// Run the main function
main(); 