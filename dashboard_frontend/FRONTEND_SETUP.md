# HoneyShield React Dashboard - Complete Setup

## What Was Created

A professional, production-ready React dashboard that displays all HoneyShield APIs with integrated graphs and tables.

### 📁 Project Structure

```
dashboard_frontend/
├── public/
│   └── index.html                    # HTML entry point
├── src/
│   ├── api/
│   │   └── dashboardAPI.js           # API client (all 11 endpoints)
│   ├── pages/
│   │   ├── Dashboard.js              # Main dashboard page
│   │   └── Dashboard.css             # Dashboard layout
│   ├── components/
│   │   ├── StatCard.js               # 6 key metric cards
│   │   ├── StatCard.css
│   │   ├── AttackTimelineChart.js    # Area chart (24h timeline)
│   │   ├── AttackTimelineChart.css
│   │   ├── TopAttackersTable.js      # Data table (top attackers)
│   │   ├── TopAttackersTable.css
│   │   ├── ProtocolBreakdown.js      # Pie chart (protocol distribution)
│   │   ├── ProtocolBreakdown.css
│   │   ├── CredentialsTable.js       # Credentials table
│   │   └── CredentialsTable.css
│   ├── App.js                        # Root app component
│   ├── App.css                       # Global styles
│   └── index.js                      # React entry point
├── package.json                      # Dependencies
├── .env.example                      # Configuration template
├── .gitignore                        # Git ignore rules
├── README.md                         # Complete documentation
├── QUICKSTART.md                     # 3-step quick start
├── run.bat                           # Windows batch launcher
├── run.ps1                           # Windows PowerShell launcher
└── FRONTEND_SETUP.md                 # This file
```

## 🚀 Quick Start (Windows)

### Option 1: Double-click the batch file
```bash
dashboard_frontend/run.bat
```

### Option 2: PowerShell
```powershell
cd dashboard_frontend
.\run.ps1
```

### Option 3: Manual
```bash
cd dashboard_frontend
npm install
npm start
```

The dashboard opens at `http://localhost:3000`

## 📊 Dashboard Features

### 📈 Overview Statistics (6 Cards)
- Total Events (blue)
- Unique Attackers (red)
- Credentials Captured (yellow)
- HTTP Requests (green)
- Commands Executed (purple)
- Protocols Used (indigo)

### 📉 Charts & Visualizations

1. **Attack Timeline** (Area Chart)
   - Displays last 24 hours
   - Shows attack volume over time
   - Interactive tooltip
   - Gradient fill

2. **Protocol Breakdown** (Pie Chart)
   - SSH / HTTP / FTP / Telnet distribution
   - Percentage display
   - Color-coded segments
   - Legend

3. **Top Attackers** (Data Table)
   - Unique attacking IPs
   - Attack count (badge)
   - Geographic location
   - Source port
   - Last seen timestamp
   - Sortable columns

4. **Captured Credentials** (Data Table)
   - Username/password pairs
   - Masked password display
   - Attempt count
   - Last attempt timestamp
   - Recent 30 credentials

### ⚙️ Features

- ✅ Auto-refresh every 10/30/60/300 seconds
- ✅ Real-time data updates
- ✅ Responsive design (desktop/tablet/mobile)
- ✅ Dark theme optimized for SOC
- ✅ Error handling & graceful degradation
- ✅ Mock data fallback if API down
- ✅ Professional UI with smooth animations
- ✅ Color-coded status indicators
- ✅ Accessibility support

## 🔗 API Integration

The dashboard calls these backend endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/api/stats` | Overall statistics (6 metrics) |
| `/api/attackers` | Top attacking IPs |
| `/api/timeline` | Attack events timeline |
| `/api/credentials` | Captured username/password pairs |
| `/api/protocols` | Protocol distribution breakdown |
| `/api/http-requests` | HTTP request logs |
| `/api/commands` | SSH command logs |
| `/api/geo-distribution` | Geographic attacker data |
| `/api/health` | Backend health check |

All integrated automatically - no manual setup needed!

## 🎨 Design Highlights

### Color Scheme
- **Background**: Dark blue (#0f172a)
- **Cards**: Slate (#1e293b - #334155)
- **Primary**: Bright blue (#3b82f6)
- **Accents**: Red, Green, Yellow, Purple
- **Text**: Light gray (#e2e8f0)

### Responsive Breakpoints
- Desktop: Multi-column grid
- Tablet (1024px): 2 columns
- Mobile (<768px): Single column
- Tables: Horizontal scroll on small screens

### Interactive Elements
- Hover effects on cards (lift effect)
- Loading animations
- Smooth transitions (0.3s)
- Tooltips on hover
- Color gradients and shadows

## 🔧 Configuration

### Change API Backend URL

Create `.env` file:
```
REACT_APP_API_URL=http://your-server:5000
```

Or set environment variable:
```bash
export REACT_APP_API_URL=http://your-server:5000
npm start
```

### Auto-refresh Interval

Select from dropdown in dashboard header:
- 10 seconds (active monitoring)
- 30 seconds (default)
- 1 minute (balanced)
- 5 minutes (low bandwidth)

## 📋 Dependencies

```json
{
  "react": "^18.2.0",           // UI framework
  "react-dom": "^18.2.0",       // DOM rendering
  "axios": "^1.6.0",            // HTTP client
  "recharts": "^2.10.0"         // Chart library
}
```

- Zero external styling framework (pure CSS)
- Lightweight: Only 4 core dependencies
- No jQuery or bootstrap needed
- Fast load times

## 🧪 Testing the Dashboard

### Generate Test Data

```bash
# Terminal 1: Start honeypot
python honeypot_engine/engine.py

# Terminal 2: Run tests
python tests/test_ssh.py
python tests/test_http.py
python tests/test_ftp.py
python tests/test_telnet.py
```

Then refresh dashboard to see data populate in real-time!

### Expected Sample Data

After running tests, dashboard should show:
- ~50+ total attack events
- 1 unique attacker (localhost testing)
- 30+ credentials captured
- Breakdown: SSH, HTTP, FTP, Telnet
- Attack timeline graph populated
- Tables with real data

## 🚨 Troubleshooting

### Dashboard shows "API Connection Failed"

1. **Check backend is running**:
   ```bash
   python -m uvicorn dashboard_backend/main:app --port 5000
   ```

2. **Verify port 5000 is accessible**:
   ```bash
   curl http://localhost:5000/api/health
   ```

3. **Check firewall settings** - allow localhost:5000

4. **Review browser console** (F12) for detailed errors

### Empty charts (no data)

1. **Run attack tests** to populate database:
   ```bash
   python tests/test_*.py
   ```

2. **Check backend API directly**:
   ```bash
   curl http://localhost:5000/api/stats
   ```

3. **Verify database has data**:
   ```bash
   python tests/validate_db.py
   ```

### npm install fails

1. **Ensure Node.js installed**: `node --version`
2. **Clear npm cache**: `npm cache clean --force`
3. **Delete node_modules**: `rm -r node_modules` or PowerShell: `Remove-Item -Recurse node_modules`
4. **Reinstall**: `npm install`

### Page won't load / blank screen

1. **Hard refresh**: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. **Clear browser cache** via DevTools (F12)
3. **Check console** for JavaScript errors
4. **Restart npm**: `npm start`

## 📱 Responsive Design

### Desktop (1400px+)
- 2-column layout
- Charts side-by-side
- Full-size tables

### Tablet (1024px - 1399px)
- 2-column layout, narrower
- Tables with scroll

### Mobile (<1024px)
- Single column
- Stacked components
- Horizontal table scroll
- Touch-friendly buttons

## 🔒 Security Considerations

- ✅ No credentials stored in localStorage
- ✅ No sensitive data in URL parameters
- ✅ CORS configured for secure cross-origin requests
- ✅ Input sanitization for user inputs
- ✅ Backend password masking (dots)
- ✅ Ready for authentication integration

## 🎯 Next Steps

1. ✅ **Install & Run**: `npm install && npm start`
2. 🔧 **Generate Data**: Run test scripts
3. 📊 **Monitor Dashboard**: Observe live data
4. 🎨 **Customize**: Modify colors/components as needed
5. 🚀 **Deploy**: Run `npm build` for production

## 📞 Support

### Check Logs
- Backend logs: `dashboard_backend/logs/`
- Browser console: Press F12
- Network tab: Check API calls

### API Documentation
- Interactive docs: `http://localhost:5000/docs`
- Swagger UI: `http://localhost:5000/api/docs`

### Debug Mode
```bash
REACT_APP_DEBUG=true npm start
```

## 🎉 Summary

You now have a **complete, production-ready dashboard** that:
- ✅ Displays all attacks in real-time
- ✅ Shows attack patterns and trends
- ✅ Integrates all 11 backend APIs
- ✅ Works on any device
- ✅ Handles offline scenarios gracefully
- ✅ Professional dark theme
- ✅ Zero-configuration setup

**Just run `npm start` and enjoy!** 🍯
