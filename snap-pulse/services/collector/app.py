import os, asyncio, datetime as dt
import httpx
from snapstore import SnapStore
from feast import FeatureStore

store_api = SnapStore()
fs = FeatureStore(repo_path="feast_repo")

# API endpoint for ingesting data
API_ENDPOINT = os.environ.get("API_ENDPOINT", "http://localhost:8000")


async def job():
    snap = os.environ.get("SNAP_NAME", "firefox")  # Default to firefox for testing
    try:
        meta = store_api.details(snap)

        # Prepare data for both Feast and API
        record = {
            "snap": snap,
            "download_total": meta.channel_downloads.get("stable", 0),
            "timestamp": dt.datetime.utcnow(),
        }

        # Store in Feast
        fs.write_to_online_store("snap_metrics", [record])
        print("Pushed to Feast:", record)

        # Also send to API for immediate availability
        api_data = {
            "snap_name": snap,
            "channel": "stable",
            "download_total": meta.channel_downloads.get("stable", 0),
            "download_last_30_days": meta.channel_downloads.get("stable", 0)
            // 10,  # Estimate
            "rating": getattr(meta, "rating", 4.0),
            "version": getattr(meta, "version", "1.0.0"),
            "confinement": getattr(meta, "confinement", "strict"),
            "grade": getattr(meta, "grade", "stable"),
            "publisher": getattr(meta, "publisher", "Unknown"),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_ENDPOINT}/ingest", json=api_data)
            if response.status_code == 200:
                print("Pushed to API:", api_data)
            else:
                print(f"Failed to push to API: {response.status_code}")

    except Exception as e:
        print(f"Error collecting metrics for {snap}: {e}")


async def main():
    print("Starting SnapPulse Collector...")
    while True:
        await job()
        await asyncio.sleep(1800)  # 30 minutes


if __name__ == "__main__":
    asyncio.run(main())
