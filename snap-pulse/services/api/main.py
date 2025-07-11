from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from feast import FeatureStore  # Commented out for local demo
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

app = FastAPI(title="SnapPulse API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Feast feature store
# fs = FeatureStore(repo_path="feast_repo")  # Commented out for local demo

@app.get("/")
async def root():
    return {"message": "SnapPulse API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/stats/{snap_name}/{channel}")
async def get_snap_stats(snap_name: str, channel: str = "stable"):
    """Get statistics for a specific snap and channel."""
    try:
        # For now, return mock data since we need to set up the full pipeline
        # In a real implementation, this would query Feast and OpenSearch
        mock_data = {
            "snap_name": snap_name,
            "channel": channel,
            "download_total": 150000,
            "download_last_30_days": 12000,
            "rating": 4.2,
            "version": "1.0.0",
            "last_updated": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "confinement": "strict",
            "grade": "stable",
            "publisher": "Canonical",
            "trending_score": 85.5
        }
        return mock_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@app.get("/stats/{snap_name}")
async def get_snap_all_channels(snap_name: str):
    """Get statistics for a snap across all channels."""
    channels = ["stable", "candidate", "beta", "edge"]
    results = {}
    
    for channel in channels:
        # Mock data for each channel
        results[channel] = {
            "download_total": 150000 - (channels.index(channel) * 20000),
            "version": f"1.{channels.index(channel)}.0",
            "last_updated": (datetime.utcnow() - timedelta(days=channels.index(channel))).isoformat()
        }
    
    return {
        "snap_name": snap_name,
        "channels": results,
        "total_downloads": sum(ch["download_total"] for ch in results.values())
    }

@app.get("/trending")
async def get_trending_snaps(limit: int = 10):
    """Get trending snaps."""
    # Mock trending data
    trending_snaps = [
        {"name": "firefox", "downloads_growth": 15.2, "rating": 4.3},
        {"name": "discord", "downloads_growth": 12.8, "rating": 4.1},
        {"name": "code", "downloads_growth": 10.5, "rating": 4.5},
        {"name": "slack", "downloads_growth": 8.3, "rating": 4.0},
        {"name": "spotify", "downloads_growth": 7.9, "rating": 4.2},
    ]
    
    return {"trending": trending_snaps[:limit]}

@app.post("/webhook/github")
async def github_webhook(payload: Dict):
    """Handle GitHub webhooks for copilot integration."""
    # This will be used by the copilot service
    return {"status": "received", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
