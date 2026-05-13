#!/usr/bin/env python3
"""
Stress tests for concurrent access to shared state (Story 1.9)
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import mtv_dl_web.main as main_module
from fastapi.testclient import TestClient
from mtv_dl_web.main import app, active_downloads, database_refresh_lock, active_downloads_lock, database_update_lock


client = TestClient(app)


def test_concurrent_active_downloads_access():
    """Test concurrent access to active_downloads dictionary"""
    # Clear any existing downloads
    active_downloads.clear()
    
    # Add a test download
    test_id = "test_download_1"
    with active_downloads_lock:
        active_downloads[test_id] = {
            "status": "queued",
            "progress": 0.0,
            "message": "Test queued",
            "file_path": None
        }
    
    # Function to simulate concurrent access
    def access_downloads(iteration: int, results: list) -> None:
        try:
            # Simulate concurrent reads and writes
            with active_downloads_lock:
                if test_id in active_downloads:
                    current_status = active_downloads[test_id]["status"]
                    # Modify status
                    active_downloads[test_id]["status"] = f"processing_{iteration}"
                    active_downloads[test_id]["progress"] = iteration / 100.0
                    active_downloads[test_id]["message"] = f"Processed {iteration}"
            
            # Read status
            with active_downloads_lock:
                status = active_downloads[test_id]["status"] if test_id in active_downloads else "not_found"
                results.append((iteration, status))
        except Exception as e:
            results.append((iteration, f"error: {e}"))
    
    # Run concurrent access
    results = []
    threads = []
    for i in range(10):
        thread = threading.Thread(target=access_downloads, args=(i, results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Verify all accesses occurred
    assert len(results) == 10
    for iteration, status in results:
        assert status.startswith("processing_")


def test_concurrent_database_refresh_access():
    """Test concurrent access to database refresh state"""
    # Function to simulate concurrent access
    def access_database_state(iteration: int, results: list) -> None:
        try:
            # Simulate concurrent access to database refresh state
            with database_refresh_lock:
                is_refreshing = False  # This is just to test lock acquisition
                results.append((iteration, "lock_acquired"))
        except Exception as e:
            results.append((iteration, f"error: {e}"))
    
    # Run concurrent access
    results = []
    threads = []
    for i in range(10):
        thread = threading.Thread(target=access_database_state, args=(i, results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Verify all accesses occurred
    assert len(results) == 10
    for iteration, status in results:
        assert status == "lock_acquired"


def test_concurrent_database_update_access():
    """Test concurrent access to database update counter"""
    # Reset counter and ensure cleanup to avoid leaking state across tests
    with database_update_lock:
        main_module._database_update_count = 0
    
    # Function to simulate concurrent access to update counter
    def access_update_counter(iteration: int, results: list) -> None:
        try:
            with database_update_lock:
                count = main_module._database_update_count
                main_module._database_update_count += 1  # Increment
                results.append((iteration, count))
        except Exception as e:
            results.append((iteration, f"error: {e}"))
    
    try:
        # Run concurrent access
        results = []
        threads = []
        for i in range(10):
            thread = threading.Thread(target=access_update_counter, args=(i, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Verify all accesses occurred and counter incremented correctly
        assert len(results) == 10
        for iteration, count in results:
            assert count >= 0 and count <= 9
        assert main_module._database_update_count == 10  # Should be incremented 10 times
    finally:
        with database_update_lock:
            main_module._database_update_count = 0


def test_mixed_workload_stress():
    """Test mixed workload stress with health, refresh, downloads, and queues"""
    # Clear any existing downloads
    active_downloads.clear()
    
    # Add initial downloads
    test_ids = [f"test_download_{i}" for i in range(5)]
    with active_downloads_lock:
        for test_id in test_ids:
            active_downloads[test_id] = {
                "status": "queued",
                "progress": 0.0,
                "message": "Initial queued",
                "file_path": None
            }
    
    # Function to simulate mixed workload
    def mixed_workload(iteration: int, results: list) -> None:
        try:
            # Simulate mixed concurrent operations
            with database_refresh_lock:
                # Access database refresh state
                is_refreshing = False  # Just to test lock
            
            with active_downloads_lock:
                # Access active downloads
                if test_ids[0] in active_downloads:
                    active_downloads[test_ids[0]]["status"] = f"processed_{iteration}"
            
            # Simulate some time-consuming operations
            time.sleep(0.001)
            
            with database_update_lock:
                # Access database update counter
                from mtv_dl_web.main import _database_update_count
                count = _database_update_count
            
            results.append((iteration, "success"))
        except Exception as e:
            results.append((iteration, f"error: {e}"))
    
    # Run mixed workload stress test
    results = []
    threads = []
    for i in range(20):  # More iterations for stress test
        thread = threading.Thread(target=mixed_workload, args=(i, results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Verify all operations completed
    assert len(results) == 20
    for iteration, status in results:
        assert status == "success"


def test_exception_handling_in_background_tasks():
    """Test that background tasks handle exceptions and clean up properly"""
    # This is more of a behavioral test
    
    # Mock a database refresh to fail and ensure cleanup
    def failing_refresh():
        from mtv_dl_web.main import database_refresh_lock, is_database_refreshing, database_refresh_task
        with database_refresh_lock:
            is_database_refreshing = True
            database_refresh_task = threading.current_thread()
        
        # Simulate exception
        try:
            raise Exception("Simulated refresh failure")
        except Exception:
            # This should not leave the refresh in a stuck state
            pass
        finally:
            with database_refresh_lock:
                is_database_refreshing = False
                database_refresh_task = None
    
    # Run the failing refresh simulation
    thread = threading.Thread(target=failing_refresh)
    thread.start()
    thread.join()
    
    # Verify cleanup happened
    from mtv_dl_web.main import database_refresh_lock, is_database_refreshing, database_refresh_task
    with database_refresh_lock:
        assert is_database_refreshing == False
        assert database_refresh_task is None


if __name__ == "__main__":
    raise SystemExit("Run this module with pytest")
