const { app, BrowserWindow, shell } = require("electron");
const path = require("path");
const os = require("os");
const fs = require("fs");
const http = require("http");

// Data mappen in de home directory
const DATA_DIR   = path.join(os.homedir(), ".collage-app");
const UPLOAD_DIR = path.join(DATA_DIR, "uploads");
const OUTPUT_DIR = path.join(DATA_DIR, "output");

fs.mkdirSync(UPLOAD_DIR, { recursive: true });
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

// Geef server.js de juiste paden mee via omgevingsvariabelen
process.env.COLLAGE_DATA_DIR = DATA_DIR;

// Start de Express server in hetzelfde proces
require("./server");

let hoofdvenster;

function wachtOpServer(callback, pogingen = 0) {
  if (pogingen > 50) return;
  http.get("http://localhost:3001", () => callback())
    .on("error", () => setTimeout(() => wachtOpServer(callback, pogingen + 1), 100));
}

function maakVenster() {
  hoofdvenster = new BrowserWindow({
    width: 1100,
    height: 800,
    minWidth: 820,
    minHeight: 600,
    title: "Collage Maker",
    backgroundColor: "#0f0f0f",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  hoofdvenster.loadURL("http://localhost:3001");

  // Externe links openen in de browser, niet in de app
  hoofdvenster.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  hoofdvenster.on("closed", () => { hoofdvenster = null; });
}

app.whenReady().then(() => {
  wachtOpServer(maakVenster);
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (hoofdvenster === null) maakVenster();
});
