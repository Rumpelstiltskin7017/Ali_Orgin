"""
Tests for Ali Core Module
"""

import unittest
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add source directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ali_core.core import AliCore

class TestAliCore(unittest.TestCase):
    """Test cases for the AliCore class."""
    
    def setUp(self):
        """Set up test environment before each test case."""
        # Create a test directory for data
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)
        
        # Set up environment variable to point to test directory
        os.environ["ALI_DATA_DIR"] = str(self.test_dir)
        
        # Create an instance of AliCore with test user
        self.core = AliCore(user_id="TestUser")
    
    def tearDown(self):
        """Clean up after each test case."""
        # Remove test directory
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that AliCore initializes correctly."""
        self.assertEqual(self.core.user_id, "TestUser")
        self.assertEqual(self.core.emotional_state["baseline"], "neutral")
        self.assertTrue(hasattr(self.core, "startup_time"))
    
    def test_process_input(self):
        """Test that process_input handles text input."""
        # Test with a simple query
        response = self.core.process_input("What is the weather today?", "text")
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
    
    def test_start_stop(self):
        """Test starting and stopping the core."""
        # Start the core
        start_message = self.core.start()
        self.assertIsNotNone(start_message)
        self.assertIn("active", start_message.lower())
        
        # Stop the core
        self.core.shutdown()
        self.assertFalse(hasattr(self.core, "idle_thinking_thread") and 
                        self.core.idle_thinking_thread.is_alive())
    
    def test_emotional_state_update(self):
        """Test that emotional state updates correctly."""
        # Get initial state
        initial_state = self.core.emotional_state.copy()
        
        # Process an input that should change emotional state
        self.core.process_input("Thank you so much for your help!", "text")
        
        # Check that state changed
        self.assertNotEqual(self.core.emotional_state, initial_state)
    
    def test_memory_saving(self):
        """Test that memory entries are saved."""
        # Process a few inputs to generate memory entries
        self.core.process_input("Test input 1", "text")
        self.core.process_input("Test input 2", "text")
        
        # Check that memory directory was created
        memory_path = self.test_dir / "memory"
        self.assertTrue(memory_path.exists())
        
        # There should be at least one memory file
        memory_files = list(memory_path.glob("*.json"))
        self.assertTrue(len(memory_files) > 0)
        
        # Check content of a memory file
        with open(memory_files[0], 'r') as f:
            memories = json.load(f)
            self.assertTrue(isinstance(memories, list))
            self.assertTrue(len(memories) > 0)
            
            # Each memory should have standard fields
            for memory in memories:
                self.assertIn("timestamp", memory)
                self.assertIn("emotional_state", memory)

if __name__ == "__main__":
    unittest.main()
