# Deployment Guide
## 部署指南

### Development Deployment

#### Backend
```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup environment
cp ../../.env.example ../../.env
# Edit .env with your configuration

# Run
python main.py
```

#### Frontend
```bash
cd src/frontend
npm install
npm run dev
```

### Production Deployment with Docker

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### 1. Build Environment File
```bash
# Copy and edit production environment
cp .env.production .env
# Update .env with your production values:
# - SECRET_KEY (generate random string)
# - ENCRYPTION_KEY (generate with Python)
# - ANTHROPIC_API_KEY or OPENAI_API_KEY
```

#### 2. Generate Keys
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

#### 3. Deploy
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

#### 4. Health Check
```bash
# Check backend health
curl http://localhost:8000/api/health

# Check frontend
curl http://localhost/
```

### Manual Deployment (Without Docker)

#### Backend (Systemd Service)
```bash
# Create service file
sudo nano /etc/systemd/system/worklog.service
```

Content:
```ini
[Unit]
Description=Work Log System Backend
After=network.target

[Service]
Type=simple
User=worklog
WorkingDirectory=/opt/worklog/src
Environment="PATH=/opt/worklog/venv/bin"
ExecStart=/opt/worklog/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Deploy
sudo mkdir -p /opt/worklog
cp -r . /opt/worklog/
cd /opt/worklog/src
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create data directory
mkdir -p /opt/worklog/data /opt/worklog/logs

# Start service
sudo systemctl daemon-reload
sudo systemctl enable worklog
sudo systemctl start worklog

# Check status
sudo systemctl status worklog
```

#### Frontend (Nginx)
```bash
cd frontend
npm run build

# Copy to nginx
sudo cp -r dist/* /var/www/html/worklog/

# Nginx config
sudo nano /etc/nginx/sites-available/worklog
```

Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html/worklog;
    index index.html;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/worklog /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Security Hardening

#### 1. Enable HTTPS (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### 2. Firewall Configuration
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 3. Rate Limiting (Nginx)
Add to nginx config:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20;
    proxy_pass http://localhost:8000;
}
```

### Monitoring

#### Logs
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# View application logs
tail -f logs/worklog.log
```

#### Performance Monitoring
```bash
# Check resource usage
docker stats

# Check database size
ls -lh data/worklog.db
```

### Backup Strategy

#### 1. Database Backup
```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backup/worklog"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp data/worklog.db $BACKUP_DIR/worklog_$DATE.db

# Keep last 30 days
find $BACKUP_DIR -name "worklog_*.db" -mtime +30 -delete
```

#### 2. Automated Backup (Cron)
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/worklog/scripts/backup.sh
```

### Troubleshooting

#### Issue: Container won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

#### Issue: Database locked
```bash
# Stop services
docker-compose down

# Check for lock file
ls -la data/worklog.db*

# Remove lock (DuckDB)
rm data/worklog.db-wal

# Restart
docker-compose up -d
```

#### Issue: API returns 401
```bash
# Check token
curl http://localhost:8000/api/health

# Login and get new token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_user","password":"your_pass"}'
```

### Performance Tuning

#### 1. Cache Size Optimization
Update `.env`:
```env
CACHE_MAX_SIZE=2000        # Increase for high traffic
CACHE_DEFAULT_TTL=7200     # 2 hours
```

#### 2. Database Optimization
```python
# DuckDB configuration
DUCKDB_PATH=/app/data/worklog.db
# DuckDB automatically optimizes queries
```

#### 3. Worker Processes (Production)
```bash
# Use gunicorn with uvicorn workers
pip install gunicorn

# Update CMD in Dockerfile
CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

### Scaling

#### Horizontal Scaling
```yaml
# docker-compose.yml
backend:
  deploy:
    replicas: 3
  # Add load balancer (nginx/traefik)
```

#### Vertical Scaling
```yaml
backend:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```
