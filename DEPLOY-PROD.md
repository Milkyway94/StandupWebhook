# 🚀 Production Deployment Guide

Deploy Daily Standup Webhook lên server production với image từ registry.fourier.group.

## 📋 Prerequisites

- Server với Docker installed
- Access đến registry: `registry.fourier.group`
- Credentials: `digital` / `Apec@123`
- Port 8080 available (hoặc customize)

## ⚡ Quick Deploy

### Option 1: One-command script (Khuyến nghị)

```bash
# Download deployment script
wget https://raw.githubusercontent.com/Milkyway94/StandupWebhook/main/deploy-prod.sh
chmod +x deploy-prod.sh

# Run deployment
./deploy-prod.sh
```

### Option 2: Docker Compose

```bash
# Download compose file
wget https://raw.githubusercontent.com/Milkyway94/StandupWebhook/main/docker-compose.prod.yml

# Login to registry
docker login registry.fourier.group -u digital

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: Manual Docker commands

```bash
# 1. Login to registry
docker login registry.fourier.group -u digital
# Password: Apec@123

# 2. Pull image
docker pull registry.fourier.group/bot/daily-standup-webhook:latest

# 3. Run container
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  registry.fourier.group/bot/daily-standup-webhook:latest

# 4. Check logs
docker logs -f daily-standup-webhook
```

## 🔍 Verify Deployment

```bash
# Check container status
docker ps | grep daily-standup-webhook

# Test endpoint (should return 404 - normal)
curl http://localhost:8080

# Test POST request
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "user": "Test User",
    "date": "2026-03-16",
    "project": "TestProject",
    "yesterday": "Test yesterday",
    "today": "Test today",
    "ontrack": "yes",
    "blockers": "None"
  }'

# Should send to Telegram if credentials are correct
```

## 🌐 Expose to Internet

### Option 1: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/standup-webhook
server {
    listen 80;
    server_name webhook.fourier.group;  # Change to your domain

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/standup-webhook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Traefik (Docker)

```yaml
# docker-compose.prod.yml with Traefik
version: '3.8'

services:
  daily-standup-webhook:
    image: registry.fourier.group/bot/daily-standup-webhook:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.standup.rule=Host(`webhook.fourier.group`)"
      - "traefik.http.services.standup.loadbalancer.server.port=8080"
    networks:
      - traefik
      - standup-net

networks:
  traefik:
    external: true
  standup-net:
    driver: bridge
```

## 🔄 Update to Latest Version

```bash
# Pull latest image
docker pull registry.fourier.group/bot/daily-standup-webhook:latest

# Restart with new image
docker stop daily-standup-webhook
docker rm daily-standup-webhook
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

Or use the deployment script:

```bash
./deploy-prod.sh
```

## 📊 Monitoring

### View logs

```bash
# Real-time logs
docker logs -f daily-standup-webhook

# Last 100 lines
docker logs --tail 100 daily-standup-webhook

# Logs since timestamp
docker logs --since 2026-03-16T08:00:00 daily-standup-webhook
```

### Health check

```bash
# Check if container is running
docker ps | grep daily-standup-webhook

# Check container health
docker inspect daily-standup-webhook | grep -A 5 Health

# Manual health check
curl http://localhost:8080
```

### Container stats

```bash
# Real-time resource usage
docker stats daily-standup-webhook

# One-time stats
docker stats --no-stream daily-standup-webhook
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker logs daily-standup-webhook

# Inspect container
docker inspect daily-standup-webhook

# Check if port is already in use
sudo lsof -i :8080
```

### Can't pull image

```bash
# Re-login to registry
docker logout registry.fourier.group
docker login registry.fourier.group -u digital

# Verify credentials
docker pull registry.fourier.group/bot/daily-standup-webhook:latest
```

### Telegram not receiving messages

1. Check bot token in code
2. Check chat ID and thread ID
3. Verify bot is admin in Telegram group
4. Test with manual curl POST

### Port already in use

```bash
# Change port mapping
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8081:8080 \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

## 🔒 Security Best Practices

1. **Use Reverse Proxy** - Don't expose Docker port directly
2. **Enable HTTPS** - Use Let's Encrypt with nginx/Traefik
3. **Firewall** - Only allow necessary ports
4. **Update regularly** - Pull latest image weekly
5. **Monitor logs** - Set up log rotation
6. **Resource limits** - Add CPU/memory limits

Example with resource limits:

```bash
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  --memory="256m" \
  --cpus="0.5" \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

## 📝 Configuration

### Environment Variables (if needed)

Create `.env` file:

```env
PORT=8080
BOT_TOKEN=8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q
CHAT_ID=-1003773551774
THREAD_ID=7
```

Run with env file:

```bash
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

## 🎯 URLs After Deployment

**Internal access:**
- `http://localhost:8080`
- `http://SERVER_IP:8080`

**External access (with reverse proxy):**
- `https://webhook.fourier.group`

**Update webform to use:**
- Production URL in `daily-standup-form/index.html`
- Or update `projects.yaml` config

## 📞 Support

- Image registry: `registry.fourier.group/bot/daily-standup-webhook`
- Source code: https://github.com/Milkyway94/StandupWebhook
- Issues: Contact system admin

## 📚 Related Docs

- [DEPLOY.md](./DEPLOY.md) - Development deployment guide
- [README.md](./README.md) - Project overview
- Docker Docs: https://docs.docker.com/
