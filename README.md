# FreeLLMAPI Android Companion

This Android APK is a companion launcher for the official FreeLLMAPI project. The Node.js server runs locally in Termux on the same phone. It does not use Render or a remote server.

## One-time phone setup
1. Install **Termux** from F-Droid: https://f-droid.org/packages/com.termux/
2. Open Termux once and complete its initial setup.
3. In Termux Settings, enable **Allow external apps** (required for the companion app to send the start command).
4. Open FreeLLMAPI and tap **Start FreeLLMAPI in Termux**. The first run installs Node.js LTS and Git, clones the official project, installs npm dependencies, and starts its development server.
5. Keep the Termux session running. Return to FreeLLMAPI and tap **Open dashboard**.

Dashboard: http://localhost:5173  
Local API: http://localhost:3001/v1

## Automatic behavior and limitations
- Tapping Start sends the setup/start command to Termux. First installation can take several minutes and needs an internet connection.
- Termux is a separate app installed from F-Droid; it is not bundled inside this APK.
- Android battery/background restrictions may stop long-running processes. Keep Termux running and exclude it from battery optimization if Android offers that setting.
- Starting automatically after a device reboot is not enabled by this companion app. Termux:Boot is a separate optional add-on and must be configured separately.
- This project must be built and tested through GitHub Actions and on the target phone before it can be called verified.

## Build
GitHub Actions builds a debug APK on pushes to main. Download the `FreeLLMAPI-Android-debug-apk` artifact from a successful workflow run.
