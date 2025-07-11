# SnapPulse Screenshots

## Dashboard Overview
![SnapPulse Dashboard](dashboard-overview.png)
*Real-time analytics dashboard showing snap download trends, ratings, and trending packages*

## API Documentation
![API Documentation](api-docs.png)
*Interactive OpenAPI documentation with live endpoint testing*

## Charts and Analytics
![Analytics Charts](analytics-charts.png)
*Interactive Chart.js visualizations with real-time data updates*

## Screenshots Coming Soon

To generate screenshots:

1. Start the SnapPulse services:
   ```bash
   cd /workspaces/SnapPulse/snap-pulse/services/api
   python main.py &
   cd ../dashboard
   python -m http.server 3000 &
   ```

2. Open the dashboard at `http://localhost:3000/demo.html`

3. Take screenshots of:
   - Dashboard overview with charts
   - API documentation at `http://localhost:8000/docs`
   - Different snap analytics views

4. Save as PNG files in this directory

The dashboard features:
- ✨ Real-time data updates every 5 seconds
- 📊 Interactive charts powered by Chart.js
- 🎛️ Snap and channel selection dropdowns
- 📈 Download trends and growth metrics
- ⭐ Rating and version tracking
- 🔥 Trending snaps sidebar
