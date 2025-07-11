# SnapPulse Dashboard Screenshot

![SnapPulse Dashboard](dashboard-overview.png)

*Real-time analytics dashboard showing snap download trends, ratings, and trending packages*

## How to Generate Screenshots

1. Start SnapPulse services:
   ```bash
   cd /workspaces/SnapPulse/snap-pulse/services/api
   python main.py &
   cd ../dashboard  
   python -m http.server 3000 &
   ```

2. Open `http://localhost:3000/demo.html` in browser

3. Take screenshots and save as PNG files in this directory

## Dashboard Features Shown

- ✨ Real-time data updates every 5 seconds
- 📊 Interactive Chart.js line graphs 
- 🎛️ Snap and channel selection dropdowns
- 📈 Download trends and growth metrics
- ⭐ Rating and version information
- 🔥 Top trending snaps sidebar
