# HoneyShield Dashboard Frontend

Advanced Attack Intelligence Dashboard UI for HoneyShield honeypot system.

## Features

✨ **Real-time Monitoring**
- Live attack event tracking
- Auto-refreshing dashboard (configurable intervals)
- Real-time statistics updates

📊 **Comprehensive Visualizations**
- Attack timeline chart (time-series)
- Protocol breakdown pie chart
- Top attackers table
- Captured credentials tracker
- Multiple data views (graphs + tables)

🎯 **API Integration**
- Connected to HoneyShield backend API
- All 11 backend endpoints integrated
- Error handling and graceful degradation
- Mock data fallback for offline development

🎨 **Professional UI**
- Dark theme optimized for security operations center (SOC)
- Responsive design (desktop, tablet, mobile)
- Color-coded statistics cards
- Smooth animations and transitions
- Accessibility-focused

## Prerequisites

- Node.js 14.x or higher
- npm or yarn
- HoneyShield backend running on `localhost:5000`

## Installation

```bash
# Navigate to frontend directory
cd dashboard_frontend

# Install dependencies
npm install
```

## Running the Dashboard

### Development Mode

```bash
npm start
```

The dashboard will open at `http://localhost:3000`

### Production Build

```bash
npm run build
```

The `build/` directory contains optimized production files.

## Configuration

### API Endpoint

By default, the dashboard connects to `http://localhost:5000`. To use a different URL:

```bash
# Set environment variable
export REACT_APP_API_URL=http://your-api-server:5000

# Or create .env file
echo "REACT_APP_API_URL=http://your-api-server:5000" > .env
```

### Auto-refresh Interval

Change the refresh interval from the dashboard UI:
- 10 seconds (for active monitoring)
- 30 seconds (default, balanced)
- 1 minute (for lower bandwidth)
- 5 minutes (for background monitoring)

## Project Structure

```
dashboard_frontend/
├── public/
│   └── index.html              # HTML entry point
├── src/
│   ├── api/
│   │   └── dashboardAPI.js     # API client for backend
│   ├── components/
│   │   ├── StatCard.js         # Statistics card component
│   │   ├── AttackTimelineChart.js  # Time-series chart
│   │   ├── TopAttackersTable.js    # Attackers data table
│   │   ├── ProtocolBreakdown.js    # Protocol pie chart
│   │   └── CredentialsTable.js     # Credentials display
│   ├── pages/
│   │   └── Dashboard.js        # Main dashboard page
│   ├── App.js                  # Main app component
│   ├── App.css                 # Global styles
│   └── index.js                # React entry point
├── package.json                # Dependencies
└── .gitignore                  # Git ignore rules
```

## Components

### StatCard
Displays key metrics in visually distinct cards with icons and color coding.

### AttackTimelineChart
Area chart showing attack events over time (last 24 hours by default).

### TopAttackersTable
Data table listing top attacking IPs with attack counts, location, and timestamp.

### ProtocolBreakdown
Pie chart showing distribution of attacks by protocol (SSH, HTTP, FTP, Telnet).

### CredentialsTable
Table of captured credentials with masking for passwords and attempt counts.

## API Endpoints Used

The dashboard integrates with these backend endpoints:

- `GET /api/stats` - Overall statistics
- `GET /api/attackers` - Top attackers list
- `GET /api/timeline` - Attack timeline data
- `GET /api/credentials` - Captured credentials
- `GET /api/protocols` - Protocol breakdown
- `GET /api/http-requests` - HTTP request logs
- `GET /api/commands` - Command execution logs
- `GET /api/geo-distribution` - Geographic data
- `GET /api/health` - Backend health check

## Styling

The dashboard uses:
- **CSS-in-JS** for component styles
- **Responsive Grid** for layout
- **Dark theme** with blue accents (#1e293b, #3b82f6)
- **Custom color palette** for status indicators

### Color Scheme

- Primary: `#3b82f6` (Blue)
- Danger: `#ef4444` (Red) 
- Success: `#10b981` (Green)
- Warning: `#eab308` (Yellow)
- Background: `#0f172a` (Dark Blue)
- Text: `#e2e8f0` (Light Gray)

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

- **react** - UI framework
- **react-dom** - React rendering
- **axios** - HTTP client
- **recharts** - Chart library
- **react-scripts** - CRA tooling

## Troubleshooting

### Dashboard shows "API Connection Failed"

1. Ensure backend is running: `python honeypot_engine/engine.py` and `python -m uvicorn dashboard_backend/main:app`
2. Check that backend listens on port 5000
3. Verify no firewall blocking localhost connections
4. Check browser console for detailed error messages

### Empty data/charts

- Run attack tests to populate data: `python tests/test_*.py`
- Check backend API health: Visit `http://localhost:5000/api/health`
- Review backend logs for errors

### Styling issues

- Clear browser cache: `Ctrl+Shift+Delete` (Chrome/Firefox)
- Rebuild: `npm run build`
- Check browser DevTools (F12) for CSS errors

## Development

### Adding New Components

1. Create component in `src/components/`
2. Add corresponding CSS file
3. Import and use in Dashboard.js
4. Update dashboardAPI.js if new endpoint needed

### Running Tests

```bash
npm test
```

## Performance

- Chart updates are optimized with memoization
- API calls are batched on dashboard load
- Responsive images and lazy loading
- Compressed CSS/JS in production build

## Security

- No sensitive data stored in localStorage
- API endpoints behind backend authentication ready
- CORS configured for secure requests
- Input sanitization for user-controlled UI

## License

Part of HoneyShield open-source project
