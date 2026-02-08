# Nginx Setup Guide for atma.fm

## Prerequisites

- Ubuntu server (173.212.246.158)
- Domain name (atma.fm) pointing to your server IP
- Docker container running on port 5555

## Step 1: Install Nginx

SSH to your server and install nginx:

```bash
ssh user@173.212.246.158

# Update packages
sudo apt update

# Install nginx
sudo apt install nginx -y

# Check nginx status
sudo systemctl status nginx
```

## Step 2: Configure Domain DNS

Before setting up SSL, make sure your domain DNS is configured:

**DNS A Records:**
- `atma.fm` → `173.212.246.158`
- `www.atma.fm` → `173.212.246.158` (optional)

Check DNS propagation:
```bash
dig atma.fm
nslookup atma.fm
```

## Step 3: Copy Nginx Configuration

From your local machine, copy the nginx config to the server:

```bash
# From your Mac
scp nginx/atma.fm.conf user@173.212.246.158:/tmp/
```

Then on the server:

```bash
# Move config to nginx sites-available
sudo mv /tmp/atma.fm.conf /etc/nginx/sites-available/atma.fm.conf

# Create symlink to sites-enabled
sudo ln -s /etc/nginx/sites-available/atma.fm.conf /etc/nginx/sites-enabled/

# Remove default nginx config if it exists
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t
```

## Step 4: Set Up SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Create directory for certbot challenges
sudo mkdir -p /var/www/certbot

# Get SSL certificate (replace your-email@example.com)
sudo certbot certonly --webroot -w /var/www/certbot -d atma.fm -d www.atma.fm --email your-email@example.com --agree-tos --no-eff-email

# Reload nginx
sudo systemctl reload nginx
```

**Note:** If certbot fails because SSL directives in config reference non-existent certs, temporarily comment out the HTTPS server block, reload nginx, get the cert, then uncomment.

## Step 5: Verify Setup

```bash
# Check nginx status
sudo systemctl status nginx

# Check if port 80 and 443 are listening
sudo netstat -tulpn | grep nginx

# Test HTTPS
curl https://atma.fm

# Check logs if issues
sudo tail -f /var/log/nginx/atma.fm.error.log
```

## Step 6: Auto-Renewal for SSL

Certbot automatically sets up a cron job for renewal. Test it:

```bash
# Dry run renewal
sudo certbot renew --dry-run
```

## Step 7: Configure Firewall (if UFW is enabled)

```bash
# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Check status
sudo ufw status
```

## Testing

1. **HTTP Redirect:** Visit `http://atma.fm` - should redirect to HTTPS
2. **HTTPS:** Visit `https://atma.fm` - should load your site
3. **SSE:** Check browser DevTools Network tab - `/api/events/channel1` should show `EventStream`
4. **Stream:** Test the audio player works

## Troubleshooting

### SSL Certificate Issues

If certbot fails on first try:

```bash
# Edit nginx config and comment out the HTTPS server block (lines with ssl_*)
sudo nano /etc/nginx/sites-available/atma.fm.conf

# Reload nginx
sudo systemctl reload nginx

# Get certificate
sudo certbot certonly --webroot -w /var/www/certbot -d atma.fm -d www.atma.fm --email your-email@example.com --agree-tos

# Uncomment HTTPS block in nginx config
sudo nano /etc/nginx/sites-available/atma.fm.conf

# Reload nginx
sudo systemctl reload nginx
```

### Check Nginx Logs

```bash
# Error log
sudo tail -f /var/log/nginx/atma.fm.error.log

# Access log
sudo tail -f /var/log/nginx/atma.fm.access.log
```

### Restart Services

```bash
# Restart nginx
sudo systemctl restart nginx

# Restart docker container
cd ~/atma
docker-compose restart
```

### Port Conflicts

If port 80/443 is already in use:

```bash
# Check what's using the ports
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Stop conflicting service (example: apache)
sudo systemctl stop apache2
sudo systemctl disable apache2
```

## Maintenance

### View Logs
```bash
sudo tail -f /var/log/nginx/atma.fm.access.log
sudo tail -f /var/log/nginx/atma.fm.error.log
```

### Reload Config (after changes)
```bash
sudo nginx -t  # Test config first
sudo systemctl reload nginx
```

### Renew SSL Manually
```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Security Notes

- SSL certificates auto-renew every 90 days
- HTTPS is enforced (HTTP redirects to HTTPS)
- Security headers are configured (HSTS, X-Frame-Options, etc.)
- SSE endpoints properly configured (no buffering)