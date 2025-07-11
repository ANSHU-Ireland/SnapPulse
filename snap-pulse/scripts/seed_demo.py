#!/usr/bin/env python3
"""
Seed demo data for SnapPulse dashboard.
This script generates realistic-looking analytics data for demonstration purposes.
"""

import json
import random
import datetime
import math
from pathlib import Path

def generate_snap_data(snap_name: str, days: int = 180) -> dict:
    """Generate realistic download and engagement data for a snap."""
    
    base_downloads = random.randint(50000, 500000)
    data_points = []
    
    for i in range(days):
        date = datetime.datetime.now() - datetime.timedelta(days=days-i)
        
        # Add some seasonality and trend
        trend_factor = 1 + (i / days) * 0.3  # Growing trend
        seasonal_factor = 1 + 0.2 * math.sin(2 * math.pi * i / 30)  # Monthly cycle
        random_factor = random.uniform(0.8, 1.2)
        
        daily_downloads = int(base_downloads * trend_factor * seasonal_factor * random_factor / days)
        
        data_points.append({
            "date": date.strftime("%Y-%m-%d"),
            "downloads": daily_downloads,
            "active_users": int(daily_downloads * random.uniform(0.7, 0.9)),
            "rating": round(random.uniform(3.5, 4.8), 1),
            "crashes": random.randint(0, max(1, daily_downloads // 10000)),
        })
    
    return {
        "snap_name": snap_name,
        "total_downloads": sum(d["downloads"] for d in data_points),
        "data_points": data_points,
        "channels": {
            "stable": {"downloads": sum(d["downloads"] for d in data_points), "version": "1.0.0"},
            "candidate": {"downloads": int(sum(d["downloads"] for d in data_points) * 0.1), "version": "1.1.0"},
            "beta": {"downloads": int(sum(d["downloads"] for d in data_points) * 0.05), "version": "1.2.0"},
            "edge": {"downloads": int(sum(d["downloads"] for d in data_points) * 0.01), "version": "1.3.0-dev"},
        }
    }

def main():
    import math
    
    print("🌱 Seeding SnapPulse demo data...")
    
    # Popular snaps to generate data for
    snaps = [
        "firefox", "discord", "code", "spotify", "slack", "gimp", 
        "vlc", "telegram-desktop", "skype", "zoom-client"
    ]
    
    demo_data = {}
    
    for snap in snaps:
        print(f"  📊 Generating data for {snap}...")
        demo_data[snap] = generate_snap_data(snap)
    
    # Save to JSON file
    output_file = Path(__file__).parent.parent / "data" / "demo_data.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(demo_data, f, indent=2)
    
    print(f"✅ Demo data saved to {output_file}")
    print(f"📈 Generated data for {len(snaps)} snaps with {len(demo_data[snaps[0]]['data_points'])} days of history each")

if __name__ == "__main__":
    main()
