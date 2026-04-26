# HoneyShield Dashboard - Quick Start Guide

## Prerequisites

✓ Node.js 14+ installed
✓ npm package manager available
✓ HoneyShield backend running (port 5000)

## Quick Start (3 steps)

### Step 1: Install Dependencies
```bash
cd dashboard_frontend
npm install
```
*Takes 1-2 minutes on first run*

### Step 2: Start Backend (if not already running)
In another terminal:
```bash
cd ..
python -m uvicorn dashboard_backend/main:app --port 5000
```

### Step 3: Start Dashboard
```bash
npm start
```
*Opens at http://localhost:3000 automatically*

## Accessing the Dashboard

- **URL**: http://localhost:3000
- **Default Page**: Full-featured attack intelligence dashboard
- **Auto-refresh**: Configurable (10s, 30s, 1min, 5min)

## What You'll See

1. **Header** - HoneyShield title with refresh controls
2. **Overview Cards** - Key metrics:
   - Total Events
   - Unique Attackers
   - Credentials Captured
   - HTTP Requests
   - Commands Executed
   - Protocols Used

3. **Left Column**:
   - Attack Timeline Chart (last 24 hours)
   - Protocol Breakdown Pie Chart

4. **Right Column**:
   - Top Attackers Table
   - Recent Captured Credentials

## Generating Test Data

To populate the dashboard with realistic attack data:

```bash
# Terminal 1: Start honeypot engine
python honeypot_engine/engine.py

# Terminal 2: Run attack tests
python tests/test_ssh.py
python tests/test_http.py
python tests/test_ftp.py
python tests/test_telnet.py
```

Then refresh the dashboard to see data populate real-time!

## Customization

### Change API URL
Edit `.env` file:
```
REACT_APP_API_URL=http://your-server:5000
```

### Change Refresh Interval
Use dropdown in dashboard header UI

### Modify Colors/Theme
Edit component CSS files in `src/components/`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API Connection Failed" | Check backend running on port 5000 |
| Empty charts/tables | Run test scripts to generate data |
| Page won't load | Try `npm install` again, then `npm start` |
| Blank screen | Check browser console (F12) for errors |

## Development Mode

```bash
npm start
```
- Hot reload enabled (changes auto-refresh)
- Source maps for debugging
- Detailed error messages

## Production Build

```bash
npm build
```
- Optimized and minified
- Ready for deployment
- `build/` directory contains static files

## File Structure

```
src/
├── App.js                  # Main component
├── pages/
│   └── Dashboard.js        # Dashboard page
├── components/             # Reusable components
│   ├── StatCard.js
│   ├── AttackTimelineChart.js
│   ├── TopAttackersTable.js
│   ├── ProtocolBreakdown.js
│   └── CredentialsTable.js
└── api/
    └── dashboardAPI.js     # API client
```

## Next Steps

1. ✅ Install and run dashboard
2. 🔧 Generate test attack data
3. 📊 Monitor live attack statistics
4. 🔍 Analyze attacker patterns
5. 🛡️ Implement security responses

## Support

For issues or questions:
- Check backend logs: `dashboard_backend/logs/`
- Review backend API: `http://localhost:5000/docs`
- Check browser console: Press F12

Enjoy your HoneyShield Dashboard! 🍯
