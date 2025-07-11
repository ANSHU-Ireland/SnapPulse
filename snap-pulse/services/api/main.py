from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import uvicorn
import os
import httpx

app = FastAPI(title="SnapPulse API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Data models
class SnapData(BaseModel):
    snap_name: str
    channel: str
    download_total: int
    download_last_30_days: int
    rating: float
    version: str
    last_updated: datetime
    confinement: str
    grade: str
    publisher: str
    trending_score: float


class IngestData(BaseModel):
    snap_name: str
    channel: str
    download_total: int
    download_last_30_days: int
    rating: float
    version: str
    confinement: str
    grade: str
    publisher: str


# In-memory storage for demo (replace with OpenSearch in production)
snap_data_store: Dict[str, Dict[str, SnapData]] = {}


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
        # Check if we have real data
        if snap_name in snap_data_store and channel in snap_data_store[snap_name]:
            data = snap_data_store[snap_name][channel]
            return {
                "snap_name": data.snap_name,
                "channel": data.channel,
                "download_total": data.download_total,
                "download_last_30_days": data.download_last_30_days,
                "rating": data.rating,
                "version": data.version,
                "last_updated": data.last_updated.isoformat(),
                "confinement": data.confinement,
                "grade": data.grade,
                "publisher": data.publisher,
                "trending_score": data.trending_score,
            }

        # No real data available yet
        raise HTTPException(
            status_code=404, detail="No data yet – wait for collector"
        )
    except HTTPException:
        raise
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
            "last_updated": (
                datetime.utcnow() - timedelta(days=channels.index(channel))
            ).isoformat(),
        }

    return {
        "snap_name": snap_name,
        "channels": results,
        "total_downloads": sum(ch["download_total"] for ch in results.values()),
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
async def github_webhook_handler(payload: dict):
    """Forward GitHub webhooks to the Copilot service."""
    try:
        # Forward to copilot service
        copilot_url = os.environ.get("COPILOT_ENDPOINT", "http://localhost:8001")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{copilot_url}/github-webhook", json=payload
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook forwarding failed: {str(e)}")


@app.post("/ingest")
async def ingest_snap_data(data: IngestData):
    """Ingest snap data from collector"""
    try:
        snap_data = SnapData(
            snap_name=data.snap_name,
            channel=data.channel,
            download_total=data.download_total,
            download_last_30_days=data.download_last_30_days,
            rating=data.rating,
            version=data.version,
            last_updated=datetime.now(),
            confinement=data.confinement,
            grade=data.grade,
            publisher=data.publisher,
            trending_score=calculate_trending_score(data),
        )

        # Store data
        if data.snap_name not in snap_data_store:
            snap_data_store[data.snap_name] = {}
        snap_data_store[data.snap_name][data.channel] = snap_data

        return {"status": "success", "message": "Data ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest data: {str(e)}")


def calculate_trending_score(data: IngestData) -> float:
    """Calculate trending score based on downloads and rating"""
    # Simple algorithm: weight recent downloads more heavily
    base_score = data.rating * 10
    download_boost = min(data.download_last_30_days / 1000, 50)  # Cap at 50
    return round(base_score + download_boost, 1)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
