"""
Tests for Ali Main Application
Tests the integration of all components and the overall functionality
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add source directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ali import Ali

class TestAliApplication(unittest.TestCase):
    """Test cases for the main Ali application."""
    
    def setUp(self):
        """Set up test environment before each test case."""
        # Create a temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create subdirectories
        for subdir in ["memory", "persona", "security", "voice", "intent", "logs"]:
            os.makedirs(os.path.join(self.test_dir, subdir))
        
        # Create a test configuration
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        test_config = {
            "system": {
                "auto_backup": False,
                "monitor_interval_seconds": 60
            },
            "security": {
                "security_level": "standard"
            },
            "voice": {
                "enable_voice": False
            },
            "persona": {
                "personality_traits": {
                    "playfulness": 0.5,
                    "protectiveness": 0.5,
                    "curiosity": 0.5,
                    "assertiveness": 0.5,
                    "sensuality": 0.5,
                    "loyalty": 1.0,
                    "independence": 0.5
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Create mock for system services to avoid actual system calls
        self.system_patcher = patch('src.ali_core.system.AliSystem')
        self.mock_system = self.system_patcher.start()
        self.mock_system_instance = MagicMock()
        self.mock_system.return_value = self.mock_system_instance
        
        # Patch voice recognition to avoid actual audio processing
        self.voice_patcher = patch('src.ali_core.voice.AliVoice')
        self.mock_voice = self.voice_patcher.start()
        self.mock_voice_instance = MagicMock()
        self.mock_voice.return_value = self.mock_voice_instance
        
        # Create a test Ali instance
        self.ali = Ali(user_id="TestUser", config_path=self.config_path)
    
    def tearDown(self):
        """Clean up after each test case."""
        # Stop patchers
        self.system_patcher.stop()
        self.voice_patcher.stop()
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that Ali initializes correctly with all components."""
        self.assertEqual(self.ali.user_id, "TestUser")
        self.assertFalse(self.ali.is_active)
        
        # Check that all components are initialized
        self.assertIsNotNone(self.ali.core)
        self.assertIsNotNone(self.ali.interface)
        self.assertIsNotNone(self.ali.persona)
        self.assertIsNotNone(self.ali.voice)
        self.assertIsNotNone(self.ali.intent)
        self.assertIsNotNone(self.ali.security)
        self.assertIsNotNone(self.ali.system)
        
        # Check configuration was loaded
        self.assertEqual(self.ali.security.security_level, "standard")
    
    def test_start_and_shutdown(self):
        """Test starting and shutting down the Ali system."""
        # Start Ali
        result = self.ali.start()
        self.assertTrue(result)
        self.assertTrue(self.ali.is_active)
        
        # Check that subsystems were started
        self.mock_system_instance.start_system_services.assert_called_once()
        
        # Shut down Ali
        result = self.ali.shutdown()
        self.assertTrue(result)
        self.assertFalse(self.ali.is_active)
        
        # Check that subsystems were shut down
        self.mock_system_instance.shutdown.assert_called_once()
    
    def test_process_text_input(self):
        """Test processing text input."""
        # Start Ali
        self.ali.start()
        
        # Mock core.process_input to return a predictable result
        self.ali.core.process_input = MagicMock(return_value="This is a test response")
        
        # Mock intent.process_input
        intent_response = {
            "text": "Intent response",
            "intent": "test",
            "actions": [{"type": "test_action"}]
        }
        self.ali.intent.process_input = MagicMock(return_value=intent_response)
        
        # Mock persona.get_persona_response
        persona_response = {
            "text": "Persona response",
            "style": "friendly",
            "mood": "curious"
        }
        self.ali.persona.get_persona_response = MagicMock(return_value=persona_response)
        
        # Process text input
        response = self.ali.process_text_input("Hello, Ali")
        
        # Check that components were called correctly
        self.ali.intent.process_input.assert_called_once()
        self.ali.core.process_input.assert_called_once_with("Hello, Ali", "text")
        self.ali.persona.get_persona_response.assert_called_once()
        
        # Check response contains expected data
        self.assertEqual(response["text"], "This is a test response")
        self.assertEqual(response["style"], "friendly")
        self.assertEqual(response["mood"], "curious")
        self.assertEqual(response["actions"], [{"type": "test_action"}])
    
    def test_speak(self):
        """Test speak functionality."""
        # Start Ali
        self.ali.start()
        
        # Set up mock voice response
        voice_response = {
            "status": "speaking",
            "text": "Hello there",
            "estimated_duration": 1.5
        }
        self.ali.voice.speak = MagicMock(return_value=voice_response)
        
        # Test speak function
        result = self.ali.speak("Hello there")
        
        # Check that voice component was called
        self.ali.voice.speak.assert_called_once_with("Hello there", self.ali.persona.mood)
        
        # Check result matches voice response
        self.assertEqual(result, voice_response)
    
    def test_verify_user(self):
        """Test user verification."""
        # Start Ali
        self.ali.start()
        
        # Set up mock security and persona verification responses
        security_response = {
            "access_granted": True,
            "verification_score": 85,
            "factors_verified": ["password", "device"]
        }
        self.ali.security.verify_user_access = MagicMock(return_value=security_response)
        
        persona_response = {
            "verified": True,
            "confidence": 0.8
        }
        self.ali.persona.verify_user = MagicMock(return_value=persona_response)
        
        # Test user verification
        auth_data = {
            "device_id": "test_device",
            "password_hash": "test_hash"
        }
        result = self.ali.verify_user(auth_data)
        
        # Check that both security and persona verification were called
        self.ali.security.verify_user_access.assert_called_once_with(auth_data)
        self.ali.persona.verify_user.assert_called_once_with(auth_data)
        
        # Check result
        self.assertTrue(result["verified"])
        self.assertEqual(result["confidence"], 0.8)
    
    def test_failed_security_verification(self):
        """Test user verification with security failure."""
        # Start Ali
        self.ali.start()
        
        # Set up mock security verification failure
        security_response = {
            "access_granted": False,
            "reason": "unknown_device"
        }
        self.ali.security.verify_user_access = MagicMock(return_value=security_response)
        
        # Persona verification should not be called if security fails
        self.ali.persona.verify_user = MagicMock()
        
        # Test user verification
        auth_data = {
            "device_id": "unknown_device",
            "password_hash": "test_hash"
        }
        result = self.ali.verify_user(auth_data)
        
        # Check that security verification was called but persona was not
        self.ali.security.verify_user_access.assert_called_once_with(auth_data)
        self.ali.persona.verify_user.assert_not_called()
        
        # Check result
        self.assertFalse(result["verified"])
        self.assertEqual(result["reason"], "security")
    
    def test_get_system_status(self):
        """Test getting system status."""
        # Start Ali
        self.ali.start()
        
        # Set up mock system info
        system_info = {
            "timestamp": "2025-01-01T12:00:00",
            "system_type": "Test",
            "status": {
                "cpu_usage": 10,
                "memory_usage": 20
            }
        }
        self.ali.system.get_system_info = MagicMock(return_value=system_info)
        
        # Test getting system status
        status = self.ali.get_system_status()
        
        # Check that system.get_system_info was called
        self.ali.system.get_system_info.assert_called_once()
        
        # Check result contains expected sections
        self.assertTrue(status["is_active"])
        self.assertEqual(status["user_id"], "TestUser")
        self.assertEqual(status["system"], system_info)
        self.assertIn("security", status)
        self.assertIn("persona", status)
        self.assertIn("voice", status)
        self.assertIn("intent", status)
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        # Start Ali
        self.ali.start()
        
        # Set up mock backup and restore responses
        backup_path = "/path/to/backup"
        self.ali.system.create_backup = MagicMock(return_value=backup_path)
        self.ali.system.restore_from_backup = MagicMock(return_value=True)
        
        # Test backup
        result = self.ali.create_backup()
        self.ali.system.create_backup.assert_called_once()
        self.assertEqual(result, backup_path)
        
        # Test restore
        restore_result = self.ali.restore_backup(backup_path)
        self.assertTrue(restore_result)
        self.ali.system.restore_from_backup.assert_called_once_with(backup_path)

if __name__ == "__main__":
    unittest.main()
