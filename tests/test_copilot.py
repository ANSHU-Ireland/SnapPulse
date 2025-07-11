import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the Copilot service to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'snap-pulse', 'services', 'copilot'))

from main import app

client = TestClient(app)

def test_copilot_health():
    """Test that the copilot health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_analyze_endpoint_structure():
    """Test that the analyze endpoint has the correct structure."""
    # Mock request data
    test_request = {
        "snapcraft_yaml": """
name: test-snap
base: core22
version: '1.0'
summary: Test snap
description: A test snap for validation
grade: stable
confinement: strict

parts:
  my-part:
    plugin: nil
""",
        "repository_url": "https://github.com/test/test-repo",
        "issue_number": 1
    }
    
    # Note: This will fail without a GitHub token, but we test the structure
    response = client.post("/analyze", json=test_request)
    
    # Should return 400 for missing GitHub token, not 500 for bad structure
    assert response.status_code in [200, 400]
    
    if response.status_code == 400:
        data = response.json()
        assert "GitHub token not configured" in data["detail"]

def test_github_webhook_endpoint():
    """Test that the GitHub webhook endpoint accepts payloads."""
    test_payload = {
        "action": "created",
        "comment": {
            "body": "/snappulse fix this snap please"
        },
        "repository": {
            "html_url": "https://github.com/test/test-repo"
        },
        "issue": {
            "number": 123
        }
    }
    
    response = client.post("/github-webhook", json=test_payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "processing"
