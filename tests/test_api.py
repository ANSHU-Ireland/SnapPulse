import pytest
import httpx
from fastapi.testclient import TestClient
import sys
import os

# Add the API service to the path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "snap-pulse", "services", "api")
)

from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that the health endpoint returns 200 and correct structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"


def test_stats_endpoint():
    """Test that the stats endpoint returns snap data."""
    # First ingest some test data
    test_data = {
        "snap_name": "firefox",
        "channel": "stable",
        "download_total": 150000,
        "download_last_30_days": 12000,
        "rating": 4.2,
        "version": "1.0.0",
        "confinement": "strict",
        "grade": "stable",
        "publisher": "Test Publisher",
    }

    ingest_response = client.post("/ingest", json=test_data)
    assert ingest_response.status_code == 200

    # Now test the stats endpoint
    response = client.get("/stats/firefox/stable")
    assert response.status_code == 200
    data = response.json()

    # Check required fields
    required_fields = [
        "snap_name",
        "channel",
        "download_total",
        "download_last_30_days",
        "rating",
        "version",
        "last_updated",
        "confinement",
        "grade",
        "publisher",
        "trending_score",
    ]

    for field in required_fields:
        assert field in data, f"Missing field: {field}"

    assert data["snap_name"] == "firefox"
    assert data["channel"] == "stable"
    assert data["download_total"] == 150000


def test_stats_endpoint_no_data():
    """Test that the stats endpoint returns 404 when no data exists."""
    response = client.get("/stats/nonexistent-snap/stable")
    assert response.status_code == 404
    data = response.json()
    assert "No data yet" in data["detail"]


def test_trending_endpoint():
    """Test that the trending endpoint returns trending data."""
    response = client.get("/trending")
    assert response.status_code == 200
    data = response.json()

    assert "trending" in data
    assert isinstance(data["trending"], list)
    assert len(data["trending"]) > 0

    # Check first trending item structure
    first_item = data["trending"][0]
    assert "name" in first_item
    assert "downloads_growth" in first_item
    assert "rating" in first_item


def test_ingest_endpoint():
    """Test that the ingest endpoint accepts new data."""
    test_data = {
        "snap_name": "test-snap",
        "channel": "stable",
        "download_total": 100000,
        "download_last_30_days": 5000,
        "rating": 4.5,
        "version": "1.0.0",
        "confinement": "strict",
        "grade": "stable",
        "publisher": "Test Publisher",
    }

    response = client.post("/ingest", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    # Verify the data was stored by retrieving it
    response = client.get("/stats/test-snap/stable")
    assert response.status_code == 200
    retrieved_data = response.json()
    assert retrieved_data["snap_name"] == "test-snap"
    assert retrieved_data["download_total"] == 100000
