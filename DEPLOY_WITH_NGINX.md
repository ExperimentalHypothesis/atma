# Deploy atma.fm with HTTPS

This guide shows how to deploy atma.fm with full HTTPS support (website + streams) using your existing nginx.

## What This Does

- **Website**: `https://atma.fm` → Flask app
- **Stream Channel 1**: `https://atma.fm/channel1` → Icecast (HTTPS wrapper)
- **Stream Channel 2**: `https://atma.fm/channel2` → Icecast (HTTPS wrapper)
- **Playlist files**: `/channel1.pls`, `/channel2.pls`

Everything goes through nginx with SSL, so browsers are happy (no mixed content warnings).

## Prerequisites

1. DNS: `atma.fm` points to `173.212.246.158`
2. Icecast running on `173.212.246.158:7778`
3. Existing `blog-infra` nginx setup

## Step 1: Verify DNS

```bash
dig atma.fm
# Should show: 173.212.246.158
```

## Step 2: Get SSL Certificate for atma.fm

SSH to your server:

```bash
ssh user@173.212.246.158
cd ~/blog-infra
```

### Option A: Using Cloudflare DNS Challenge (Recommended)

Create a temporary certbot config:

```bash
cat > /tmp/certbot-atma.yaml << 'EOF'
version: '3'
services:
  certbot:
    image: certbot/dns-cloudflare
    volumes:
      - /etc/blog/ssl/conf:/etc/letsencrypt
    command: >
      certonly -v --dns-cloudflare
      --email YOUR_EMAIL@example.com
      -d atma.fm
      -d www.atma.fm
      --agree-tos --non-interactive
      --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini
      --dns-cloudflare-propagation-seconds 60
EOF
```

**Replace `YOUR_EMAIL@example.com` with your email!**

Run it:

```bash
docker-compose -f /tmp/certbot-atma.yaml up
```

Certificate will be saved to:
- `/etc/blog/ssl/conf/live/atma.fm/fullchain.pem`
- `/etc/blog/ssl/conf/live/atma.fm/privkey.pem`

### Option B: Using Standalone (Alternative)

If Cloudflare method doesn't work:

```bash
# Stop nginx temporarily
cd ~/blog-infra
docker-compose stop nginx

# Get certificate
sudo certbot certonly --standalone \
  -d atma.fm -d www.atma.fm \
  --email YOUR_EMAIL@example.com \
  --agree-tos

# Copy to blog SSL directory
sudo cp -r /etc/letsencrypt/live/atma.fm /etc/blog/ssl/conf/live/
sudo cp -r /etc/letsencrypt/archive/atma.fm /etc/blog/ssl/conf/archive/

# Restart nginx
docker-compose start nginx
```

## Step 3: Deploy Updated Code

### On Your Mac:

```bash
# Commit and push blog-infra changes
cd ~/Code/Private/blog-infra
git add .
git commit -m "Add atma.fm nginx config with stream proxy"
git push origin master

# Commit and push atma changes
cd ~/Code/Private/atma
git add .
git commit -m "Update to use HTTPS URLs via nginx"
git push origin master
```

### On the Server:

```bash
ssh user@173.212.246.158

# Deploy blog-infra (nginx config)
cd ~/blog-infra
git pull origin master
docker-compose restart nginx

# Deploy atma.fm
cd ~/atma
./deploy.sh
```

## Step 4: Verify Everything Works

```bash
# Test website
curl -I https://atma.fm
# Should return: 200 OK

# Test stream channel 1
curl -I https://atma.fm/channel1
# Should return: 200 OK (audio/mpeg)

# Test stream channel 2
curl -I https://atma.fm/channel2
# Should return: 200 OK (audio/mpeg)

# Test SSE
curl -N https://atma.fm/api/events/channel1
# Should keep connection open and stream events

# Check containers
docker ps
# Should show: nginx, blog, atma-fm all running
```

## Step 5: Test in Browser

1. Open `https://atma.fm`
2. Click "listen" - should play channel 1
3. Switch to channel 2 - should play channel 2
4. Check browser console - no mixed content errors
5. Download playlist file - should work in VLC/iTunes

## Architecture

```
Browser
   ↓ HTTPS
nginx (port 443)
   ├─→ atma-fm:5555 (Flask app) → Website, API
   └─→ 173.212.246.158:7778 (Icecast) → /channel1, /channel2
```

## Troubleshooting

### SSL Certificate Not Found

```bash
# Check certificate exists
ls -la /etc/blog/ssl/conf/live/atma.fm/

# If not, re-run certbot (see Step 2)
```

### Stream Not Working

```bash
# Test Icecast directly
curl -I http://173.212.246.158:7778/channel1

# Check nginx can reach Icecast
docker exec nginx curl -I http://173.212.246.158:7778/channel1

# Check nginx logs
docker logs nginx 2>&1 | grep -i error
```

### Containers Can't Communicate

```bash
# Check web network
docker network inspect web

# Should show: nginx, blog, atma-fm

# If not, restart in order:
cd ~/blog-infra && docker-compose restart
cd ~/atma && docker-compose restart
```

### Mixed Content Errors

If you see mixed content warnings in browser console:
- Check all URLs in code use `https://atma.fm` not IP addresses
- Check browser dev tools Network tab for HTTP requests
- Verify nginx is proxying streams correctly

### SSE Not Working

```bash
# Test SSE endpoint
curl -N https://atma.fm/api/events/channel1

# Should stay connected and output JSON events
# Press Ctrl+C to stop

# Check nginx buffering settings
docker exec nginx nginx -T | grep -A 5 "location /api/events"
```

## SSL Renewal

Certbot should auto-renew. To test:

```bash
sudo certbot renew --dry-run
```

Set up auto-reload of nginx after renewal:

```bash
sudo crontab -e

# Add this line:
0 3 * * * certbot renew --quiet && docker exec nginx nginx -s reload
```

## Monitoring

```bash
# Watch nginx logs
docker logs -f nginx

# Watch atma logs
docker logs -f atma-fm

# Check SSL certificate expiry
echo | openssl s_client -servername atma.fm -connect 173.212.246.158:443 2>/dev/null | openssl x509 -noout -dates
```

## Rolling Back

If something breaks:

```bash
# Rollback blog-infra
cd ~/blog-infra
git revert HEAD
docker-compose restart nginx

# Rollback atma
cd ~/atma
git revert HEAD
./deploy.sh
```

## Notes

- atma.fm and cognitai.cz share the same nginx but have separate SSL certificates
- Streams go through nginx for HTTPS but use Icecast backend
- Port 5555 can be removed from atma's docker-compose if you only want nginx access
- All traffic is HTTPS - no mixed content warnings