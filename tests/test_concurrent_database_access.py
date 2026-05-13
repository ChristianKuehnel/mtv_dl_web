#!/usr/bin/env python3
"""
Test for concurrent database access during refresh (Story 1.6)
"""

import os
import time
import threading
import sys
from pathlib import Path
from unittest.mock import patch

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
# Removed redundant path for mtv_dl as it's now handled via standard dependency

from fastapi.testclient import TestClient
from mtv_dl_web.main import app, get_database_refresh_status


client = TestClient(app)

def test_concurrent_database_access():
    """Test that database operations work during refresh"""
    response = client.get('/health')
    assert response.status_code == 200
    health_data = response.json()
    assert 'status' in health_data
    assert 'database' in health_data

    db_status_response = client.get('/api/database/status')
    assert db_status_response.status_code == 200
    db_status_data = db_status_response.json()
    assert 'is_refreshing' in db_status_data

    with patch('mtv_dl_web.main.is_database_refreshing', True):
        concurrent_response = client.get('/health')
        assert concurrent_response.status_code == 200
        assert concurrent_response.json()['status'] == 'updating'

        db_status_during_refresh = get_database_refresh_status()
        assert db_status_during_refresh['is_refreshing']

    def make_request(results: list[bool]) -> None:
        response = client.get('/health')
        results.append(response.status_code == 200)

    threads = []
    results: list[bool] = []
    for _ in range(5):
        thread = threading.Thread(target=make_request, args=(results,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    assert sum(results) == 5


def test_acceptance_criteria():
    """Test specific acceptance criteria for Story 1.6"""
    with patch('mtv_dl_web.main.is_database_refreshing', True):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'updating'

    start_time = time.time()
    response = client.get('/health')
    response_time = (time.time() - start_time) * 1000
    assert response.status_code == 200
    assert response_time <= 500

    with patch('mtv_dl_web.main.is_database_refreshing', True):
        status_response = client.get('/api/download/status')
        assert status_response.status_code == 200


def test_remove_download_status_during_refresh():
    """AC-21 includes remove operations while refresh is active."""
    active_id = 'story-1-6-test-download'
    with patch('mtv_dl_web.main.active_downloads', {active_id: {'status': 'queued', 'progress': 0.0, 'message': 'Queued'}}):
        with patch('mtv_dl_web.main.is_database_refreshing', True):
            remove_response = client.delete(f'/api/download/status/{active_id}')
            assert remove_response.status_code == 200
            assert remove_response.json()['download_id'] == active_id


if __name__ == "__main__":
    raise SystemExit("Run this module with pytest")
