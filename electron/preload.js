const { contextBridge, ipcRenderer } = require('electron');

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
  style.textContent = `
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
  `;
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
