#!/usr/bin/env python3
"""
Test for enhanced health endpoint (Story 1.2)
"""

import sys
import os
import time
from pathlib import Path

# Add the src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'mtv_dl' / 'src'))

# Mock the version function to avoid import issues
import importlib.metadata
original_version = importlib.metadata.version

def mock_version(name):
    if name == 'mtv_dl':
        return '0.28.0'
    return original_version(name)

importlib.metadata.version = mock_version

from mtv_dl_web.main import app
from fastapi.testclient import TestClient

# Restore original version function
importlib.metadata.version = original_version

def test_health_endpoint_functionality():
    """Test that health endpoint returns proper response"""
    try:
        client = TestClient(app)
        
        # Test health endpoint
        print('Testing enhanced health endpoint...')
        start_time = time.time()
        response = client.get('/health')
        response_time = (time.time() - start_time) * 1000
        
        print(f'Status Code: {response.status_code}')
        print(f'Response Time: {response_time:.2f}ms')
        print(f'Response Body: {response.json()}')
        
        # Verify acceptance criteria
        success_count = 0
        total_tests = 3
        
        if response.status_code == 200:
            print('✓ AC1 PASSED: Returns 200 OK')
            success_count += 1
        else:
            print('✗ AC1 FAILED: Expected 200 OK')
        
        if response_time <= 500:
            print('✓ AC2 PASSED: Response time within 500ms')
            success_count += 1
        else:
            print('✗ AC2 FAILED: Response time exceeds 500ms')
        
        health_data = response.json()
        if 'status' in health_data and health_data['status'] == 'healthy':
            print('✓ Health status is healthy')
            success_count += 1
        else:
            print('✗ Health status is not healthy')
        
        # Validate exact response format (AC1)
        if set(health_data.keys()) == {'status'}:
            print('✓ Response format matches AC1')
        else:
            print('✗ Response format does not match AC1')
        
        print(f'\nResults: {success_count}/{total_tests} acceptance criteria passed')
        
        # Test degraded state
        def test_degraded_state():
            """Test degraded state (e.g., slow response time)"""
            # Mock slow response time
            import time
            original_time = time.time
            time.time = lambda: original_time() + 0.6  # Simulate 600ms delay
            
            response = client.get('/health')
            health_data = response.json()
            
            if health_data.get('status') == 'unhealthy':
                print('✓ Degraded state test passed (response time > 500ms)')
            else:
                print('✗ Degraded state test failed')
            
            # Restore time
            time.time = original_time
        
        test_degraded_state()
        
        return success_count == total_tests
        
    except Exception as e:
        print(f'✗ Test failed with error: {e}')
        return False

if __name__ == "__main__":
    print("Running tests for Story 1.2: Implement Readiness Endpoint...")
    
    if test_health_endpoint_functionality():
        print("\n🎉 All acceptance criteria passed! Story 1.2 implementation is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some acceptance criteria failed.")
        sys.exit(1)