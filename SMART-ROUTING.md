# 🎯 Smart Routing - 1 Container, Multiple Projects

## Concept

Thay vì deploy nhiều containers cho mỗi project, chỉ cần **1 container** với smart routing:

- POST request có field `project` (xlite, apecfinance, ai-development)
- Code tự động route đến đúng Telegram chat/thread
- Config projects trong file YAML hoặc env variables

## Lợi ích

✅ **1 source code** - Dễ maintain  
✅ **1 image** - Tiết kiệm resource  
✅ **1 container** - Đơn giản deployment  
✅ **Dynamic routing** - Add project mới chỉ cần update config  
✅ **Shared bot token** - Không cần nhiều bots  

## Implementation Options

### Option 1: YAML Config File (Recommended)

**projects-config.yaml:**
```yaml
projects:
  xlite:
    chat_id: "-1003773551774"
    thread_id: 7
  apecfinance:
    chat_id: "-1003853347044"
    thread_id: 2
```

**Deployment:**
```bash
docker run -d \
  --name daily-standup-webhook \
  -p 8080:8080 \
  -v ./projects-config.yaml:/app/projects-config.yaml \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

### Option 2: JSON Config in Env Var

```bash
docker run -d \
  --name daily-standup-webhook \
  -p 8080:8080 \
  -e PROJECTS_CONFIG='{"xlite":{"chat_id":"-1003773551774","thread_id":7},"apecfinance":{"chat_id":"-1003853347044","thread_id":2}}' \
  registry.fourier.group/bot/daily-standup-webhook:latest
```

### Option 3: Hardcoded in Code (Current)

Projects config trực tiếp trong `main-smart.py`.

## Usage

**POST request:**
```json
{
  "project": "xlite",
  "user": "Hồ Sỹ Quyết",
  "date": "2026-03-16",
  "yesterday": "Fix bugs",
  "today": "Deploy",
  "ontrack": "yes",
  "blockers": "None"
}
```

Code tự động:
- Read `project` field
- Lookup config cho "xlite"
- Send to chat `-1003773551774`, thread `7`

## Migration

### Current (Multiple containers):
```yaml
services:
  xlite: ...
  apecfinance: ...
  ai: ...
```

### New (Single container):
```yaml
services:
  webhook:
    image: registry.fourier.group/bot/daily-standup-webhook:latest
    ports:
      - "8080:8080"
    volumes:
      - ./projects-config.yaml:/app/projects-config.yaml
```

## Adding New Project

Chỉ cần update config, không cần rebuild/redeploy:

**1. Update projects-config.yaml:**
```yaml
projects:
  new-project:
    chat_id: "-100xxx"
    thread_id: 5
```

**2. Reload config (no restart needed if watching file):**
```bash
# Or just restart container
docker restart daily-standup-webhook
```

**3. Use in webform:**
```html
<input type="hidden" name="project" value="new-project">
```

## Comparison

| Approach | Containers | Ports | Config | Maintenance |
|----------|-----------|-------|--------|-------------|
| **Old** | 3+ | 8080, 8081, 8082... | Per-container env | Hard |
| **New** | 1 | 8080 | Shared YAML | Easy |

## Recommendation

✅ Use **main-smart.py** với **projects-config.yaml**  
✅ Deploy **1 container** on port 8080  
✅ Update config file khi add project mới  
✅ Webform chỉ cần set `project` field đúng  

---

**Anh muốn em implement cái nào?**
1. Refactor main.py thành smart routing? ✅ (Recommended)
2. Giữ nguyên main.py, add main-smart.py như alternative?
3. Hybrid: Support cả 2 modes (env override hoặc smart routing)?
