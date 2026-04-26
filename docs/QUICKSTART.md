# HoneyShield Quick Start Guide

## 🚀 30-Second Deploy

### Option 1: Docker (Recommended)

```bash
# Navigate to project directory
cd HoneyShield

# Start everything with Docker Compose
docker-compose up -d

# Check services
docker-compose ps

# View honeypot logs
docker-compose logs -f honeypot-engine
```

**Services Running After 1 Minute:**
- SSH Honeypot: `localhost:2222`
- HTTP Honeypot: `localhost:8080`
- FTP Honeypot: `localhost:2121`
- Telnet Honeypot: `localhost:2323`
- Dashboard Backend API: `localhost:5000`
- Database: PostgreSQL on `localhost:5432`

### Option 2: Local Python Setup

```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python -c "from database.connection import init_db; init_db()"

# Run honeypot
python -m honeypot_engine.engine

# In another terminal, run dashboard backend
cd dashboard_backend
python -c "from main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=5000)"
```

## 🧪 Test the Honeypot

### Run All Tests at Once

```bash
# Linux/macOS
bash tests/run_all_tests.sh

# Windows
python tests/run_all_tests.bat
```

### Test Individual Protocols

```bash
# SSH brute-force
python tests/test_ssh.py

# HTTP scanning
python tests/test_http.py

# FTP login attempts
python tests/test_ftp.py

# Telnet login attempts
python tests/test_telnet.py

# Validate captured data in database
python tests/validate_db.py
```

## 📊 Check Dashboard Data

```bash
# Query attack statistics
curl http://localhost:5000/api/stats

# Get top attacker IPs
curl http://localhost:5000/api/attackers

# Get most attempted credentials
curl http://localhost:5000/api/credentials

# Get protocol breakdown
curl http://localhost:5000/api/protocol-distribution
```

## 🔍 View Database

### SQLite (Local Development)

```bash
# Install sqlite3 if not present
sqlite3 honeypot.db

# Check tables
.tables

# Query attack events
SELECT * FROM attack_events LIMIT 10;

# Count events by protocol
SELECT protocol, COUNT(*) as count FROM attack_events GROUP BY protocol;

# Top attacker IPs
SELECT ip, COUNT(*) as attempts FROM attack_events GROUP BY ip ORDER BY attempts DESC LIMIT 10;
```

### PostgreSQL (Docker)

```bash
# Connect to database
docker exec -it honeypot-db psql -U honeypot_user -d honeypot_db

# Check tables
\dt

# Query data
SELECT * FROM attack_events LIMIT 10;
SELECT protocol, COUNT(*) FROM attack_events GROUP BY protocol;
```

## 📝 Configuration

### Modify Ports

Edit `config/config.yaml`:

```yaml
services:
  ssh:
    port: 2222      # Change to 22 for production
  http:
    port: 8080      # Change to 80 for production
  ftp:
    port: 2121      # Change to 21 for production
  telnet:
    port: 2323      # Change to 23 for production
```

### Switch to PostgreSQL

Edit `config/config.yaml`:

```yaml
database:
  type: postgresql
  host: localhost
  port: 5432
  database: honeypot_db
  user: honeypot_user
  password: your_secure_password
```

## 🛑 Stop Services

```bash
# Docker
docker-compose down

# Local - Press Ctrl+C in terminal running honeypot
```

## 📊 Dashboard URLs

Once frontend is implemented:
- Main Dashboard: `http://localhost:3000`
- API Documentation: `http://localhost:5000/docs` (FastAPI Swagger UI)
- Attack Timeline: View last 24 hours of attacks
- World Attack Map: Geolocation-based attack visualization

## 🔐 Production Security Checklist

- [ ] Change default admin credentials
- [ ] Enable HTTPS/SSL on dashboard
- [ ] Use strong database password
- [ ] Configure firewall rules
- [ ] Enable log rotation (retention_days)
- [ ] Set up monitoring/alerting
- [ ] Review security settings in config.yaml
- [ ] Enable rate limiting
- [ ] Deploy in isolated network

## 🐛 Troubleshooting

### Ports Already in Use

```bash
# Find process using port
lsof -i :2222  # Linux/macOS
netstat -ano | findstr :2222  # Windows

# Stop the process or use different ports in config.yaml
```

### Database Connection Error

```bash
# Check database is running
docker-compose ps

# View database logs
docker-compose logs database

# Recreate database
docker-compose down -v  # Remove volumes
docker-compose up -d
```

### No Attacks Detected

1. Verify honeypot is running: `docker-compose ps`
2. Run tests manually: `python tests/test_ssh.py`
3. Check database: `python tests/validate_db.py`
4. Review logs: `docker-compose logs honeypot-engine`

## 📚 Additional Resources

- [Full README](../README.md)
- [PRD Documentation](../HoneyShield_PRD.md)
- [Configuration Reference](./configuration.md)
- [API Documentation](./api.md)
- [Deployment Guide](./deployment.md)

## 💡 Pro Tips

1. Use `docker-compose logs -f` for real-time logging
2. Export attack data: `curl http://localhost:5000/api/events > events.json`
3. Monitor resource usage: `docker stats`
4. Backup database: `docker exec honeypot-db pg_dump -U honeypot_user honeypot_db > backup.sql`
5. Run tests periodically to verify honeypot is capturing attacks

---

**HoneyShield v1.0** - Always-On Threat Intelligence Platform
