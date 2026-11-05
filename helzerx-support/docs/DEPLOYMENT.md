# HELZERX AI Support - Production Deployment Guide

This guide details three production deployment options: **Docker Compose**, **Linux VPS (systemd)**, and **Replit**.

---

## Option 1: Docker Compose (Recommended Production)

Docker Compose bundles the bot container, PostgreSQL 16 database, and health monitoring.

```bash
cd helzerx-support

# 1. Copy and configure .env
cp .env.example .env
nano .env

# 2. Build and start services in background
docker compose up -d --build

# 3. View live logs
docker compose logs -f bot
```

To stop:
```bash
docker compose down
```

---

## Option 2: Linux VPS with systemd Service

For bare-metal or KVM Linux servers (Ubuntu 22.04 / 24.04 or Debian 12):

### 1. System Packages & Python Environment
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

cd /opt
git clone https://github.com/helzerx/helzerx-support.git
cd helzerx-support

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env
```

### 3. Create systemd Service Unit
Create `/etc/systemd/system/helzerx-bot.service`:

```ini
[Unit]
Description=HELZERX AI Discord Support Bot
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/helzerx-support
ExecStart=/opt/helzerx-support/venv/bin/python3 bot/main.py
Restart=always
RestartSec=10
EnvironmentFile=/opt/helzerx-support/.env

# Security Sandbox
ProtectSystem=full
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

### 4. Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable helzerx-bot
sudo systemctl start helzerx-bot

# Check status and logs
sudo systemctl status helzerx-bot
sudo journalctl -u helzerx-bot -f
```

---

## Option 3: 1-Click Replit Deployment

The project is pre-configured with `.replit` and `replit.nix`:
1. Import or drag the `helzerx-support` folder into Replit.
2. In the **Secrets** tool (left sidebar), add:
   - `DISCORD_TOKEN`
   - `DISCORD_GUILD_ID`
   - `NVIDIA_API_KEY`
   - `NVIDIA_MODEL`
3. Click the **Run** button. Replit will execute `python3 bot/main.py` automatically.
