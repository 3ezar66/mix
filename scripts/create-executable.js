import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🚀 Creating Kashif Mining Detector Executables...');

// Configuration
const config = {
  appName: 'کاشف شبح حبشی',
  version: '2.0.0',
  description: 'سیستم ملی تشخیص ماینینگ غیرمجاز',
  author: 'Kashif Team',
  appId: 'com.kashif.mining-detector'
};

// Create Electron main process file
function createElectronMain() {
  console.log('⚡ Creating Electron main process...');
  
  const electronMain = `const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

let mainWindow;
let serverProcess;
let isServerRunning = false;

// Development mode detection
const isDev = process.env.NODE_ENV === 'development';

// Server startup function
function startServer() {
  return new Promise((resolve, reject) => {
    console.log('🚀 Starting Kashif Mining Detector Server...');
    
    // Determine the server entry point
    const serverPath = isDev 
      ? path.join(__dirname, '../server/index.ts')
      : path.join(__dirname, '../dist/server/index.js');
    
    // Use tsx for development, node for production
    const command = isDev ? 'npx' : 'node';
    const args = isDev ? ['tsx', serverPath] : [serverPath];
    
    serverProcess = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      shell: true,
      cwd: path.join(__dirname, '..')
    });

    serverProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log('Server:', output);
      
      // Check if server is ready
      if (output.includes('Kashif Mining Detector running on port 5000')) {
        isServerRunning = true;
        resolve();
      }
    });

    serverProcess.stderr.on('data', (data) => {
      console.error('Server Error:', data.toString());
    });

    serverProcess.on('error', (error) => {
      console.error('Failed to start server:', error);
      reject(error);
    });

    serverProcess.on('close', (code) => {
      console.log(\`Server process exited with code \${code}\`);
      isServerRunning = false;
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      if (!isServerRunning) {
        reject(new Error('Server startup timeout'));
      }
    }, 30000);
  });
}

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    icon: path.join(__dirname, 'assets/icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false,
    titleBarStyle: 'default',
    autoHideMenuBar: false
  });

  // Load the app
  const startUrl = isDev 
    ? 'http://localhost:5000' 
    : \`file://\${path.join(__dirname, '../dist/public/index.html')}\`;
  
  mainWindow.loadURL(startUrl);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Open DevTools in development
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Create menu
  createMenu();
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'فایل',
      submenu: [
        {
          label: 'باز کردن در مرورگر',
          accelerator: 'CmdOrCtrl+Shift+O',
          click: () => {
            shell.openExternal('http://localhost:5000');
          }
        },
        {
          label: 'تنظیمات',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            // TODO: Open settings dialog
          }
        },
        { type: 'separator' },
        {
          label: 'خروج',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'نمایش',
      submenu: [
        { role: 'reload', label: 'بارگذاری مجدد' },
        { role: 'forceReload', label: 'بارگذاری اجباری' },
        { role: 'toggleDevTools', label: 'ابزارهای توسعه' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'اندازه واقعی' },
        { role: 'zoomIn', label: 'بزرگنمایی' },
        { role: 'zoomOut', label: 'کوچک‌نمایی' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'تمام صفحه' }
      ]
    },
    {
      label: 'سرور',
      submenu: [
        {
          label: 'وضعیت سرور',
          click: () => {
            const status = isServerRunning ? 'در حال اجرا' : 'متوقف شده';
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'وضعیت سرور',
              message: \`سرور: \${status}\`,
              detail: isServerRunning ? 'سرور در حال اجرا روی پورت 5000' : 'سرور متوقف شده'
            });
          }
        },
        {
          label: 'راه‌اندازی مجدد سرور',
          click: async () => {
            try {
              if (serverProcess) {
                serverProcess.kill();
              }
              await startServer();
              dialog.showMessageBox(mainWindow, {
                type: 'info',
                title: 'سرور',
                message: 'سرور با موفقیت راه‌اندازی مجدد شد'
              });
            } catch (error) {
              dialog.showErrorBox('خطا', \`خطا در راه‌اندازی مجدد سرور: \${error.message}\`);
            }
          }
        }
      ]
    },
    {
      label: 'کمک',
      submenu: [
        {
          label: 'درباره کاشف شبح حبشی',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'درباره کاشف شبح حبشی',
              message: 'سیستم ملی تشخیص ماینینگ غیرمجاز',
              detail: \`نسخه ${config.version}\\nتوسعه‌یافته توسط ${config.author}\\n\\nاین نرم‌افزار برای تشخیص و نظارت بر فعالیت‌های ماینینگ رمزارز طراحی شده است.\`
            });
          }
        },
        {
          label: 'مستندات',
          click: () => {
            shell.openExternal('https://github.com/kashif-team/mining-detector');
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event handlers
app.whenReady().then(async () => {
  try {
    // Start the server first
    await startServer();
    console.log('✅ Server started successfully');
    
    // Then create the window
    createWindow();
    
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  } catch (error) {
    console.error('❌ Failed to start application:', error);
    dialog.showErrorBox('خطای راه‌اندازی', 
      \`خطا در راه‌اندازی سرور:\\n\${error.message}\\n\\nلطفاً مطمئن شوید که:\\n- تمام فایل‌های برنامه موجود هستند\\n- پورت 5000 آزاد است\\n- دسترسی‌های لازم را دارید\`);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (serverProcess) {
    console.log('🛑 Stopping server...');
    serverProcess.kill();
  }
});

// IPC handlers
ipcMain.handle('get-server-status', () => {
  return isServerRunning;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-platform', () => {
  return process.platform;
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  dialog.showErrorBox('خطای غیرمنتظره', 
    \`خطای غیرمنتظره رخ داده است:\\n\${error.message}\\n\\nلطفاً برنامه را مجدداً راه‌اندازی کنید.\`);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  dialog.showErrorBox('خطای غیرمنتظره', 
    \`خطای غیرمنتظره رخ داده است:\\n\${reason}\\n\\nلطفاً برنامه را مجدداً راه‌اندازی کنید.\`);
});
`;

  // Ensure electron directory exists
  if (!fs.existsSync('electron')) {
    fs.mkdirSync('electron', { recursive: true });
  }
  
  fs.writeFileSync('electron/main.js', electronMain);
  console.log('✅ Electron main process created');
}

// Create Electron preload script
function createElectronPreload() {
  console.log('🔧 Creating Electron preload script...');
  
  const preloadScript = `const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Server management
  getServerStatus: () => ipcRenderer.invoke('get-server-status'),
  
  // App information
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  
  // Window management
  minimize: () => ipcRenderer.send('minimize-window'),
  maximize: () => ipcRenderer.send('maximize-window'),
  close: () => ipcRenderer.send('close-window'),
  
  // File operations
  openFile: (options) => ipcRenderer.invoke('open-file', options),
  saveFile: (options) => ipcRenderer.invoke('save-file', options),
  
  // System information
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // Notifications
  showNotification: (options) => ipcRenderer.invoke('show-notification', options),
  
  // Database operations
  getDatabasePath: () => ipcRenderer.invoke('get-database-path'),
  backupDatabase: () => ipcRenderer.invoke('backup-database'),
  
  // Logging
  logInfo: (message) => ipcRenderer.invoke('log-info', message),
  logError: (message) => ipcRenderer.invoke('log-error', message),
  logWarning: (message) => ipcRenderer.invoke('log-warning', message),
  
  // Network operations
  checkPort: (port) => ipcRenderer.invoke('check-port', port),
  getNetworkInterfaces: () => ipcRenderer.invoke('get-network-interfaces'),
  
  // Security
  validateLicense: (licenseKey) => ipcRenderer.invoke('validate-license', licenseKey),
  
  // Updates
  checkForUpdates: () => ipcRenderer.invoke('check-for-updates'),
  downloadUpdate: () => ipcRenderer.invoke('download-update'),
  
  // Settings
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  
  // Hardware detection
  getSerialPorts: () => ipcRenderer.invoke('get-serial-ports'),
  getUSBDevices: () => ipcRenderer.invoke('get-usb-devices'),
  
  // Mining detection
  startMiningScan: (options) => ipcRenderer.invoke('start-mining-scan', options),
  stopMiningScan: () => ipcRenderer.invoke('stop-mining-scan'),
  getScanResults: () => ipcRenderer.invoke('get-scan-results'),
  
  // Reports
  generateReport: (options) => ipcRenderer.invoke('generate-report', options),
  exportReport: (format) => ipcRenderer.invoke('export-report', format),
  
  // Alerts
  getAlerts: () => ipcRenderer.invoke('get-alerts'),
  acknowledgeAlert: (alertId) => ipcRenderer.invoke('acknowledge-alert', alertId),
  
  // Maps and Geolocation
  getMapData: () => ipcRenderer.invoke('get-map-data'),
  updateLocation: (coordinates) => ipcRenderer.invoke('update-location', coordinates),
  
  // Real-time data
  subscribeToUpdates: (callback) => {
    ipcRenderer.on('real-time-update', callback);
  },
  unsubscribeFromUpdates: () => {
    ipcRenderer.removeAllListeners('real-time-update');
  },
  
  // Authentication
  login: (credentials) => ipcRenderer.invoke('login', credentials),
  logout: () => ipcRenderer.invoke('logout'),
  getCurrentUser: () => ipcRenderer.invoke('get-current-user'),
  
  // Permissions
  requestPermissions: (permissions) => ipcRenderer.invoke('request-permissions', permissions),
  checkPermissions: (permissions) => ipcRenderer.invoke('check-permissions', permissions),
  
  // Performance
  getPerformanceMetrics: () => ipcRenderer.invoke('get-performance-metrics'),
  optimizePerformance: () => ipcRenderer.invoke('optimize-performance'),
  
  // Backup and restore
  createBackup: () => ipcRenderer.invoke('create-backup'),
  restoreBackup: (backupPath) => ipcRenderer.invoke('restore-backup', backupPath),
  
  // Maintenance
  cleanupLogs: () => ipcRenderer.invoke('cleanup-logs'),
  repairDatabase: () => ipcRenderer.invoke('repair-database'),
  resetSettings: () => ipcRenderer.invoke('reset-settings'),
  
  // Help and support
  openHelp: () => ipcRenderer.invoke('open-help'),
  contactSupport: () => ipcRenderer.invoke('contact-support'),
  submitFeedback: (feedback) => ipcRenderer.invoke('submit-feedback', feedback)
});

// Handle window events
window.addEventListener('DOMContentLoaded', () => {
  // Add any initialization code here
  console.log('Kashif Mining Detector - Preload script loaded');
  
  // Inject custom styles for better integration
  const style = document.createElement('style');
  style.textContent = \`
    /* Custom styles for Electron app */
    body {
      -webkit-app-region: drag;
      user-select: none;
    }
    
    /* Make form elements and buttons non-draggable */
    input, button, select, textarea, a, [role="button"] {
      -webkit-app-region: no-drag;
      user-select: text;
    }
    
    /* Custom scrollbar for Electron */
    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    
    ::-webkit-scrollbar-track {
      background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
      background: #888;
      border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
      background: #555;
    }
    
    /* Prevent text selection on UI elements */
    .no-select {
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }
    
    /* Custom focus styles */
    *:focus {
      outline: 2px solid #007acc;
      outline-offset: 2px;
    }
  \`;
  document.head.appendChild(style);
});

// Handle errors
window.addEventListener('error', (event) => {
  console.error('Renderer error:', event.error);
  // You can send error reports to the main process here
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  // You can send error reports to the main process here
});
`;

  fs.writeFileSync('electron/preload.js', preloadScript);
  console.log('✅ Electron preload script created');
}

// Create Electron Builder configuration
function createElectronBuilderConfig() {
  console.log('⚙️  Creating Electron Builder configuration...');
  
  const builderConfig = {
    appId: config.appId,
    productName: config.appName,
    directories: {
      output: "dist-electron",
      buildResources: "electron/assets"
    },
    files: [
      "dist/**/*",
      "server/**/*",
      "shared/**/*",
      "electron/**/*",
      "package.json",
      "ilam_mining.db",
      "data/**/*",
      "drizzle/**/*",
      "!**/node_modules/*/{CHANGELOG.md,README.md,README,readme.md,readme}",
      "!**/node_modules/*/{test,__tests__,tests,powered-test,example,examples}",
      "!**/node_modules/*.d.ts",
      "!**/node_modules/.bin",
      "!**/*.{iml,o,hprof,orig,pyc,pyo,rbc,swp,csproj,sln,xproj}",
      "!.editorconfig",
      "!**/._*",
      "!**/{.DS_Store,.git,.hg,.svn,CVS,RCS,SCCS,.gitignore,.gitattributes}",
      "!**/{__pycache__,thumbs.db,.flowconfig,.idea,.vs,.nyc_output}",
      "!**/{appveyor.yml,.travis.yml,circle.yml}",
      "!**/{npm-debug.log,yarn.lock,.yarn-integrity,.yarn-metadata.json}"
    ],
    extraResources: [
      {
        "from": "server/services",
        "to": "server/services",
        "filter": ["**/*"]
      },
      {
        "from": "shared",
        "to": "shared",
        "filter": ["**/*"]
      },
      {
        "from": "data",
        "to": "data",
        "filter": ["**/*"]
      },
      {
        "from": "drizzle",
        "to": "drizzle",
        "filter": ["**/*"]
      },
      {
        "from": "ilam_mining.db",
        "to": "ilam_mining.db"
      }
    ],
    win: {
      target: [
        {
          target: "nsis",
          arch: ["x64", "ia32"]
        },
        {
          target: "portable",
          arch: ["x64", "ia32"]
        }
      ],
      icon: "electron/assets/icon.ico",
      requestedExecutionLevel: "requireAdministrator",
      artifactName: "${productName}-${version}-${arch}.${ext}",
      publisherName: config.author,
      verifyUpdateCodeSignature: false,
      signingHashAlgorithms: ["sha256"]
    },
    nsis: {
      oneClick: false,
      allowToChangeInstallationDirectory: true,
      createDesktopShortcut: true,
      createStartMenuShortcut: true,
      shortcutName: config.appName,
      installerIcon: "electron/assets/icon.ico",
      uninstallerIcon: "electron/assets/icon.ico",
      installerHeaderIcon: "electron/assets/icon.ico",
      deleteAppDataOnUninstall: false,
      license: "LICENSE",
      language: "1033",
      installerLanguages: ["en-US", "fa-IR"],
      perMachine: true,
      runAfterFinish: true,
      menuCategory: config.appName
    },
    portable: {
      artifactName: "${productName}-${version}-portable-${arch}.${ext}",
      requestExecutionLevel: "requireAdministrator"
    },
    mac: {
      target: [
        {
          target: "dmg",
          arch: ["x64", "arm64"]
        },
        {
          target: "zip",
          arch: ["x64", "arm64"]
        }
      ],
      icon: "electron/assets/icon.icns",
      category: "public.app-category.utilities",
      hardenedRuntime: true,
      gatekeeperAssess: false,
      artifactName: "${productName}-${version}-${arch}.${ext}",
      darkModeSupport: true
    },
    dmg: {
      title: "${productName} ${version}",
      icon: "electron/assets/icon.icns",
      window: {
        width: 540,
        height: 380
      },
      contents: [
        {
          x: 130,
          y: 220
        },
        {
          x: 410,
          y: 220,
          type: "link",
          path: "/Applications"
        }
      ],
      sign: false
    },
    linux: {
      target: [
        {
          target: "AppImage",
          arch: ["x64", "ia32", "armv7l", "arm64"]
        },
        {
          target: "deb",
          arch: ["x64", "ia32", "armv7l", "arm64"]
        },
        {
          target: "rpm",
          arch: ["x64", "ia32", "armv7l", "arm64"]
        }
      ],
      icon: "electron/assets/icon.png",
      category: "Utility",
      artifactName: "${productName}-${version}-${arch}.${ext}",
      desktop: {
        Name: config.appName,
        Comment: config.description,
        Keywords: "mining;cryptocurrency;detection;network;security",
        StartupNotify: true,
        Terminal: false,
        Type: "Application"
      }
    },
    appImage: {
      artifactName: "${productName}-${version}-${arch}.${ext}",
      category: "Utility"
    },
    deb: {
      artifactName: "${productName}-${version}-${arch}.${ext}",
      depends: [
        "libgtk-3-0",
        "libnotify4",
        "libnss3",
        "libxss1",
        "libxtst6",
        "xdg-utils",
        "libatspi2.0-0",
        "libdrm2",
        "libgbm1",
        "libasound2"
      ],
      packageCategory: "utils",
      priority: "optional"
    },
    rpm: {
      artifactName: "${productName}-${version}-${arch}.${ext}",
      depends: [
        "gtk3",
        "libnotify",
        "nss",
        "libXScrnSaver",
        "libXtst",
        "xdg-utils",
        "at-spi2-atk",
        "libdrm",
        "mesa-libgbm",
        "alsa-lib"
      ]
    },
    asar: true,
    asarUnpack: [
      "node_modules/better-sqlite3/**/*",
      "node_modules/serialport/**/*",
      "server/services/**/*"
    ],
    forceCodeSigning: false,
    electronVersion: "28.0.0",
    buildVersion: config.version,
    compression: "maximum",
    removePackageScripts: true,
    removePackageKeywords: true
  };
  
  fs.writeFileSync('electron-builder.json', JSON.stringify(builderConfig, null, 2));
  console.log('✅ Electron Builder configuration created');
}

// Create placeholder assets
function createPlaceholderAssets() {
  console.log('🎨 Creating placeholder assets...');
  
  // Ensure assets directory exists
  if (!fs.existsSync('electron/assets')) {
    fs.mkdirSync('electron/assets', { recursive: true });
  }
  
  // Create placeholder icon files
  const iconFiles = [
    'electron/assets/icon.ico',
    'electron/assets/icon.icns',
    'electron/assets/icon.png'
  ];
  
  iconFiles.forEach(iconFile => {
    if (!fs.existsSync(iconFile)) {
      // Create a simple placeholder
      const placeholderContent = 'Placeholder icon file - Replace with actual icon';
      fs.writeFileSync(iconFile, placeholderContent);
      console.log(`✅ Created placeholder: ${iconFile}`);
    }
  });
  
  console.log('✅ Placeholder assets created');
}

// Build Electron executables
async function buildElectronExecutables() {
  console.log('🏗️ Building Electron executables...');
  
  try {
    // Build for all platforms
    console.log('🔨 Building for Windows...');
    execSync('npm run electron:build:win', { stdio: 'inherit' });
    
    console.log('🍎 Building for macOS...');
    execSync('npm run electron:build:mac', { stdio: 'inherit' });
    
    console.log('🐧 Building for Linux...');
    execSync('npm run electron:build:linux', { stdio: 'inherit' });
    
    console.log('✅ All Electron executables built successfully!');
    
    // List generated files
    const distDir = 'dist-electron';
    if (fs.existsSync(distDir)) {
      const files = fs.readdirSync(distDir);
      console.log('📁 Generated executables:');
      files.forEach(file => {
        console.log(`  - ${file}`);
      });
    }
    
  } catch (error) {
    console.error('❌ Failed to build Electron executables:', error.message);
    throw error;
  }
}

// Create documentation for executables
function createExecutableDocumentation() {
  console.log('📚 Creating executable documentation...');
  
  const readme = `# Kashif Mining Detector - Executables

## کاشف شبح حبشی - فایل‌های اجرایی

### معرفی:
این پوشه شامل فایل‌های اجرایی Kashif Mining Detector برای سیستم‌عامل‌های مختلف است.

### فایل‌های موجود:

#### Windows:
- **Kashif-Mining-Detector-Setup.exe**: نصب‌کننده Windows
- **کاشف شبح حبشی-2.0.0-portable-x64.exe**: نسخه قابل حمل 64-bit
- **کاشف شبح حبشی-2.0.0-portable-ia32.exe**: نسخه قابل حمل 32-bit

#### macOS:
- **کاشف شبح حبشی-2.0.0.dmg**: نصب‌کننده macOS
- **کاشف شبح حبشی-2.0.0-mac.zip**: نسخه فشرده macOS

#### Linux:
- **کاشف شبح حبشی-2.0.0.AppImage**: نسخه AppImage (قابل اجرا در اکثر توزیع‌های Linux)
- **کاشف شبح حبشی-2.0.0.deb**: بسته Debian/Ubuntu
- **کاشف شبح حبشی-2.0.0.rpm**: بسته Red Hat/Fedora

### راهنمای نصب:

#### Windows:
1. فایل **Kashif-Mining-Detector-Setup.exe** را دانلود کنید
2. روی فایل دوبار کلیک کنید
3. مراحل نصب را دنبال کنید
4. برنامه از منوی Start قابل دسترسی خواهد بود

#### macOS:
1. فایل **کاشف شبح حبشی-2.0.0.dmg** را دانلود کنید
2. فایل DMG را باز کنید
3. برنامه را به پوشه Applications بکشید
4. برنامه از Launchpad قابل دسترسی خواهد بود

#### Linux:
1. فایل **کاشف شبح حبشی-2.0.0.AppImage** را دانلود کنید
2. فایل را قابل اجرا کنید: \`chmod +x کاشف شبح حبشی-2.0.0.AppImage\`
3. فایل را اجرا کنید: \`./کاشف شبح حبشی-2.0.0.AppImage\`

### نسخه قابل حمل:
برای استفاده بدون نصب، از فایل‌های portable استفاده کنید:
- Windows: **کاشف شبح حبشی-2.0.0-portable-x64.exe**
- macOS: **کاشف شبح حبشی-2.0.0-mac.zip**
- Linux: **کاشف شبح حبشی-2.0.0.AppImage**

### نیازمندی‌های سیستم:

#### Windows:
- Windows 10 یا بالاتر
- حداقل 4GB RAM
- حداقل 2GB فضای دیسک

#### macOS:
- macOS 10.14 (Mojave) یا بالاتر
- حداقل 4GB RAM
- حداقل 2GB فضای دیسک

#### Linux:
- Ubuntu 18.04+ یا توزیع‌های مشابه
- حداقل 4GB RAM
- حداقل 2GB فضای دیسک

### ویژگی‌ها:
- 🔍 تشخیص دستگاه‌های ماینینگ رمزارز
- 🗺️ نقشه تعاملی با موقعیت دقیق
- 🌐 تحلیل شبکه و ترافیک
- 📊 گزارش‌گیری جامع
- 🚨 سیستم هشدار پیشرفته
- 🔐 احراز هویت امن
- 📱 رابط کاربری مدرن و واکنش‌گرا

### عیب‌یابی:

#### مشکل: فایل اجرا نمی‌شود
**راه‌حل**:
1. مطمئن شوید که فایل مناسب سیستم‌عامل خود را دانلود کرده‌اید
2. آنتی‌ویروس را موقتاً غیرفعال کنید
3. فایل را با دسترسی Administrator اجرا کنید

#### مشکل: خطای "Permission denied" در Linux
**راه‌حل**:
\`\`\`bash
chmod +x کاشف شبح حبشی-2.0.0.AppImage
\`\`\`

#### مشکل: خطای "Gatekeeper" در macOS
**راه‌حل**:
1. System Preferences > Security & Privacy
2. روی "Open Anyway" کلیک کنید

### پشتیبانی:
- **ایمیل**: support@kashif.ir
- **تلفن**: +98-21-XXXXXXXX
- **وب‌سایت**: https://kashif.ir

### لایسنس:
این نرم‌افزار تحت لایسنس MIT منتشر شده است.

---
**نسخه**: ${config.version}  
**توسعه‌یافته توسط**: ${config.author}  
**تاریخ انتشار**: ${new Date().toLocaleDateString('fa-IR')}
`;

  fs.writeFileSync('dist-electron/README.md', readme);
  console.log('✅ Executable documentation created');
}

// Main execution
async function main() {
  try {
    console.log('🚀 Starting Electron executable creation...');
    console.log(`📋 Configuration:`);
    console.log(`  - App Name: ${config.appName}`);
    console.log(`  - Version: ${config.version}`);
    console.log(`  - App ID: ${config.appId}`);
    
    // Check if build exists
    if (!fs.existsSync('dist')) {
      console.log('🔨 Building project first...');
      execSync('npm run build', { stdio: 'inherit' });
    }
    
    // Create Electron files
    createElectronMain();
    createElectronPreload();
    createElectronBuilderConfig();
    createPlaceholderAssets();
    
    // Build executables
    await buildElectronExecutables();
    
    // Create documentation
    createExecutableDocumentation();
    
    console.log('🎉 Electron executables created successfully!');
    console.log('📁 Check the dist-electron directory for the generated executables');
    console.log('📚 Documentation available in dist-electron/README.md');
    
  } catch (error) {
    console.error('❌ Failed to create Electron executables:', error);
    process.exit(1);
  }
}

// Run the main function
main(); 