# CodeBeep Setup Guide

## HTTPS Configuration Complete ✅

Your OpenCode server is now accessible via HTTPS:
- **URL:** `https://mihais-macbook-pro.taila9246e.ts.net`
- **Username:** `opencode`
- **Password:** `Pncdfrwll25121997m@!`

## Next Steps

### 1. Get Beeper Access Token

**Method A: Beeper Desktop App (Recommended)**
1. Open Beeper desktop app
2. Go to **Settings** → **Developers**
3. Click **"+"** next to "Approved connections"
4. Follow the instructions to create a token
5. Copy the token (starts with `syt_`)

**Method B: Element/Other Matrix Client**
1. Log into your bot account (`@codebeep-bot:beeper.local`)
2. Go to **Settings** → **Help & About** → **Access Token**
3. Copy the token

### 2. Update Configuration

Edit `config.yaml`:
```yaml
matrix:
  username: "@codebeep-bot:beeper.local"
  access_token: "PASTE_YOUR_TOKEN_HERE"  # ← Replace this
  allowed_users:
    - "@mihai:beeper.local"  # ← Your personal Beeper username
```

### 3. Start CodeBeep

**Option A: Docker (Recommended)**
```bash
cd /Volumes/990Pro2TB/MyProjects/codebeep
docker-compose up -d
docker-compose logs -f  # View logs
```

**Option B: macOS LaunchAgent**
```bash
# Copy LaunchAgent
cp com.mihai.codebeep.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.mihai.codebeep.plist

# Check logs
tail -f /tmp/codebeep.log
```

### 4. Test the Setup

1. **OpenCode:** Open `https://mihais-macbook-pro.taila9246e.ts.net` in Safari
2. **CodeBeep:** Check logs for successful connection
3. **Beeper:** DM `@codebeep-bot:beeper.local` from your phone

## Troubleshooting

### Docker Issues
```bash
# Rebuild if needed
docker-compose build --no-cache

# Check container status
docker-compose ps

# View detailed logs
docker-compose logs --tail=100
```

### Matrix Connection Issues
1. Verify access token is correct
2. Check bot username format: `@username:beeper.local`
3. Ensure bot account exists on Beeper

### OpenCode Connection Issues
```bash
# Test OpenCode HTTPS access
curl -u opencode:Pncdfrwll25121997m@! https://mihais-macbook-pro.taila9246e.ts.net/health

# Check Tailscale Serve status
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve status
```

## Files Created

1. **`ai.tailscale.serve.plist`** - Tailscale Serve LaunchAgent (HTTPS proxy)
2. **`config.yaml`** - Updated configuration with HTTPS URL
3. **`SETUP_GUIDE.md`** - This guide
4. **`Dockerfile` & `docker-compose.yml`** - Docker support
5. **`opencode-access.html`** - Safari-friendly access portal

## Security Notes

- ✅ **HTTPS enabled** via Tailscale Serve
- ✅ **Access token authentication** (more secure than password)
- ✅ **Basic Auth** for OpenCode with strong password
- ✅ **Tailscale network** (private, encrypted)
- ✅ **Docker container** (isolated environment)

## Quick Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Test OpenCode access
open https://mihais-macbook-pro.taila9246e.ts.net
```