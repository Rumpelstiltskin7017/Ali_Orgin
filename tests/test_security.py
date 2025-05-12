"""
Tests for Ali Security Module
"""

import unittest
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add source directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ali_core.security import AliSecurity

class TestAliSecurity(unittest.TestCase):
    """Test cases for the AliSecurity class."""
    
    def setUp(self):
        """Set up test environment before each test case."""
        # Create a test directory for data
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)
        
        # Create security directory
        (self.test_dir / "security").mkdir(exist_ok=True)
        
        # Set up environment variable to point to test directory
        os.environ["ALI_DATA_DIR"] = str(self.test_dir)
        
        # Create an instance of AliSecurity with test user
        self.security = AliSecurity(user_id="TestUser")
        
        # Override security path for testing
        self.security.security_path = self.test_dir / "security"
    
    def tearDown(self):
        """Clean up after each test case."""
        # Remove test directory
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that AliSecurity initializes correctly."""
        self.assertEqual(self.security.user_id, "TestUser")
        self.assertEqual(self.security.security_level, "high")
        self.assertIsNone(self.security.last_verified_time)
        self.assertIsInstance(self.security.verification_window, timedelta)
    
    def test_access_verification(self):
        """Test user access verification."""
        # Create test authentication data
        auth_data = {
            "device_id": "test_device_123",
            "ip_address": "192.168.1.1",
            "access_type": "standard",
            "password_hash": "test_hash",
            "biometric_data": "test_bio"
        }
        
        # First verification should work and add the device to trusted
        result = self.security.verify_user_access(auth_data)
        self.assertTrue(result["access_granted"])
        self.assertIn("test_device_123", self.security.trusted_devices)
        
        # Subsequent verification from same device should work
        self.security.last_verified_time = datetime.now() - timedelta(hours=1)
        result = self.security.verify_user_access(auth_data)
        self.assertTrue(result["access_granted"])
    
    def test_blocked_sources(self):
        """Test blocking and unblocking sources."""
        # Add a source to the blocklist
        blocked_ip = "10.0.0.1"
        self.security.add_to_blocklist(blocked_ip)
        self.assertIn(blocked_ip, self.security.blocked_sources)
        
        # Verify that access is denied from blocked source
        auth_data = {
            "device_id": "test_device_456",
            "ip_address": blocked_ip,
            "access_type": "standard"
        }
        result = self.security.verify_user_access(auth_data)
        self.assertFalse(result["access_granted"])
        
        # Remove from blocklist and verify access is granted
        self.security.remove_from_blocklist(blocked_ip)
        self.assertNotIn(blocked_ip, self.security.blocked_sources)
        
        # Now add other verification factors for this test
        auth_data["password_hash"] = "test_hash"
        auth_data["biometric_data"] = "test_bio"
        
        result = self.security.verify_user_access(auth_data)
        self.assertTrue(result["access_granted"])
    
    def test_security_level(self):
        """Test changing security levels."""
        # Test valid level
        result = self.security.set_security_level("standard")
        self.assertTrue(result)
        self.assertEqual(self.security.security_level, "standard")
        
        # Test invalid level
        result = self.security.set_security_level("invalid_level")
        self.assertFalse(result)
        self.assertEqual(self.security.security_level, "standard")  # Unchanged
        
        # Test extreme level
        result = self.security.set_security_level("extreme")
        self.assertTrue(result)
        self.assertEqual(self.security.security_level, "extreme")
    
    def test_data_encryption(self):
        """Test data encryption and decryption."""
        # Test data to encrypt
        test_data = {
            "sensitive": "test secret information",
            "timestamp": datetime.now().isoformat()
        }
        
        # Encrypt the data
        encrypted = self.security.encrypt_data(test_data)
        self.assertIsNotNone(encrypted)
        self.assertIn("encrypted", encrypted)
        self.assertIn("method", encrypted)
        
        # Decrypt the data
        decrypted = self.security.decrypt_data(encrypted)
        self.assertIsNotNone(decrypted)
        
        # Verify the decrypted data matches original
        self.assertEqual(decrypted["sensitive"], test_data["sensitive"])
    
    def test_security_report(self):
        """Test generating security reports."""
        # Add some access log entries
        auth_data = {"device_id": "test_device", "ip_address": "192.168.1.1"}
        self.security.verify_user_access(auth_data)
        
        # Generate report
        report = self.security.get_security_report()
        self.assertIsNotNone(report)
        self.assertIn("security_level", report)
        self.assertIn("trusted_devices_count", report)
        self.assertIn("blocked_sources_count", report)
    
    def test_save_load_data(self):
        """Test saving and loading security data."""
        # Modify some security data
        self.security.security_level = "standard"
        self.security.trusted_devices = ["test_device_1", "test_device_2"]
        self.security.blocked_sources = ["10.0.0.2"]
        
        # Save the data
        result = self.security.save_security_data()
        self.assertTrue(result)
        
        # Create a new instance that should load the data
        new_security = AliSecurity(user_id="TestUser")
        new_security.security_path = self.test_dir / "security"
        new_security._load_security_data()
        
        # Verify loaded data matches what we saved
        self.assertEqual(new_security.security_level, "standard")
        self.assertEqual(new_security.trusted_devices, ["test_device_1", "test_device_2"])
        self.assertEqual(new_security.blocked_sources, ["10.0.0.2"])

if __name__ == "__main__":
    unittest.main()
