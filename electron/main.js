const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
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
      console.log(`Server process exited with code ${code}`);
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
    : `file://${path.join(__dirname, '../dist/public/index.html')}`;
  
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
              message: `سرور: ${status}`,
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
              dialog.showErrorBox('خطا', `خطا در راه‌اندازی مجدد سرور: ${error.message}`);
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
              detail: `نسخه 2.0.0\nتوسعه‌یافته توسط Kashif Team\n\nاین نرم‌افزار برای تشخیص و نظارت بر فعالیت‌های ماینینگ رمزارز طراحی شده است.`
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
      `خطا در راه‌اندازی سرور:\n${error.message}\n\nلطفاً مطمئن شوید که:\n- تمام فایل‌های برنامه موجود هستند\n- پورت 5000 آزاد است\n- دسترسی‌های لازم را دارید`);
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
    `خطای غیرمنتظره رخ داده است:\n${error.message}\n\nلطفاً برنامه را مجدداً راه‌اندازی کنید.`);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  dialog.showErrorBox('خطای غیرمنتظره', 
    `خطای غیرمنتظره رخ داده است:\n${reason}\n\nلطفاً برنامه را مجدداً راه‌اندازی کنید.`);
});
