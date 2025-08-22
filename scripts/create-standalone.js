import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

console.log('🚀 Creating standalone Kashif Mining Detector...');

// Ensure dist directory exists
if (!fs.existsSync('dist')) {
  console.error('❌ Dist directory not found. Run "npm run build" first.');
  process.exit(1);
}

// Create standalone package directory
const packageDir = 'kashif-standalone';
if (fs.existsSync(packageDir)) {
  fs.rmSync(packageDir, { recursive: true });
}
fs.mkdirSync(packageDir);

// Copy necessary files
console.log('📁 Copying files...');

// Copy dist files
fs.cpSync('dist', path.join(packageDir, 'dist'), { recursive: true });

// Copy package.json
fs.copyFileSync('package.json', path.join(packageDir, 'package.json'));

// Copy database
if (fs.existsSync('ilam_mining.db')) {
  fs.copyFileSync('ilam_mining.db', path.join(packageDir, 'ilam_mining.db'));
}

// Copy server services
if (fs.existsSync('server/services')) {
  fs.cpSync('server/services', path.join(packageDir, 'server/services'), { recursive: true });
}

// Copy shared files
if (fs.existsSync('shared')) {
  fs.cpSync('shared', path.join(packageDir, 'shared'), { recursive: true });
}

// Create startup script
const startupScript = `@echo off
echo ========================================
echo Kashif - Shabah Habashi
echo سیستم ملی تشخیص ماینینگ غیرمجاز
echo ========================================
echo.
echo Starting server...
node dist/server/index.js
pause
`;

fs.writeFileSync(path.join(packageDir, 'start.bat'), startupScript);

// Create README
const readme = `# Kashif - Shabah Habashi

## سیستم ملی تشخیص ماینینگ غیرمجاز

### راهنمای اجرا:

1. فایل start.bat را اجرا کنید
2. مرورگر را باز کرده و به آدرس http://localhost:5000 بروید
3. با نام کاربری: admin و رمز عبور: admin وارد شوید

### ویژگی‌ها:
- تشخیص دستگاه‌های ماینینگ رمزارز
- نقشه تعاملی با موقعیت دقیق
- تحلیل شبکه و ترافیک
- گزارش‌گیری جامع
- رابط کاربری پیشرفته

### پشتیبانی:
برای پشتیبانی با تیم فنی تماس بگیرید.
`;

fs.writeFileSync(path.join(packageDir, 'README.md'), readme);

console.log('✅ Standalone package created successfully!');
console.log(`📦 Package location: ${packageDir}`);
console.log('🚀 Run start.bat to launch the application'); 