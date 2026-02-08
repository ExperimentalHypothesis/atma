# Integrate atma.fm with Existing Nginx Setup

Your server already has a dockerized nginx running (blog-infra). This guide shows how to add atma.fm to it.

## Changes Made

### 1. Docker Network
Both containers now share a `web` network so nginx can proxy to atma-fm:

- **blog-infra/docker-compose.yaml** - nginx and blog now on `web` network
- **atma/docker-compose.yaml** - atma-fm now on `web` network (external)

### 2. Nginx Configuration
- **blog-infra/nginx/nginx.conf** - Added atma.fm server block
- **blog-infra/nginx/snippets/ssl-atma.conf** - SSL config for atma.fm

## Deployment Steps

### Step 1: Update DNS

Make sure `atma.fm` DNS points to your server:
- `atma.fm` → `173.212.246.158`
- `www.atma.fm` → `173.212.246.158`

Check:
```bash
dig atma.fm
nslookup atma.fm
```

### Step 2: Get SSL Certificate for atma.fm

SSH to your server and get Let's Encrypt certificate:

```bash
ssh user@173.212.246.158

# Install certbot if not already installed
sudo apt update
sudo apt install certbot -y

# Stop nginx temporarily
cd ~/blog-infra
docker-compose stop nginx

# Get certificate
sudo certbot certonly --standalone -d atma.fm -d www.atma.fm --email your-email@example.com --agree-tos

# Certificate will be saved to:
# /etc/letsencrypt/live/atma.fm/fullchain.pem
# /etc/letsencrypt/live/atma.fm/privkey.pem
```

### Step 3: Update docker-compose for SSL Volume

Edit `~/blog-infra/docker-compose.yaml` on the server to add atma.fm SSL certs:

```yaml
  nginx:
    ...
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/snippets/:/etc/nginx/snippets/:ro
      - /etc/letsencrypt/live/cognitai.cz:/etc/letsencrypt/live/cognitai.cz:ro
      - /etc/letsencrypt/live/atma.fm:/etc/letsencrypt/live/atma.fm:ro
      - /etc/letsencrypt/archive:/etc/letsencrypt/archive:ro
```

Or simpler - mount the entire letsencrypt directory:
```yaml
  nginx:
    ...
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/snippets/:/etc/nginx/snippets/:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Step 4: Deploy Updated Configurations

From your Mac, push changes to GitHub:

```bash
cd ~/Code/Private/atma
git add .
git commit -m "Add nginx integration and SSE support"
git push origin master

cd ~/Code/Private/blog-infra
git add .
git commit -m "Add atma.fm to nginx config"
git push origin master
```

On the server:

```bash
ssh user@173.212.246.158

# Update blog-infra (nginx)
cd ~/blog-infra
git pull origin master

# Recreate nginx with network changes
docker-compose down
docker-compose up -d

# Update atma
cd ~/atma
git pull origin master

# Deploy atma with new network config
docker-compose down
docker-compose up -d --build
```

### Step 5: Verify Setup

```bash
# Check if web network exists
docker network ls | grep web

# Check if both containers are on the web network
docker network inspect web

# Check nginx logs
docker logs nginx

# Check atma-fm logs
docker logs atma-fm

# Test HTTPS
curl -I https://atma.fm

# Test SSE endpoint
curl -N https://atma.fm/api/events/channel1
```

## Architecture

```
Internet (port 80/443)
         ↓
    nginx container (blog-infra)
         ├─→ blog:3000 (cognitai.cz)
         └─→ atma-fm:5555 (atma.fm)
```

## Troubleshooting

### Containers can't communicate

```bash
# Verify network exists
docker network inspect web

# Check containers are on network
docker inspect nginx | grep -A 20 Networks
docker inspect atma-fm | grep -A 20 Networks

# If web network doesn't exist, create it
docker network create web

# Restart containers
cd ~/blog-infra && docker-compose restart
cd ~/atma && docker-compose restart
```

### SSL Certificate Issues

```bash
# Check certificate exists
sudo ls -la /etc/letsencrypt/live/atma.fm/

# Test nginx config
docker exec nginx nginx -t

# Check nginx error logs
docker logs nginx 2>&1 | grep -i error
```

### SSE Not Working

Check nginx logs for buffering warnings:
```bash
docker logs nginx | grep -i buffer
```

Test SSE directly:
```bash
# Should keep connection open and stream events
curl -N https://atma.fm/api/events/channel1
```

### Port 5555 Still Needed?

You can remove the port mapping from atma's docker-compose.yaml if you only want nginx to access it:

```yaml
# Remove this line:
    ports:
      - "5555:5555"
```

Then `docker-compose down && docker-compose up -d` in ~/atma.

## SSL Auto-Renewal

Certbot auto-renewal should work. Test it:

```bash
sudo certbot renew --dry-run
```

After renewal, reload nginx:
```bash
docker exec nginx nginx -s reload
```

Or set up a cron job:
```bash
sudo crontab -e

# Add this line (runs at 2am daily):
0 2 * * * certbot renew --quiet && docker exec nginx nginx -s reload
```

## Monitoring

### Check if site is up
```bash
curl -I https://atma.fm
curl -I https://cognitai.cz
```

### View logs
```bash
# Nginx access logs
docker exec nginx tail -f /var/log/nginx/access.log

# Nginx error logs
docker exec nginx tail -f /var/log/nginx/error.log

# Atma app logs
docker logs -f atma-fm
```

### Container status
```bash
docker ps
docker stats
```