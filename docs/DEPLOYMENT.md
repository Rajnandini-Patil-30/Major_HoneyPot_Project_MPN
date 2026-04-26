# HoneyShield Deployment Guide

## 🚀 Production Deployment

### Prerequisites

- Ubuntu 20.04+ or RHEL 8+
- Docker & Docker Compose installed
- Minimum 2GB RAM, 10GB storage
- Open ports: 2222, 8080, 2121, 2323 (SSH, HTTP, FTP, Telnet)
- PostgreSQL (if not using Docker database)

---

## 📋 Pre-Deployment Checklist

- [ ] Review security settings in `config/config.yaml`
- [ ] Change default admin credentials
- [ ] Configure PostgreSQL connection
- [ ] Set up log rotation
- [ ] Configure firewall rules
- [ ] Enable SSL/TLS if needed
- [ ] Plan backup strategy
- [ ] Document API endpoints for integrations

---

## 🐳 Docker Deployment (Recommended)

### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Deploy HoneyShield

```bash
# Clone/download HoneyShield
cd /opt
sudo git clone <repository-url> honeyshield
cd honeyshield

# Configure environment
sudo cp .env.example .env
sudo nano .env  # Edit database credentials

# Edit config
sudo nano config/config.yaml
```

### 3. Start Services

```bash
# Start in background
sudo docker-compose up -d

# Verify services
sudo docker-compose ps

# Check logs
sudo docker-compose logs -f honeypot-engine
```

### 4. Access Services

- **SSH Honeypot**: `ssh -p 2222 localhost`
- **HTTP Honeypot**: `curl http://localhost:8080`
- **FTP Honeypot**: `ftp localhost 2121`
- **Dashboard API**: `http://localhost:5000/api/stats`

---

## 🔒 Security Hardening

### 1. Network Security

```bash
# Setup firewall (UFW)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp    # SSH honeypot
sudo ufw allow 8080/tcp    # HTTP honeypot
sudo ufw allow 2121/tcp    # FTP honeypot
sudo ufw allow 2323/tcp    # Telnet honeypot
sudo ufw allow 5000/tcp    # Dashboard (limit by IP)
sudo ufw enable
```

### 2. Docker Security

```bash
# Create non-root user for honeypot
sudo usermod -aG docker honeypot

# Configure AppArmor profiles
sudo aa-enforce docker-default

# Enable seccomp filters
# Already configured in docker-compose.yml
```

### 3. Database Security

```bash
# Change default PostgreSQL password
sudo docker-compose exec database psql -U honeypot_user -d honeypot_db \
  -c "ALTER USER honeypot_user WITH PASSWORD 'strong_secure_password';"

# Update .env and config files
sudo nano .env
```

### 4. Dashboard Security

```bash
# Generate new JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update in environment
export DASHBOARD_SECRET_KEY="<generated_secret>"

# Enable HTTPS
# Configure reverse proxy (nginx/Apache) with SSL
```

---

## 📊 Monitoring & Logging

### 1. View Logs

```bash
# Real-time logs
sudo docker-compose logs -f honeypot-engine

# Get last 100 lines
sudo docker-compose logs --tail 100 honeypot-engine

# Specific service
sudo docker-compose logs -f database
```

### 2. Monitor Resources

```bash
# Docker stats
docker stats

# Container inspection
docker inspect honeypot-engine
```

### 3. Database Monitoring

```bash
# Connect to database
sudo docker-compose exec database psql -U honeypot_user -d honeypot_db

# Count events
SELECT COUNT(*) FROM attack_events;

# Events per hour
SELECT DATE_TRUNC('hour', timestamp), COUNT(*) 
FROM attack_events 
GROUP BY DATE_TRUNC('hour', timestamp) 
ORDER BY DATE_TRUNC DESC;
```

---

## 🔄 Backup & Recovery

### 1. Automated Backups

```bash
# Create backup script
sudo cat > /usr/local/bin/honeypot-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/honeypot"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec database pg_dump -U honeypot_user honeypot_db > \
  $BACKUP_DIR/db_${TIMESTAMP}.sql

# Backup configs
tar -czf $BACKUP_DIR/config_${TIMESTAMP}.tar.gz config/ .env

# Keep last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"
EOF

sudo chmod +x /usr/local/bin/honeypot-backup.sh

# Schedule daily backups
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/honeypot-backup.sh
```

### 2. Database Backup

```bash
# Manual backup
sudo docker-compose exec database pg_dump -U honeypot_user honeypot_db > honeypot_db.sql

# Restore
sudo docker-compose exec -T database psql -U honeypot_user honeypot_db < honeypot_db.sql
```

### 3. Full System Snapshot

```bash
# Use AWS EBS snapshots or equivalent
# Document backup procedure in runbooks
```

---

## 🚨 Alerting & Monitoring

### 1. Set Up Email Alerts

```yaml
# Add to config.yaml
alerting:
  enabled: true
  email:
    smtp_server: smtp.gmail.com
    smtp_port: 587
    from: alerts@honeyshield.io
    to:
      - security@company.com
    thresholds:
      - events_per_hour > 100
      - new_attacker_ips > 10
      - failed_logins > 1000
```

### 2. Prometheus Integration (Optional)

```bash
# Add metrics exposure
# Implement /metrics endpoint
# Configure Prometheus scraping
```

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Find process
sudo lsof -i :2222

# Kill process or change port in config.yaml
```

### Database Connection Issues

```bash
# Test connectivity
sudo docker-compose exec honeypot-engine \
  python -c "from database.connection import init_db; init_db()"

# Check database logs
sudo docker-compose logs database
```

### High Memory Usage

```bash
# Check container memory
sudo docker stats honeypot-engine

# Adjust limits in docker-compose.yml
# Add: mem_limit: 2g
```

### Attack Data Not Appearing

```bash
# Validate honeypot service
sudo docker-compose exec honeypot-engine \
  python tests/validate_db.py

# Run tests
sudo docker-compose exec honeypot-engine \
  python tests/test_ssh.py
```

---

## 📈 Scaling

### Horizontal Scaling (Multiple Honeypots)

```yaml
# docker-compose.yml
services:
  honeypot-engine-1:
    # ... port 2222, 8080
  honeypot-engine-2:
    # ... port 2223, 8081
  # Shared database
  database:
    # ... centralized
```

### Kubernetes Deployment

```bash
# Create ConfigMap from honeypot config
kubectl create configmap honeypot-config --from-file=config/

# Deploy HoneyShield replicas
kubectl apply -f k8s-deployment.yaml
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

- [ ] Daily: Review logs for anomalies
- [ ] Weekly: Check disk usage, database size
- [ ] Monthly: Backup verification, security updates
- [ ] Quarterly: Performance analysis, capacity planning

### Incident Response

```bash
# Isolate compromised honeypot
sudo docker-compose down honeypot-engine

# Preserve logs for forensics
sudo tar -czf incident_logs.tar.gz logs/

# Restart services
sudo docker-compose up -d
```

---

## 🎯 Production Checklist

- [ ] All services deployed and verified
- [ ] Firewall configured
- [ ] Backup scripts running
- [ ] Monitoring enabled
- [ ] Logs centralized
- [ ] Admin credentials changed
- [ ] Database password secured
- [ ] SSL/TLS configured
- [ ] Team trained on operations
- [ ] Documentation complete
- [ ] Incident procedures documented
- [ ] Capacity planning completed

---

## 📞 Emergency Contacts

| Role | Contact | Available |
|------|---------|-----------|
| On-Call | [Phone/Email] | 24/7 |
| Database Admin | [Contact] | Business Hours |
| Security Team | [Contact] | Business Hours |

---

## 📚 Related Documentation

- [Quick Start Guide](./QUICKSTART.md)
- [README](../README.md)
- [Implementation Details](./IMPLEMENTATION.md)
- [API Documentation](./api.md)

---

**HoneyShield Production Deployment Guide v1.0**
