# Daily Standup Webhook Server

Webhook server để nhận submissions từ form và post vào Telegram topic.

## Deploy to Railway

1. Vào https://railway.app
2. Sign up với GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Chọn repo này (hoặc deploy from local directory)
5. Railway sẽ tự động detect Python và deploy
6. Copy URL public (dạng: https://xxx.up.railway.app)

## Environment Variables

Không cần set gì - all hardcoded trong code.

## Usage

POST request to: `https://your-railway-url.up.railway.app/`

Body:
```json
{
  "user": "Tên người dùng",
  "date": "2026-02-07",
  "project": "FS.XLite.Develop",
  "yesterday": "...",
  "today": "...",
  "ontrack": "yes",
  "blockers": "..."
}
```
