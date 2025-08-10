# Deployment Guide
**Last Updated**: 2025-08-10  
**Version**: 1.1.2  
**Description**: Step-by-step deployment instructions for production environments

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python**: 3.8+ (3.11+ recommended for optimal performance)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space for application and cache
- **Network**: Internet connection for API integrations (optional for offline mode)

### Operating System Support
- ✅ **Linux**: Ubuntu 20.04+, RHEL 8+, CentOS 8+
- ✅ **macOS**: 10.15+ (Catalina and newer)
- ✅ **Windows**: Windows 10+, Windows Server 2019+

### Dependencies
- Git (for source code management)
- pip (Python package installer)
- virtualenv or conda (for environment isolation)

## Environment Setup

### 1. Create Virtual Environment
```bash
# Using virtualenv
python -m venv healthplan-navigator-env
source healthplan-navigator-env/bin/activate  # Linux/macOS
healthplan-navigator-env\Scripts\activate     # Windows

# Using conda
conda create -n healthplan-navigator python=3.11
conda activate healthplan-navigator
```

### 2. Clone Repository
```bash
git clone https://github.com/rzimmerman2022/healthplan-navigator.git
cd healthplan-navigator
```

### 3. Install Dependencies
```bash
# Production installation
pip install -r requirements.txt

# Development installation (includes testing tools)
pip install -r requirements-dev.txt
pip install -e .
```

## Installation Methods

### Method 1: Standard Installation (Recommended)
```bash
# Clone and install
git clone https://github.com/rzimmerman2022/healthplan-navigator.git
cd healthplan-navigator
pip install -r requirements.txt

# Verify installation
python main.py --version
python -c "from src.healthplan_navigator.analyzer import HealthPlanAnalyzer; print('Installation successful')"
```

### Method 2: Package Installation
```bash
# Install as Python package
pip install -e .

# Use as command-line tool
healthplan-navigator --help
```

### Method 3: Docker Deployment (Future)
```bash
# Docker support planned for v1.3.0
# docker build -t healthplan-navigator .
# docker run -p 8000:8000 healthplan-navigator
```

## Configuration

### 1. Environment Variables
Create a `.env` file in the project root:
```bash
# API Configuration (optional)
HEALTHCARE_GOV_API_KEY=your_api_key_here
NPPES_API_KEY=your_nppes_key_here

# Cache Configuration
CACHE_DIRECTORY=./cache
CACHE_EXPIRY_HOURS=24

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/healthplan_navigator.log

# Statistical Configuration
DEFAULT_CONFIDENCE_LEVEL=0.95
MONTE_CARLO_ITERATIONS=10000
```

### 2. Configuration Files
Create `config/app.yaml`:
```yaml
# Application Configuration
application:
  name: "HealthPlan Navigator"
  version: "1.1.2"
  debug: false

# Analysis Settings
analysis:
  confidence_level: 0.95
  enable_statistics: true
  monte_carlo_runs: 10000
  
# API Settings
apis:
  healthcare_gov:
    enabled: true
    timeout: 30
    retry_attempts: 3
  
  nppes:
    enabled: true
    timeout: 15
    retry_attempts: 2

# Output Settings
output:
  default_format: "json"
  include_confidence_intervals: true
  save_intermediate_results: false
```

### 3. Directory Structure Setup
```bash
# Create required directories
mkdir -p logs cache/{medications,providers} reports/generated
mkdir -p data/{input,processed} config

# Set permissions (Linux/macOS)
chmod 755 logs cache reports
chmod 644 config/*
```

## Production Deployment

### 1. Application Server Setup

#### Using Gunicorn (Linux/macOS)
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF

# Start application
gunicorn --config gunicorn.conf.py main:app
```

#### Using systemd Service (Linux)
```bash
# Create service file
sudo cat > /etc/systemd/system/healthplan-navigator.service << EOF
[Unit]
Description=HealthPlan Navigator Service
After=network.target

[Service]
User=healthplan
Group=healthplan
WorkingDirectory=/opt/healthplan-navigator
Environment="PATH=/opt/healthplan-navigator/venv/bin"
ExecStart=/opt/healthplan-navigator/venv/bin/python main.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable healthplan-navigator
sudo systemctl start healthplan-navigator
```

### 2. Database Setup (Future)
```bash
# PostgreSQL setup (planned for v1.3.0)
# sudo apt-get install postgresql postgresql-contrib
# sudo -u postgres createdb healthplan_navigator
# python manage.py migrate
```

### 3. Load Balancer Configuration

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Static files
    location /static/ {
        alias /opt/healthplan-navigator/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4. SSL/HTTPS Setup
```bash
# Using Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Or using custom certificates
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/healthplan-navigator.key \
  -out /etc/ssl/certs/healthplan-navigator.crt
```

## Monitoring & Maintenance

### 1. Health Check Endpoint
```python
# Built-in health check
curl http://localhost:8000/health
# Response: {"status": "healthy", "version": "1.1.2", "timestamp": "2025-08-10T12:00:00Z"}
```

### 2. Logging Configuration
```python
# Configure structured logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/healthplan_navigator.log',
            'formatter': 'json'
        }
    },
    'loggers': {
        'healthplan_navigator': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### 3. Monitoring Metrics
```bash
# System metrics to monitor
- CPU usage (should stay below 80%)
- Memory usage (should stay below 90%)
- Disk space (cache directory growth)
- Response times (analysis should complete within 30s)
- Error rates (should stay below 1%)
- API response times (external APIs)
```

### 4. Backup Strategy
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/healthplan-navigator-$DATE"

# Create backup
mkdir -p $BACKUP_DIR
cp -r config/ $BACKUP_DIR/
cp -r cache/ $BACKUP_DIR/
cp -r logs/ $BACKUP_DIR/
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Keep only 30 days of backups
find /backup -name "healthplan-navigator-*.tar.gz" -mtime +30 -delete
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure src/ is in Python path
export PYTHONPATH="${PYTHONPATH}:./src"
# Or use: python -m src.healthplan_navigator.main
```

#### 2. Permission Denied
```bash
# Error: Permission denied writing to cache/
# Solution: Fix directory permissions
chmod 755 cache/
chmod 755 logs/
```

#### 3. API Timeout Issues
```bash
# Error: API request timeout
# Solution: Increase timeout in config
# Edit config/app.yaml:
apis:
  healthcare_gov:
    timeout: 60  # Increase from 30
```

#### 4. Memory Issues
```bash
# Error: MemoryError during analysis
# Solution: Reduce batch size or increase system memory
# Edit analysis configuration:
analysis:
  batch_size: 100  # Reduce from default
  enable_memory_optimization: true
```

### Performance Tuning

#### 1. Cache Optimization
```bash
# Enable aggressive caching
mkdir -p cache/{api_responses,analysis_results,document_cache}
# Configure cache expiry based on data freshness needs
```

#### 2. Database Optimization (Future)
```sql
-- Index optimization for PostgreSQL
CREATE INDEX idx_plans_zipcode ON plans(zipcode);
CREATE INDEX idx_analysis_client_id ON analysis_results(client_id);
```

#### 3. Resource Limits
```bash
# Set resource limits in systemd service
[Service]
LimitNOFILE=65536
LimitNPROC=32768
MemoryLimit=8G
CPUQuota=400%
```

### Log Analysis
```bash
# Common log analysis commands
# Error analysis
grep "ERROR" logs/healthplan_navigator.log | tail -50

# Performance analysis
grep "Analysis completed" logs/healthplan_navigator.log | awk '{print $NF}' | sort -n

# API response times
grep "API call" logs/healthplan_navigator.log | grep -o "took [0-9.]*s"
```

## Security Considerations

### 1. API Key Management
```bash
# Store API keys securely
# Use environment variables or secure key management
export HEALTHCARE_GOV_API_KEY=$(cat /secure/api_key.txt)

# Or use HashiCorp Vault (enterprise)
vault kv get -field=api_key secret/healthplan-navigator
```

### 2. Data Protection
```bash
# Encrypt sensitive data at rest
# Use encrypted file systems or database encryption
sudo cryptsetup luksFormat /dev/sdb1
sudo cryptsetup luksOpen /dev/sdb1 encrypted_storage
```

### 3. Network Security
```bash
# Firewall configuration
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Rate limiting
# Configure in nginx or use fail2ban
```

## Rollback Procedures

### 1. Application Rollback
```bash
# Keep previous version available
cp -r healthplan-navigator healthplan-navigator-backup-$(date +%Y%m%d)

# Rollback process
systemctl stop healthplan-navigator
mv healthplan-navigator-current healthplan-navigator-failed
mv healthplan-navigator-previous healthplan-navigator-current
systemctl start healthplan-navigator
```

### 2. Configuration Rollback
```bash
# Version control for configurations
git log --oneline config/
git checkout HEAD~1 config/app.yaml
systemctl restart healthplan-navigator
```

## Support and Maintenance

- **Documentation**: [https://github.com/rzimmerman2022/healthplan-navigator/docs](./README.md)
- **Issues**: [https://github.com/rzimmerman2022/healthplan-navigator/issues](https://github.com/rzimmerman2022/healthplan-navigator/issues)
- **Updates**: Check `git pull origin main` regularly for updates
- **Community**: Join discussions in project repository

---

*For additional deployment assistance, please create an issue in the GitHub repository with your specific environment details.*