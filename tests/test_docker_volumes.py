#!/usr/bin/env python3
"""
Test for Docker volume configuration (Story 1.3)
"""

import sys
import os
from pathlib import Path

def test_dockerfile_volumes():
    """Test that Dockerfile has proper volume setup"""
    try:
        dockerfile_path = Path(__file__).parent.parent / 'Dockerfile'
        
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Check for volume directory creation
        if 'mkdir -p /data /downloads /config' in content:
            print('✓ Dockerfile creates required volume directories')
        else:
            print('✗ Dockerfile missing volume directory creation')
            return False
        
        # Check for proper CMD with module path
        if 'mtv_dl_web.main:app' in content:
            print('✓ Dockerfile uses correct module path')
        else:
            print('✗ Dockerfile has incorrect module path')
            return False
        
        # Check for proper user permissions
        if 'chown -R appuser:appuser /data /downloads /config' in content:
            print('✓ Dockerfile sets proper permissions for volumes')
        else:
            print('✗ Dockerfile missing volume permissions')
            return False
        
        return True
    except Exception as e:
        print(f'✗ Dockerfile test failed: {e}')
        return False

def test_docker_compose_volumes():
    """Test that docker-compose.yml has proper volume configuration"""
    try:
        compose_path = Path(__file__).parent.parent / 'docker-compose.yml'
        
        if not compose_path.exists():
            print('✗ docker-compose.yml file not found')
            return False
        
        with open(compose_path, 'r') as f:
            content = f.read()
        
        # Check for volume definitions
        required_volumes = ['/data', '/downloads', '/config', '/home/appuser/.mtv_dl_web']
        volume_count = 0
        
        for volume in required_volumes:
            if volume in content:
                volume_count += 1
                print(f'✓ Found {volume} volume mount')
        
        if volume_count == len(required_volumes):
            print('✓ All required volumes are configured')
        else:
            print(f'✗ Missing volume configurations (found {volume_count}/{len(required_volumes)})')
            return False
        
        # Check for proper service configuration
        if 'mtv_dl_web:' in content and 'ports:' in content and '8000:8000' in content:
            print('✓ Service configuration is proper')
        else:
            print('✗ Service configuration issues')
            return False
        
        return True
    except Exception as e:
        print(f'✗ docker-compose.yml test failed: {e}')
        return False

def test_volume_paths_architecture():
    """Test that volume paths match architecture requirements"""
    try:
        compose_path = Path(__file__).parent.parent / 'docker-compose.yml'
        
        with open(compose_path, 'r') as f:
            content = f.read()
        
        # Check for architecture-required database path
        if '/home/appuser/.mtv_dl_web' in content:
            print('✓ Database volume path matches architecture (.mtv_dl_web)')
        else:
            print('✗ Database volume path does not match architecture')
            return False
        
        # Check for standard volume paths
        if '/data' in content and '/downloads' in content and '/config' in content:
            print('✓ Standard volume paths are configured')
        else:
            print('✗ Missing standard volume paths')
            return False
        
        return True
    except Exception as e:
        print(f'✗ Architecture compliance test failed: {e}')
        return False

if __name__ == "__main__":
    print("Running tests for Story 1.3: Configure Mounted Volumes (Docker)...")
    
    success_count = 0
    total_tests = 3
    
    if test_dockerfile_volumes():
        success_count += 1
        
    if test_docker_compose_volumes():
        success_count += 1
        
    if test_volume_paths_architecture():
        success_count += 1
    
    print(f'\nResults: {success_count}/{total_tests} tests passed')
    
    if success_count == total_tests:
        print('🎉 All Docker volume configuration tests passed!')
        sys.exit(0)
    else:
        print('❌ Some Docker configuration tests failed.')
        sys.exit(1)