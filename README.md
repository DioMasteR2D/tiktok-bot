# FreeLLMAPI Android Companion

Android APK frontend for the **local** FreeLLMAPI dashboard. This is a companion app, **not a standalone Node.js backend**. It requires the official FreeLLMAPI server running separately in Termux on the same phone. No external cloud or Render is used.

## Set up Termux (from F-Droid)

```sh
pkg update && pkg upgrade -y
pkg install -y nodejs-lts git
git clone https://github.com/tashfeenahmed/freellmapi.git
cd freellmapi
npm install --no-audit --no-fund
npm run dev
```

Once server is running, open this APK. Dashboard uses `http://localhost:5173` and API `http://localhost:3001/v1`.

## Build APK

Push to the default branch `main`. GitHub Actions > Build Android APK > Run workflow. Download `FreeLLMAPI-Android-debug-apk` from the successful workflow run's artifacts and install `app-debug.apk` on Android.

### Limitations
- Does not install, embed, start or manage Node.js or FreeLLMAPI automatically.
- Termux must stay running for dashboard/API to work.
- This Android app has not been compiled or device-tested locally. GitHub Actions workflow is provided for actual build verification.
- Use only on trusted networks; avoid exposing development servers publicly.
