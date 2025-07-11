#!/usr/bin/env python3
"""
SnapPulse Collector Service

Collects snap package data from the Snap Store API and forwards it to the API service.
"""

import asyncio
import datetime as dt
import json
import os
import logging
from typing import Dict, Any

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SNAP_NAME = os.getenv("SNAP_NAME", "firefox")
INTERVAL = int(os.getenv("POLL_SEC", "1800"))  # 30 minutes default
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Snap Store API base URL
SNAP_STORE_API = "https://api.snapcraft.io/v2"


async def get_snap_info(snap_name: str) -> Dict[str, Any]:
    """Get snap information from the Snap Store API."""
    async with httpx.AsyncClient() as client:
        try:
            # Get snap details
            response = await client.get(
                f"{SNAP_STORE_API}/snaps/info/{snap_name}",
                headers={
                    "Snap-Device-Series": "16",
                    "User-Agent": "SnapPulse/1.0",
                },
            )
            response.raise_for_status()

            snap_data = response.json()
            logger.info(f"Retrieved data for snap: {snap_name}")

            return {
                "snap_name": snap_name,
                "title": snap_data.get("name", snap_name),
                "summary": snap_data.get("summary", ""),
                "description": snap_data.get("description", ""),
                "publisher": snap_data.get("publisher", {}).get("display-name", ""),
                "license": snap_data.get("license", ""),
                "website": snap_data.get("website", ""),
                "contact": snap_data.get("contact", ""),
                "categories": [
                    cat.get("name", "") for cat in snap_data.get("categories", [])
                ],
                "channels": list(snap_data.get("channels", {}).keys()),
                "timestamp": dt.datetime.utcnow().isoformat(),
                "download_size": snap_data.get("download", {}).get("size", 0),
                "installed_size": snap_data.get("installed-size", 0),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting snap info: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting snap info: {e}")
            return None


async def send_to_api(data: Dict[str, Any]) -> bool:
    """Send collected data to the API service."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_URL}/ingest", json=data, timeout=30.0)
            response.raise_for_status()
            logger.info(f"Successfully sent data to API: {data['snap_name']}")
            return True

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending to API: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending to API: {e}")
            return False


async def collect_and_send():
    """Main collection function - get snap data and send to API."""
    logger.info(f"Collecting data for snap: {SNAP_NAME}")

    snap_data = await get_snap_info(SNAP_NAME)
    if snap_data:
        success = await send_to_api(snap_data)
        if success:
            logger.info(f"Collection cycle completed successfully for {SNAP_NAME}")
        else:
            logger.error(f"Failed to send data for {SNAP_NAME}")
    else:
        logger.error(f"Failed to get data for {SNAP_NAME}")


async def main():
    """Main collector loop."""
    logger.info(f"Starting SnapPulse Collector")
    logger.info(f"Monitoring snap: {SNAP_NAME}")
    logger.info(f"Collection interval: {INTERVAL} seconds")
    logger.info(f"API endpoint: {API_URL}")

    while True:
        try:
            await collect_and_send()
        except Exception as e:
            logger.error(f"Error in collection cycle: {e}")

        logger.info(f"Waiting {INTERVAL} seconds until next collection...")
        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
