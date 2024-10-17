import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import fs from 'fs'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import { spawn } from 'child_process';

function createWindow() {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the lopathcal html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

let pythonProcess = null

let server_port = import.meta.env.VITE_SERVER_PORT

const startPythonServer = () => {
  try {
    // 判断是否是生产环境（打包后的环境）
    const basePath = app.isPackaged
    ? join(process.resourcesPath, 'app.asar.unpacked', 'resources')  // 打包后路径
    : join('resources'); // 开发环境路径

    // 可执行文件的完整路径
    const pyPath = join(basePath, 'app.exe');
    const jsonPath = join(basePath, 'sources.json');
    pythonProcess = spawn(
      pyPath,
      [server_port, jsonPath]);
      pythonProcess.stdout.on('data', (data) => {
        console.log(`${data}`);
      });
    //pythonProcess.unref()
    
      pythonProcess.stderr.on('data', (data) => {
        console.error(`${data}`);
      });
    
      pythonProcess.on('close', (code) => {
        console.log(`${code}`);
      });
  } catch (err) {
    console.error('Failed to start Python server:', err);
    return;
  }
}

function stopPythonServer() {
  if (pythonProcess) {
    pythonProcess.kill(); // 杀掉 Python 进程
    console.log('Python process terminated');
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  startPythonServer()
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // IPC test
  ipcMain.on('ping', () => console.log('pong'))

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  stopPythonServer();
});

ipcMain.handle('read-sources-json', (event) => {
  const filePath = app.isPackaged
  ? join(process.resourcesPath, 'app.asar.unpacked', 'resources', 'sources.json')  // 打包后路径
  : join('resources', 'sources.json'); // 开发环境路径
  try {
    const data = fs.readFileSync(filePath, 'utf-8');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('write-sources-json', (event, { content }) => {
  const filePath = app.isPackaged
  ? join(process.resourcesPath, 'app.asar.unpacked', 'resources', 'sources.json')  // 打包后路径
  : join('resources', 'sources.json'); // 开发环境路径
  try {
    fs.writeFileSync(filePath, content, 'utf-8');
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// In this file you can include the rest of your app"s specific main process
// code. You can also put them in separate files and require them here.
