# Deployment Guide for atma.fm

Simple deployment workflow for your Ubuntu server.

## Initial Server Setup (One-time)

### 1. Install Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add your user to docker group (to run docker without sudo)
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

### 2. Clone Repository

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/atma.git
cd atma
```

### 3. Create Environment File

```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Create .env file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=${SECRET_KEY}

# These paths should match your Icecast/Ices installation
ICECAST_PLAYLIST_LOG=/etc/icecast2/log/playlist.log
ICES_CUE_CHANNEL1=/etc/ices/log/channel1/ices.cue
ICES_CUE_CHANNEL2=/etc/ices/log/channel2/ices.cue
AUDIO_DIR_CHANNEL1=${HOME}/audio/channel1
AUDIO_DIR_CHANNEL2=${HOME}/audio/channel2
EOF

echo "✅ .env file created"
```

### 4. Make Deploy Script Executable

```bash
chmod +x deploy.sh
```

### 5. Initial Deployment

```bash
./deploy.sh
```

---

## Regular Deployment Workflow

Every time you want to deploy new changes:

### On Your Mac (Development)

```bash
# Make your changes
git add .
git commit -m "Your commit message"
git push origin master
```

### On Ubuntu Server

```bash
# SSH to your server
ssh user@your-server-ip

# Navigate to project directory
cd ~/atma

# Run deployment script
./deploy.sh
```

That's it! The script will:
1. Pull latest code from GitHub
2. Rebuild Docker image
3. Restart the application
4. Show you the status and logs

---

## Useful Commands

```bash
# View live logs
docker-compose logs -f

# Stop the app
docker-compose down

# Start the app
docker-compose up -d

# Restart the app
docker-compose restart

# Check container status
docker-compose ps

# See resource usage
docker stats
```

---

## Troubleshooting

### Port 5555 already in use
```bash
# Find what's using the port
sudo lsof -i :5555

# Stop the container
docker-compose down
```

### Can't connect to Docker daemon
```bash
# Make sure Docker is running
sudo systemctl start docker

# Check Docker status
sudo systemctl status docker
```

### Files not found errors
Check that your Icecast/Ices paths in `.env` are correct and the files exist:
```bash
ls -la /etc/icecast2/log/playlist.log
ls -la /etc/ices/log/channel1/ices.cue
ls -la /etc/ices/log/channel2/ices.cue
ls -la ~/audio/channel1
ls -la ~/audio/channel2
```

---

## Security Notes

- **Never commit `.env` file** - It's already in `.gitignore`
- Change the default SECRET_KEY in production
- Consider setting up a reverse proxy (nginx) with SSL for HTTPS
- Use a firewall to restrict access to port 5555 if needed