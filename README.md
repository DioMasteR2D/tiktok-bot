# DioMasteR2D TikTok Desk

A lightweight, password-protected web dashboard for organizing TikTok video links and recording performance metrics manually.

## What it does
- Add and organize TikTok video URLs.
- Store a title/note for each video.
- Record followers, views, likes, comments and shares over time.
- View each video's metric history and latest recorded values.
- Password-protected dashboard with CSRF-protected forms.
- SQLite database stored at `/var/data/tiktok_dashboard.db` when deployed with the included Render disk.

## What it does not do
This dashboard does **not** automate follows, followers, likes, views, comments, shares, CAPTCHA solving, or actions through Zefoy. It does not ask for or store your TikTok password. Metrics are entered manually. Official TikTok API integration can be added later only with the appropriate approved developer app and permissions.

The original upstream `bot.py` is retained for reference but is not used by this web app or by the Render start command. Do not run it as a way to manufacture engagement.

## Deploy to Render
1. Push this repository to GitHub.
2. In Render, choose **New + → Blueprint** and connect `DioMasteR2D/tiktok-bot`.
3. Render reads `render.yaml`. Enter a strong value for `DASHBOARD_PASSWORD` when prompted.
4. The Blueprint uses a Starter web service and a 1 GB persistent disk so SQLite data survives redeploys. These are paid Render resources; check current pricing before confirming.
5. After deployment, open the generated `.onrender.com` URL and sign in with your password.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DASHBOARD_PASSWORD='use-a-long-private-password'
export SECRET_KEY='replace-with-a-long-random-secret'
python app.py
```
Open http://localhost:10000.

## Health check
`GET /health` returns a small JSON status response and does not expose account data.
