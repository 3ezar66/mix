import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🚀 Creating Kashif Mining Detector Portable Package...');

// Configuration
const config = {
  appName: 'کاشف شبح حبشی',
  version: '2.0.0',
  description: 'سیستم ملی تشخیص ماینینگ غیرمجاز',
  port: 5000
};

// Create portable package
function createPortablePackage() {
  const portableDir = 'kashif-portable';
  
  // Clean existing directory
  if (fs.existsSync(portableDir)) {
    fs.rmSync(portableDir, { recursive: true });
  }
  fs.mkdirSync(portableDir);
  
  console.log('📁 Creating portable package structure...');
  
  // Create directory structure
  const dirs = [
    'dist',
    'server',
    'shared',
    'data',
    'logs',
    'config',
    'assets'
  ];
  
  dirs.forEach(dir => {
    fs.mkdirSync(path.join(portableDir, dir), { recursive: true });
  });
  
  // Copy built files
  console.log('📦 Copying built files...');
  if (fs.existsSync('dist')) {
    fs.cpSync('dist', path.join(portableDir, 'dist'), { recursive: true });
  }
  
  // Copy server files
  if (fs.existsSync('server')) {
    fs.cpSync('server', path.join(portableDir, 'server'), { recursive: true });
  }
  
  // Copy shared files
  if (fs.existsSync('shared')) {
    fs.cpSync('shared', path.join(portableDir, 'shared'), { recursive: true });
  }
  
  // Copy database
  if (fs.existsSync('ilam_mining.db')) {
    fs.copyFileSync('ilam_mining.db', path.join(portableDir, 'ilam_mining.db'));
  }
  
  // Copy data files
  if (fs.existsSync('data')) {
    fs.cpSync('data', path.join(portableDir, 'data'), { recursive: true });
  }
  
  // Copy drizzle migrations
  if (fs.existsSync('drizzle')) {
    fs.cpSync('drizzle', path.join(portableDir, 'drizzle'), { recursive: true });
  }
  
  // Create startup scripts
  createStartupScripts(portableDir);
  
  // Create configuration files
  createConfigFiles(portableDir);
  
  // Create documentation
  createDocumentation(portableDir);
  
  // Create package.json for portable
  createPortablePackageJson(portableDir);
  
  console.log('✅ Portable package created successfully!');
  console.log(`📦 Package location: ${portableDir}`);
}

// Create startup scripts for different platforms
function createStartupScripts(portableDir) {
  console.log('🔧 Creating startup scripts...');
  
  // Windows batch script
  const windowsScript = `@echo off
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
echo Checking system requirements...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if port is available
netstat -an | find "0.0.0.0:${config.port}" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Port ${config.port} is already in use
    echo Please close other applications using port ${config.port}
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

REM Start the server
cd /d "%~dp0"
node dist/server/index.js

echo.
echo Server stopped. Press any key to exit...
pause >nul
`;

  fs.writeFileSync(path.join(portableDir, 'start.bat'), windowsScript);
  
  // Linux/Mac shell script
  const unixScript = `#!/bin/bash

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

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if port is available
if lsof -Pi :${config.port} -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port ${config.port} is already in use"
    echo "Please close other applications using port ${config.port}"
    exit 1
fi

echo "✅ System requirements met"
echo ""
echo "Starting Kashif Mining Detector..."
echo ""

# Set environment variables
export NODE_ENV=production
export PORT=${config.port}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "\${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "\$SCRIPT_DIR"

# Start the server
node dist/server/index.js

echo ""
echo "Server stopped."
`;

  fs.writeFileSync(path.join(portableDir, 'start.sh'), unixScript);
  
  // Make shell script executable
  try {
    fs.chmodSync(path.join(portableDir, 'start.sh'), '755');
  } catch (error) {
    console.log('⚠️  Could not set executable permissions on start.sh');
  }
  
  // PowerShell script for Windows
  const powershellScript = `# Kashif Mining Detector - کاشف شبح حبشی
# سیستم ملی تشخیص ماینینگ غیرمجاز

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Kashif - Shabah Habashi" -ForegroundColor Yellow
Write-Host "سیستم ملی تشخیص ماینینگ غیرمجاز" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Version: ${config.version}" -ForegroundColor Green
Write-Host "Port: ${config.port}" -ForegroundColor Green
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if port is available
$portInUse = Get-NetTCPConnection -LocalPort ${config.port} -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Port ${config.port} is already in use" -ForegroundColor Yellow
    Write-Host "Please close other applications using port ${config.port}" -ForegroundColor Yellow
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

# Get the directory where the script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Start the server
node dist/server/index.js

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
`;

  fs.writeFileSync(path.join(portableDir, 'start.ps1'), powershellScript);
  
  console.log('✅ Startup scripts created');
}

// Create configuration files
function createConfigFiles(portableDir) {
  console.log('⚙️  Creating configuration files...');
  
  // Main configuration file
  const configFile = {
    app: {
      name: config.appName,
      version: config.version,
      description: config.description,
      port: config.port
    },
    database: {
      path: './ilam_mining.db',
      type: 'sqlite'
    },
    logging: {
      level: 'info',
      file: './logs/app.log',
      maxSize: '10m',
      maxFiles: 5
    },
    security: {
      sessionSecret: 'kashif-mining-detector-secret-key',
      jwtSecret: 'kashif-jwt-secret-key',
      bcryptRounds: 10
    },
    features: {
      realTimeScanning: true,
      networkAnalysis: true,
      geolocation: true,
      reporting: true,
      alerts: true
    }
  };
  
  fs.writeFileSync(
    path.join(portableDir, 'config', 'app.json'), 
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

# Security settings
ENABLE_RATE_LIMITING=true
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX_REQUESTS=100

# Database settings
DB_MIGRATIONS_PATH=./drizzle
DB_BACKUP_PATH=./data/backups

# Logging settings
LOG_MAX_SIZE=10m
LOG_MAX_FILES=5
LOG_ROTATE=true
`;
  
  fs.writeFileSync(path.join(portableDir, 'config', '.env'), envFile);
  
  // Logging configuration
  const loggingConfig = {
    level: 'info',
    format: 'combined',
    transports: [
      {
        type: 'file',
        filename: './logs/app.log',
        maxsize: 10485760, // 10MB
        maxFiles: 5,
        tailable: true
      },
      {
        type: 'file',
        filename: './logs/error.log',
        level: 'error',
        maxsize: 10485760, // 10MB
        maxFiles: 3,
        tailable: true
      }
    ]
  };
  
  fs.writeFileSync(
    path.join(portableDir, 'config', 'logging.json'), 
    JSON.stringify(loggingConfig, null, 2)
  );
  
  console.log('✅ Configuration files created');
}

// Create documentation
function createDocumentation(portableDir) {
  console.log('📚 Creating documentation...');
  
  // Main README
  const readme = `# Kashif Mining Detector - Portable

## کاشف شبح حبشی - سیستم ملی تشخیص ماینینگ غیرمجاز

### معرفی:
این نرم‌افزار یک سیستم پیشرفته برای تشخیص و نظارت بر فعالیت‌های ماینینگ رمزارز است که به صورت قابل حمل طراحی شده و بدون نیاز به نصب قابل اجرا است.

### ویژگی‌ها:
- 🔍 تشخیص دستگاه‌های ماینینگ رمزارز
- 🗺️ نقشه تعاملی با موقعیت دقیق
- 🌐 تحلیل شبکه و ترافیک
- 📊 گزارش‌گیری جامع
- 🚨 سیستم هشدار پیشرفته
- 🔐 احراز هویت امن
- 📱 رابط کاربری مدرن و واکنش‌گرا

### نیازمندی‌های سیستم:
- **سیستم‌عامل**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Node.js**: نسخه 18 یا بالاتر
- **RAM**: حداقل 4GB (توصیه شده: 8GB)
- **فضای دیسک**: حداقل 2GB
- **شبکه**: دسترسی به اینترنت

### راهنمای اجرا:

#### Windows:
1. فایل \`start.bat\` را اجرا کنید
2. یا فایل \`start.ps1\` را در PowerShell اجرا کنید

#### macOS/Linux:
1. ترمینال را باز کنید
2. به پوشه برنامه بروید
3. دستور \`./start.sh\` را اجرا کنید

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
kashif-portable/
├── dist/           # فایل‌های کامپایل شده
├── server/         # کدهای سرور
├── shared/         # فایل‌های مشترک
├── data/           # داده‌ها و پشتیبان‌ها
├── logs/           # فایل‌های لاگ
├── config/         # فایل‌های تنظیمات
├── assets/         # فایل‌های رسانه
├── ilam_mining.db  # پایگاه داده
├── start.bat       # اسکریپت راه‌اندازی Windows
├── start.sh        # اسکریپت راه‌اندازی Linux/Mac
├── start.ps1       # اسکریپت راه‌اندازی PowerShell
└── README.md       # این فایل
\`\`\`

### تنظیمات:
فایل‌های تنظیمات در پوشه \`config\` قرار دارند:
- \`app.json\`: تنظیمات اصلی برنامه
- \`.env\`: متغیرهای محیطی
- \`logging.json\`: تنظیمات لاگ‌گیری

### عیب‌یابی:

#### مشکل: پورت ${config.port} در حال استفاده است
**راه‌حل**: 
1. برنامه‌های دیگر را که از پورت ${config.port} استفاده می‌کنند ببندید
2. یا پورت را در فایل \`config/app.json\` تغییر دهید

#### مشکل: Node.js یافت نشد
**راه‌حل**:
1. Node.js را از https://nodejs.org/ دانلود و نصب کنید
2. مطمئن شوید که Node.js در PATH سیستم قرار دارد

#### مشکل: دسترسی به پایگاه داده
**راه‌حل**:
1. مطمئن شوید که فایل \`ilam_mining.db\` موجود است
2. دسترسی‌های لازم را به پوشه برنامه بدهید

### پشتیبانی:
- **ایمیل**: support@kashif.ir
- **تلفن**: +98-21-XXXXXXXX
- **وب‌سایت**: https://kashif.ir

### لایسنس:
این نرم‌افزار تحت لایسنس MIT منتشر شده است.

---
**نسخه**: ${config.version}  
**توسعه‌یافته توسط**: تیم کاشف  
**تاریخ انتشار**: ${new Date().toLocaleDateString('fa-IR')}
`;

  fs.writeFileSync(path.join(portableDir, 'README.md'), readme);
  
  // Quick start guide
  const quickStart = `# راهنمای سریع - Kashif Mining Detector

## شروع سریع:

### 1. راه‌اندازی:
- **Windows**: روی \`start.bat\` دوبار کلیک کنید
- **Linux/Mac**: در ترمینال \`./start.sh\` را اجرا کنید

### 2. دسترسی:
- مرورگر را باز کنید
- به آدرس \`http://localhost:${config.port}\` بروید

### 3. ورود:
- نام کاربری: \`admin\`
- رمز عبور: \`admin\`

### 4. تغییر رمز عبور:
- به بخش تنظیمات بروید
- رمز عبور جدید را تنظیم کنید

### 5. شروع اسکن:
- روی "شروع اسکن" کلیک کنید
- مناطق مورد نظر را انتخاب کنید
- نتایج را مشاهده کنید

---
برای اطلاعات بیشتر فایل README.md را مطالعه کنید.
`;

  fs.writeFileSync(path.join(portableDir, 'QUICK_START.md'), quickStart);
  
  // Troubleshooting guide
  const troubleshooting = `# راهنمای عیب‌یابی - Kashif Mining Detector

## مشکلات رایج و راه‌حل‌ها:

### 1. خطای "Port ${config.port} is already in use"
**علت**: پورت ${config.port} توسط برنامه دیگری استفاده می‌شود
**راه‌حل**:
- برنامه‌های دیگر را ببندید
- یا پورت را در \`config/app.json\` تغییر دهید

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

## لاگ‌ها:
فایل‌های لاگ در پوشه \`logs\` قرار دارند:
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

  fs.writeFileSync(path.join(portableDir, 'TROUBLESHOOTING.md'), troubleshooting);
  
  console.log('✅ Documentation created');
}

// Create portable package.json
function createPortablePackageJson(portableDir) {
  const portablePackageJson = {
    name: "kashif-mining-detector-portable",
    version: config.version,
    description: "Portable version of Kashif Mining Detector",
    main: "dist/server/index.js",
    scripts: {
      "start": "node dist/server/index.js",
      "start:dev": "NODE_ENV=development node dist/server/index.js"
    },
    dependencies: {
      // Minimal dependencies for portable version
      "express": "^4.21.2",
      "better-sqlite3": "^12.2.0",
      "sqlite3": "^5.1.7",
      "drizzle-orm": "^0.39.3",
      "winston": "^3.17.0",
      "dotenv": "^17.2.0"
    },
    engines: {
      "node": ">=18.0.0"
    },
    portable: true,
    platform: "cross-platform"
  };
  
  fs.writeFileSync(
    path.join(portableDir, 'package.json'), 
    JSON.stringify(portablePackageJson, null, 2)
  );
}

// Main execution
async function main() {
  try {
    console.log('🚀 Starting portable package creation...');
    console.log(`📋 Configuration:`);
    console.log(`  - App Name: ${config.appName}`);
    console.log(`  - Version: ${config.version}`);
    console.log(`  - Port: ${config.port}`);
    
    // Check if build exists
    if (!fs.existsSync('dist')) {
      console.log('🔨 Building project first...');
      execSync('npm run build', { stdio: 'inherit' });
    }
    
    createPortablePackage();
    
    console.log('🎉 Portable package created successfully!');
    console.log('📁 Package location: kashif-portable/');
    console.log('🚀 To run:');
    console.log('  Windows: Double-click start.bat');
    console.log('  Linux/Mac: ./start.sh');
    console.log('  PowerShell: .\\start.ps1');
    
  } catch (error) {
    console.error('❌ Failed to create portable package:', error);
    process.exit(1);
  }
}

// Run the main function
main(); 