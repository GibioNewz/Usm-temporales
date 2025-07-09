const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      // Necesario para usar APIs de Node en el renderer
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  win.loadFile(path.join(__dirname, 'index.html'));
}

app.whenReady().then(createWindow);

// En macOS suele reabrir la ventana si se hace clic en el dock
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
