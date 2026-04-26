# HoneyShield - Intelligent Multi-Protocol Honeypot & Threat Intelligence Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Overview

HoneyShield is an intelligent, multi-protocol honeypot and threat intelligence platform designed to deceive, detect, and document cyber attackers in real time. It simulates production-grade services (SSH, HTTP, FTP, Telnet) to lure malicious actors, capture their tactics, and provide security teams with actionable intelligence.

### Key Features

- **Multi-Protocol Support**: SSH, HTTP, FTP, Telnet, SMTP
- **Real-Time Monitoring**: Web-based dashboard with live attack feeds
- **Attack Intelligence**: Captures credentials, commands, payloads, and attack patterns
- **IP Geolocation**: Enriches attack data with attacker location
- **Virtual File System**: Realistic fake Linux environment
- **Docker Ready**: One-command deployment
- **Database-Driven**: Structured logging and querying
- **Startup Ready**: Production-grade security and scalability

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Linux/macOS/Windows with WSL

### Local Setup (Development)

1. **Clone the repository**
   ```bash
   cd HoneyShield
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup configuration**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

5. **Initialize database**
   ```bash
   python -c "from database.connection import init_db; init_db()"
   ```

6. **Start honeypot engine**
   ```bash
   python -m honeypot_engine.engine
   ```

### Docker Deployment

1. **Build and start services**
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running**
   ```bash
   docker-compose ps
   ```

3. **View logs**
   ```bash
   docker-compose logs -f honeypot-engine
   ```

## 📁 Project Structure

```
HoneyShield/
├── honeypot_engine/          # Core honeypot services
│   ├── engine.py            # Main honeypot runner
│   ├── base_service.py      # Base honeypot service class
│   ├── ssh_honeypot.py      # SSH implementation
│   ├── http_honeypot.py     # HTTP implementation
│   ├── ftp_honeypot.py      # FTP implementation
│   ├── telnet_honeypot.py   # Telnet implementation
│   └── virtual_fs.py        # Virtual file system
├── database/                 # Database layer
│   ├── models.py            # SQLAlchemy ORM models
│   └── connection.py        # Database connection management
├── dashboard_backend/        # FastAPI backend
│   └── main.py              # REST API endpoints
├── dashboard_frontend/       # React frontend (placeholder)
├── geo_service/             # Geolocation service
│   └── geolocation.py       # IP geolocation module
├── tests/                    # Test suite
│   ├── test_ssh.py         # SSH brute-force test
│   ├── test_http.py        # HTTP scan test
│   ├── test_ftp.py         # FTP login test
│   ├── test_telnet.py      # Telnet login test
│   ├── validate_db.py      # Database validation
│   ├── run_all_tests.sh    # Test runner (Linux/macOS)
│   └── run_all_tests.bat   # Test runner (Windows)
├── config/                   # Configuration
│   └── config.yaml          # Main configuration file
├── docker-compose.yml        # Docker Compose orchestration
├── Dockerfile               # Main honeypot container
├── Dockerfile.backend       # Backend API container
└── README.md                # This file
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:

- **Port assignments**: SSH (2222), HTTP (8080), FTP (2121), Telnet (2323)
- **Database settings**: SQLite or PostgreSQL
- **Service enabled/disabled**: Toggle protocols
- **Log retention**: Configure log cleanup
- **Geolocation**: API key or offline database

## 🧪 Testing & Validation

### Run Individual Tests

```bash
# SSH brute-force test
python tests/test_ssh.py

# HTTP scanning test
python tests/test_http.py

# FTP login attempts
python tests/test_ftp.py

# Telnet login attempts
python tests/test_telnet.py

# Validate captured data
python tests/validate_db.py
```

### Run All Tests

```bash
# Linux/macOS
bash tests/run_all_tests.sh

# Windows
python tests/run_all_tests.bat
```

## 📊 Dashboard

### Access Dashboard UI
- **URL**: http://localhost:5000/dashboard (when frontend is implemented)
- **Default Credentials**: admin / admin123 (change in production!)

### API Endpoints

- `GET /api/stats` - Dashboard statistics
- `GET /api/events` - Attack events
- `GET /api/attackers` - Top attacker IPs
- `GET /api/credentials` - Most attempted credentials
- `GET /api/sessions` - Attack sessions
- `GET /api/protocol-distribution` - Attacks by protocol
- `GET /api/geo-distribution` - Attacks by country
- `GET /api/timeline` - Attack timeline

## 🗄️ Database Schema

### Key Tables

**attack_events**: Master event log
- id, timestamp, ip, protocol, port, success, session_id

**credentials**: Login attempts
- event_id, username, password, timestamp

**commands**: Commands executed
- event_id, command, output, timestamp

**http_requests**: Web requests
- event_id, method, path, query_string, payload, response_code

**sessions**: Full session records
- session_id, ip, protocol, start_time, end_time, duration_seconds

**geo_data**: IP geolocation
- ip, country, city, latitude, longitude, isp, asn

## 🔒 Security Considerations

- ✅ No real command execution - all commands are simulated
- ✅ Network isolation via Docker
- ✅ Non-root user execution
- ✅ No outbound network calls from honeypot
- ✅ Dashboard behind authentication (JWT)
- ✅ Rate limiting on login attempts
- ✅ Environment variables for sensitive data
- ✅ SSL/TLS ready for production

## 📈 Development Roadmap

### Phase 1: Core Engine (Complete ✓)
- Multi-threaded service runner
- SSH, HTTP, FTP, Telnet honeypots
- SQLite database setup
- Basic test scripts

### Phase 2: Intelligence & VFS (In Progress)
- Virtual file system
- Command parser
- IP geolocation
- PostgreSQL support

### Phase 3: Dashboard (Planned)
- React frontend
- Real-time WebSocket updates
- Interactive attack map (Leaflet.js)
- CSV/JSON exports

### Phase 4: Deployment & Demo (Planned)
- AWS deployment
- Complete test suite
- Performance optimization
- Documentation & demo

## 💼 Startup Go-To-Market

### Pricing Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0/mo | Self-hosted, all core features |
| **Startup** | $35/mo | Cloud deployment, email alerts |
| **Professional** | $120/mo | All protocols, SIEM integration, API |
| **Enterprise** | Custom | On-premise, compliance, SLA |

### Target Market

- Indian IT SMBs and startups
- Academic cybersecurity labs
- Bug bounty hunters
- Government security teams

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

HoneyShield is designed for legitimate security research and honeypot deployment. Users are responsible for legal compliance in their jurisdiction. Unauthorized network monitoring and attack simulation may be illegal. Use only in authorized test environments.

## 📞 Support & Contact

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Email**: support@honeyshield.io
- **Project**: Final Year Major Project + Startup Initiative

## 🎯 Project Status

- **Current Version**: 1.0.0 (Beta)
- **Last Updated**: March 2026
- **Development Status**: Active
- **Production Ready**: Phase 1-2 Complete, Phase 3-4 In Progress

---

**HoneyShield PRD v1.0** - *Make every attacker unknowingly teach you how to defend better.*
"# Major_HoneyPot_Project_MPN" 
"# Major_HoneyPot_Project_MPN" 
"# Major_HoneyPot_Project_MPN" 
