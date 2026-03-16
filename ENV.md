# 🔧 Environment Variables Configuration

Hướng dẫn cấu hình biến môi trường cho Daily Standup Webhook.

## 📋 Available Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `8080` | HTTP server port |
| `BOT_TOKEN` | No | `8305092853:...` | Telegram bot token |
| `CHAT_ID` | No | `-1003773551774` | Telegram chat/group ID |
| `THREAD_ID` | No | `7` | Telegram topic/thread ID |
| `SHEETS_URL` | No | `https://script.google...` | Google Sheets webhook URL |

**Note:** Tất cả variables đều có default values, nhưng anh nên override khi deploy cho projects khác.

## 🎯 Use Cases

### 1. Default Configuration (XLite Project)

Không cần set gì, sử dụng default values:

```bash
docker run -d \
  --name daily-standup-webhook \
  -p 8080:8080 \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

### 2. Custom Configuration (ApecFinance Project)

Override cho project khác:

```bash
docker run -d \
  --name daily-standup-apecfinance \
  -p 8081:8080 \
  -e BOT_TOKEN="8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q" \
  -e CHAT_ID="-1003853347044" \
  -e THREAD_ID="2" \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

### 3. Using .env File (Recommended for Production)

Tạo file `.env`:

```env
PORT=8080
BOT_TOKEN=8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q
CHAT_ID=-1003773551774
THREAD_ID=7
SHEETS_URL=https://script.google.com/macros/s/xxx/exec
```

Deploy với Docker:

```bash
docker run -d \
  --name daily-standup-webhook \
  -p 8080:8080 \
  --env-file .env \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

Deploy với Docker Compose:

```yaml
# docker-compose.yml
services:
  daily-standup-webhook:
    image: registry.fourier.group/bot/daily-standup-webhook:latest
    env_file:
      - .env
    ports:
      - "8080:8080"
```

```bash
docker-compose up -d
```

## 🔐 Security Best Practices

### 1. Never commit .env files

Add to `.gitignore`:

```gitignore
.env
.env.*
!.env.example
```

### 2. Use secrets management in production

**Docker Swarm:**

```bash
echo "8305092853:AAF..." | docker secret create bot_token -
```

```yaml
services:
  webhook:
    secrets:
      - bot_token
    environment:
      BOT_TOKEN_FILE: /run/secrets/bot_token
```

**Kubernetes:**

```bash
kubectl create secret generic webhook-secrets \
  --from-literal=bot-token="8305092853:AAF..." \
  --from-literal=chat-id="-1003773551774"
```

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: webhook
    env:
    - name: BOT_TOKEN
      valueFrom:
        secretKeyRef:
          name: webhook-secrets
          key: bot-token
```

### 3. Rotate credentials regularly

- Update bot token quarterly
- Monitor for unauthorized access
- Use read-only tokens where possible

## 🚀 Multi-Project Setup

Deploy multiple instances cho nhiều projects:

### XLite Project (Port 8080)

```bash
docker run -d \
  --name standup-xlite \
  -p 8080:8080 \
  -e CHAT_ID="-1003773551774" \
  -e THREAD_ID="7" \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

### ApecFinance Project (Port 8081)

```bash
docker run -d \
  --name standup-apecfinance \
  -p 8081:8080 \
  -e CHAT_ID="-1003853347044" \
  -e THREAD_ID="2" \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

### AI Development Project (Port 8082)

```bash
docker run -d \
  --name standup-ai-dev \
  -p 8082:8080 \
  -e CHAT_ID="-1003873043927" \
  -e THREAD_ID="12" \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

## 📊 Verification

### Check current configuration

```bash
# View environment variables
docker exec daily-standup-webhook env | grep -E "BOT_TOKEN|CHAT_ID|THREAD_ID|PORT"

# Check if using custom config
docker inspect daily-standup-webhook | grep -A 20 "Env"
```

### Test with different configs

```bash
# Test POST to specific instance
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "user": "Test XLite",
    "date": "2026-03-16",
    "project": "XLite",
    "yesterday": "Test",
    "today": "Test",
    "ontrack": "yes",
    "blockers": "None"
  }'

curl -X POST http://localhost:8081 \
  -H "Content-Type: application/json" \
  -d '{
    "user": "Test ApecFinance",
    "date": "2026-03-16",
    "project": "ApecFinance",
    "yesterday": "Test",
    "today": "Test",
    "ontrack": "yes",
    "blockers": "None"
  }'
```

## 🔄 Update Configuration

### Without recreating container

```bash
# Stop container
docker stop daily-standup-webhook

# Update .env file
nano .env

# Start container (will load new .env)
docker start daily-standup-webhook
```

### With container recreation

```bash
# Update .env
nano .env

# Recreate container
docker stop daily-standup-webhook
docker rm daily-standup-webhook
docker-compose up -d
```

## 🐛 Troubleshooting

### Bot token invalid

```bash
# Check bot token format
docker exec daily-standup-webhook env | grep BOT_TOKEN
# Should be: 10-digit:35-character

# Test bot token
curl "https://api.telegram.org/bot${BOT_TOKEN}/getMe"
```

### Wrong chat ID

```bash
# Verify chat ID
# Forward message from group to @userinfobot
# Or check manually:
curl "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates"
```

### Environment not loading

```bash
# Check if .env file exists
ls -la .env

# Check file permissions
chmod 600 .env

# Verify docker-compose.yml has env_file configured
cat docker-compose.yml | grep -A 2 env_file
```

## 📝 Examples

### Complete .env file

```env
# Server
PORT=8080

# Telegram - XLite Project
BOT_TOKEN=8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q
CHAT_ID=-1003773551774
THREAD_ID=7

# Google Sheets Backup
SHEETS_URL=https://script.google.com/macros/s/AKfycbwNXKBxViab5KUkNx8q69NCF2_v7upQAbAr7MyKFM2E351tA70EYauMJsiAcko0yHSU/exec
```

### Docker Compose with multiple projects

```yaml
version: '3.8'

services:
  xlite-webhook:
    image: registry.fourier.group/bot/daily-standup-webhook:latest
    container_name: standup-xlite
    ports:
      - "8080:8080"
    environment:
      - CHAT_ID=-1003773551774
      - THREAD_ID=7

  apecfinance-webhook:
    image: registry.fourier.group/bot/daily-standup-webhook:latest
    container_name: standup-apecfinance
    ports:
      - "8081:8080"
    environment:
      - CHAT_ID=-1003853347044
      - THREAD_ID=2

  ai-dev-webhook:
    image: registry.fourier.group/bot/daily-standup-webhook:latest
    container_name: standup-ai-dev
    ports:
      - "8082:8080"
    environment:
      - CHAT_ID=-1003873043927
      - THREAD_ID=12
```

## 📚 References

- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [12 Factor App Config](https://12factor.net/config)
