# 🐳 Deploy Daily Standup Webhook với Docker

Hướng dẫn deploy webhook server lên server riêng bằng Docker.

## 📋 Yêu cầu

- Docker 20.10+
- Docker Compose 1.29+ (optional)
- Server Linux với port 8080 mở

## 🚀 Cách 1: Docker Compose (Khuyến nghị)

### 1. Clone code về server

```bash
git clone https://github.com/Milkyway94/StandupWebhook.git
cd StandupWebhook
```

### 2. Build và chạy

```bash
docker-compose up -d --build
```

### 3. Kiểm tra logs

```bash
docker-compose logs -f
```

### 4. Kiểm tra health

```bash
curl http://localhost:8080
```

### 5. Stop/Restart

```bash
docker-compose down          # Stop
docker-compose restart       # Restart
docker-compose up -d         # Start
```

## 🔧 Cách 2: Docker thuần

### 1. Build image

```bash
docker build -t daily-standup-webhook:latest .
```

### 2. Chạy container

```bash
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  daily-standup-webhook:latest
```

### 3. Kiểm tra logs

```bash
docker logs -f daily-standup-webhook
```

### 4. Stop/Start

```bash
docker stop daily-standup-webhook
docker start daily-standup-webhook
docker restart daily-standup-webhook
```

## 🌐 Cách 3: Push lên Registry riêng

### 1. Build và tag

```bash
docker build -t your-registry.com/daily-standup-webhook:latest .
```

### 2. Push lên registry

```bash
docker push your-registry.com/daily-standup-webhook:latest
```

### 3. Pull và chạy trên server

```bash
docker pull your-registry.com/daily-standup-webhook:latest
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  your-registry.com/daily-standup-webhook:latest
```

## 🔒 Expose ra Internet

### Option 1: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/standup-webhook
server {
    listen 80;
    server_name webhook.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable và reload:

```bash
sudo ln -s /etc/nginx/sites-available/standup-webhook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Cloudflare Tunnel (Không cần mở port)

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create tunnel
cloudflared tunnel login
cloudflared tunnel create standup-webhook
cloudflared tunnel route dns standup-webhook webhook.yourdomain.com

# Run tunnel
cloudflared tunnel run standup-webhook --url http://localhost:8080
```

### Option 3: Direct Port Mapping

Mở port 8080 trên firewall:

```bash
# Ubuntu/Debian
sudo ufw allow 8080

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

## 📊 Monitoring

### Health check endpoint

```bash
curl http://localhost:8080
# Expect: {"status":"error","code":404,...}
# (404 là bình thường vì chỉ accept POST requests)
```

### Test POST request

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "user": "Test User",
    "date": "2026-03-16",
    "project": "TestProject",
    "yesterday": "Test yesterday",
    "today": "Test today",
    "ontrack": "yes",
    "blockers": "No blockers"
  }'
```

## 🔄 Update Code

### With Docker Compose

```bash
git pull
docker-compose down
docker-compose up -d --build
```

### With Docker

```bash
git pull
docker stop daily-standup-webhook
docker rm daily-standup-webhook
docker build -t daily-standup-webhook:latest .
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  daily-standup-webhook:latest
```

## 🐛 Troubleshooting

### Container không start

```bash
docker logs daily-standup-webhook
```

### Port đã được dùng

```bash
# Tìm process đang dùng port 8080
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

### Webhook không nhận được request

```bash
# Kiểm tra container đang chạy
docker ps | grep standup

# Kiểm tra network
docker network ls
docker network inspect standup-net

# Test từ bên trong container
docker exec -it daily-standup-webhook curl http://localhost:8080
```

## 📝 Environment Variables (Nếu cần customize)

Tạo file `.env`:

```env
PORT=8080
BOT_TOKEN=8305092853:AAFJEMce0TPjU2NTFcmLqbnlGJaXC-ZeU1Q
CHAT_ID=-1003773551774
THREAD_ID=7
```

Update `docker-compose.yml`:

```yaml
services:
  daily-standup-webhook:
    # ...
    env_file:
      - .env
```

## 🎯 Production Best Practices

1. **Use Docker Compose** - Dễ quản lý hơn
2. **Enable auto-restart** - `restart: unless-stopped`
3. **Setup logging** - Rotate logs để tránh đầy disk
4. **Use reverse proxy** - Nginx/Traefik cho SSL
5. **Monitor health** - Setup alerting nếu container down
6. **Backup data** - Nếu có persistent volume
7. **Limit resources** - Set CPU/memory limits

```yaml
# docker-compose.yml with resource limits
services:
  daily-standup-webhook:
    # ...
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
```

## 🔗 URLs

Sau khi deploy, update URL trong:
- `projects.yaml`: Webform URL
- GitHub Pages: Daily Standup Form backend endpoint

**Public URL của anh sẽ là:**
- `http://your-server-ip:8080` (nếu direct)
- `https://webhook.yourdomain.com` (nếu dùng reverse proxy)
