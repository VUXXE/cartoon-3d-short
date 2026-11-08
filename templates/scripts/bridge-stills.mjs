// usage: node scripts/bridge-stills.mjs <outPrefix> <frame,frame,...> [scale]
// BRIDGE_ENTRY=src/sandboxes/<name>/index.tsx renders a sandbox copy instead of the main project entry.
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

// Prevent filling RAM-based /tmp (tmpfs on Arch Linux) with Remotion bundles (~1.3 GB each)
const defaultTmp = process.platform === "win32"
  ? path.join(os.homedir(), "AppData", "Local", "Temp", "remotion-tmp")
  : path.join(os.homedir(), ".cache", "remotion-tmp");

const remotionTmp = process.env.REMOTION_TMP || defaultTmp;
fs.mkdirSync(remotionTmp, { recursive: true });
process.env.TEMP = process.env.TMP = process.env.REMOTION_TMP = remotionTmp;

function resolveBrowser() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) return process.env.PUPPETEER_EXECUTABLE_PATH;
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;

  const candidates = process.platform === "win32"
    ? [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
      ]
    : process.platform === "darwin"
    ? [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
      ]
    : [
        path.join(os.homedir(), ".local/bin/google-chrome"),
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser"
      ];

  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return undefined; // Let Remotion find installed browser
}

const [prefix, frames, scale = "0.5"] = process.argv.slice(2);
const browserExecutable = resolveBrowser();

// Always enforce GPU hardware acceleration when available
const glBackend = process.env.CHROME_GL || (process.platform === "win32" ? "angle" : "egl");
const chromiumOptions = {
  gl: glBackend,
  headless: true,
  args: [
    "--enable-gpu",
    "--ignore-gpu-blocklist",
    "--enable-gpu-rasterization",
    "--enable-zero-copy",
    process.platform === "win32" ? "--use-gl=angle" : "--use-gl=egl"
  ]
};

console.log(`Using browser: ${browserExecutable || "default puppeteer"} (gl: ${chromiumOptions.gl}, GPU hardware acceleration enabled)`);
console.log(`Temp directory: ${remotionTmp}`);

const serveUrl = await bundle({
  entryPoint: path.resolve(process.env.BRIDGE_ENTRY || "src/index.ts"),
  publicDir: path.resolve("public")
});

const composition = await selectComposition({
  serveUrl,
  id: process.env.REMOTION_COMPOSITION || "BridgeShort",
  browserExecutable,
  chromiumOptions
});

const onBrowserLog = (l) => {
  if (l.type === "error" || l.type === "warning") {
    console.log(`[${l.type}]`, l.text.slice(0, 300));
  }
};

for (const f of frames.split(",").map(Number)) {
  const t0 = Date.now();
  await renderStill({
    composition,
    serveUrl,
    frame: f,
    output: `${prefix}${f}.jpg`,
    imageFormat: "jpeg",
    jpegQuality: 88,
    scale: Number(scale),
    browserExecutable,
    chromiumOptions,
    timeoutInMilliseconds: 180000,
    onBrowserLog
  });
  console.log("still", f, ((Date.now() - t0) / 1000).toFixed(1) + "s");
}
