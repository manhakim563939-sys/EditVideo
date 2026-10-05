# render-test

Standalone render check: Remotion 4.0.532 + Node.js 22 + ffmpeg. All dependencies stay in this folder.

```bash
npm install
npm run render   # -> out/render-test.mp4 (1920x1080, 30fps, 150 frames, 5.0s, H.264)
```

`remotion.config.ts` points Remotion at the Chromium headless shell already on the machine
(`/opt/pw-browsers/...`). On another computer, remove that line and Remotion downloads its own browser.
