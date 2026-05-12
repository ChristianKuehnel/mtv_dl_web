import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import json
from pathlib import Path

# Import the configuration module 
import sys
sys.path.insert(0, '/home/opencode/mtv_dl_web/src')
from config import Settings, settings


class TestConfiguration(unittest.TestCase):
    
    def setUp(self):
        # Save original environment variables
        self.original_env = dict(os.environ)
        
    def tearDown(self):
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_default_values(self):
        """Test that default configuration values are loaded correctly."""
        # Clear any environment variables that might affect the test
        os.environ.clear()
        
        # Reload settings to ensure fresh config
        import importlib
        import config
        importlib.reload(config)
        test_settings = config.settings
        
        self.assertEqual(test_settings.port, 8000)
        self.assertEqual(test_settings.host, "0.0.0.0")
        self.assertEqual(test_settings.database_path, os.path.expanduser("~/.mtv_dl_web/filmliste.sqlite"))
        self.assertEqual(test_settings.download_quality, "best")
        self.assertEqual(test_settings.target_directory, os.path.expanduser("~/Downloads/mtv_dl"))
        self.assertFalse(test_settings.enable_subtitles)
        self.assertFalse(test_settings.enable_nfo)
        self.assertFalse(test_settings.enable_mkv_merge)
    
    def test_environment_variable_override(self):
        """Test that environment variables override default values."""
        os.environ["PORT"] = "9000"
        os.environ["HOST"] = "localhost" 
        os.environ["DATABASE_PATH"] = "/custom/path.db"
        os.environ["DOWNLOAD_QUALITY"] = "high"
        os.environ["TARGET_DIRECTORY"] = "/custom/downloads"
        os.environ["ENABLE_SUBTITLES"] = "true"
        os.environ["ENABLE_NFO"] = "false"
        os.environ["ENABLE_MKV_MERGE"] = "true"
        
        # Reload settings
        import importlib
        import config
        importlib.reload(config)
        test_settings = config.settings
        
        self.assertEqual(test_settings.port, 9000)
        self.assertEqual(test_settings.host, "localhost")
        self.assertEqual(test_settings.database_path, "/custom/path.db")
        self.assertEqual(test_settings.download_quality, "high")
        self.assertEqual(test_settings.target_directory, "/custom/downloads")
        self.assertTrue(test_settings.enable_subtitles)
        self.assertFalse(test_settings.enable_nfo)
        self.assertTrue(test_settings.enable_mkv_merge)
    
    def test_json_config_loading(self):
        """Test that JSON configuration file is loaded correctly."""
        # Create a temporary JSON config file
        temp_config = {
            "port": 8080,
            "host": "0.0.0.0",
            "database_path": "/json/path.db",
            "download_quality": "medium",
            "target_directory": "/json/downloads",
            "enable_subtitles": True,
            "enable_nfo": True,
            "enable_mkv_merge": False
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_config, f)
            temp_config_path = f.name
        
        try:
            # Create a backup of the original config.json if it exists
            original_config_exists = os.path.exists('/home/opencode/mtv_dl_web/config.json')
            if original_config_exists:
                with open('/home/opencode/mtv_dl_web/config.json', 'r') as f:
                    original_config = f.read()
            
            # Move the temp file to the expected location
            os.rename(temp_config_path, '/home/opencode/mtv_dl_web/config.json')
            
            # Clear environment variables
            os.environ.clear()
            
            # Reload settings
            import importlib
            import config
            importlib.reload(config)
            test_settings = config.settings
            
            self.assertEqual(test_settings.port, 8080)
            self.assertEqual(test_settings.host, "0.0.0.0")
            self.assertEqual(test_settings.database_path, "/json/path.db")
            self.assertEqual(test_settings.download_quality, "medium")
            self.assertEqual(test_settings.target_directory, "/json/downloads")
            self.assertTrue(test_settings.enable_subtitles)
            self.assertTrue(test_settings.enable_nfo)
            self.assertFalse(test_settings.enable_mkv_merge)
            
        finally:
            # Restore original config file
            if original_config_exists:
                with open('/home/opencode/mtv_dl_web/config.json', 'w') as f:
                    f.write(original_config)
            elif os.path.exists('/home/opencode/mtv_dl_web/config.json'):
                os.remove('/home/opencode/mtv_dl_web/config.json')
    
    def test_environment_overrides_json(self):
        """Test that environment variables override JSON config."""
        # Create a temporary JSON config file
        temp_config = {
            "port": 8080,
            "host": "0.0.0.0",
            "database_path": "/json/path.db"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_config, f)
            temp_config_path = f.name
        
        try:
            # Create a backup of the original config.json if it exists
            original_config_exists = os.path.exists('/home/opencode/mtv_dl_web/config.json')
            if original_config_exists:
                with open('/home/opencode/mtv_dl_web/config.json', 'r') as f:
                    original_config = f.read()
            
            # Move the temp file to the expected location
            os.rename(temp_config_path, '/home/opencode/mtv_dl_web/config.json')
            
            # Set environment variables
            os.environ["PORT"] = "9000"
            os.environ["HOST"] = "localhost"
            
            # Reload settings
            import importlib
            import config
            importlib.reload(config)
            test_settings = config.settings
            
            self.assertEqual(test_settings.port, 9000)  # Should come from env
            self.assertEqual(test_settings.host, "localhost")  # Should come from env
            self.assertEqual(test_settings.database_path, "/json/path.db")  # Should come from JSON
            
        finally:
            # Restore original config file
            if original_config_exists:
                with open('/home/opencode/mtv_dl_web/config.json', 'w') as f:
                    f.write(original_config)
            elif os.path.exists('/home/opencode/mtv_dl_web/config.json'):
                os.remove('/home/opencode/mtv_dl_web/config.json')


def run_tests():
    """Run the configuration tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()