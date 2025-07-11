import os, asyncio, datetime as dt
from snapstore import SnapStore
from feast import FeatureStore

store_api = SnapStore()
fs = FeatureStore(repo_path="feast_repo")

async def job():
    snap = os.environ.get("SNAP_NAME", "firefox")  # Default to firefox for testing
    try:
        meta = store_api.details(snap)
        record = {
            "snap": snap,
            "download_total": meta.channel_downloads.get("stable", 0),
            "timestamp": dt.datetime.utcnow()
        }
        fs.write_to_online_store("snap_metrics", [record])
        print("pushed metrics", record)
    except Exception as e:
        print(f"Error collecting metrics for {snap}: {e}")

async def main():
    print("Starting SnapPulse Collector...")
    while True:
        await job()
        await asyncio.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    asyncio.run(main())
