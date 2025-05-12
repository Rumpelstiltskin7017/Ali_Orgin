"""
Tests for Ali Persona Module
"""

import unittest
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add source directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ali_core.persona import AliPersona

class TestAliPersona(unittest.TestCase):
    """Test cases for the AliPersona class."""
    
    def setUp(self):
        """Set up test environment before each test case."""
        # Create a test directory for data
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)
        
        # Create persona directory
        (self.test_dir / "persona").mkdir(exist_ok=True)
        
        # Set up environment variable to point to test directory
        os.environ["ALI_DATA_DIR"] = str(self.test_dir)
        
        # Create an instance of AliPersona with test user
        self.persona = AliPersona(user_id="TestUser")
        
        # Override persona path for testing
        self.persona.persona_path = self.test_dir / "persona"
    
    def tearDown(self):
        """Clean up after each test case."""
        # Remove test directory
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test that AliPersona initializes correctly."""
        self.assertEqual(self.persona.user_id, "TestUser")
        self.assertIsInstance(self.persona.bond_level, float)
        self.assertIsInstance(self.persona.trust_level, float)
        self.assertIsInstance(self.persona.personality_traits, dict)
        self.assertGreater(len(self.persona.personality_traits), 0)
    
    def test_process_interaction(self):
        """Test processing interactions and updating bond."""
        # Initial bond and trust levels
        initial_bond = self.persona.bond_level
        initial_trust = self.persona.trust_level
        
        # Process a positive interaction
        interaction_data = {
            "type": "deep_conversation",
            "duration": 10,
            "sentiment": 0.7
        }
        result = self.persona.process_interaction(interaction_data)
        
        # Bond and trust should increase
        self.assertGreater(self.persona.bond_level, initial_bond)
        self.assertGreater(self.persona.trust_level, initial_trust)
        
        # Result should include current mood and bond
        self.assertIn("mood", result)
        self.assertIn("bond_level", result)
        self.assertIn("trust_level", result)
    
    def test_negative_interaction(self):
        """Test processing negative interactions."""
        # Initial trust level
        initial_trust = self.persona.trust_level
        
        # Process a negative interaction
        interaction_data = {
            "type": "disagreement",
            "duration": 5,
            "sentiment": -0.6
        }
        self.persona.process_interaction(interaction_data)
        
        # Trust should decrease
        self.assertLess(self.persona.trust_level, initial_trust)
    
    def test_mood_updates(self):
        """Test mood updates based on interactions."""
        # Process interactions to influence mood
        happy_interaction = {
            "type": "casual",
            "sentiment": 0.8,
            "duration": 3
        }
        self.persona.process_interaction(happy_interaction)
        
        # Record the mood after happy interaction
        happy_mood = self.persona.mood
        
        # Process a negative interaction
        negative_interaction = {
            "type": "task",
            "sentiment": -0.5,
            "duration": 2
        }
        self.persona.process_interaction(negative_interaction)
        
        # Mood should have changed
        self.assertNotEqual(self.persona.mood, happy_mood)
    
    def test_personality_evolution(self):
        """Test personality trait evolution."""
        # Save initial personality traits
        initial_traits = self.persona.personality_traits.copy()
        
        # Set a last evolution time far in the past to force evolution
        self.persona.last_evolution = datetime.now() - timedelta(days=8)
        
        # Process several interactions to trigger personality evolution
        for _ in range(5):
            interaction_data = {
                "type": "deep_conversation",
                "duration": 15,
                "sentiment": 0.6
            }
            self.persona.process_interaction(interaction_data)
        
        # Force evolution by calling it directly
        self.persona._evolve_persona()
        
        # At least some traits should have changed
        traits_changed = False
        for trait, value in self.persona.personality_traits.items():
            if abs(value - initial_traits[trait]) > 0.001:
                traits_changed = True
                break
        
        self.assertTrue(traits_changed)
    
    def test_persona_response(self):
        """Test persona-influenced response generation."""
        input_data = {
            "text": "How are you feeling today?",
            "type": "text"
        }
        
        # Get response with default bond level
        response = self.persona.get_persona_response(input_data)
        self.assertIsInstance(response, dict)
        self.assertIn("style", response)
        
        # Increase bond level and check if response style changes
        self.persona.bond_level = 0.9  # Very high bond
        high_bond_response = self.persona.get_persona_response(input_data)
        
        # Response style should be different with high bond
        self.assertNotEqual(response["style"], high_bond_response["style"])
    
    def test_user_verification(self):
        """Test user verification functionality."""
        # Create authentication data
        auth_data = {
            "interaction_pattern": "test_pattern",
            "voice_data": "test_voice",
            "device_fingerprint": "test_device"
        }
        
        # Verify user
        result = self.persona.verify_user(auth_data)
        self.assertIsInstance(result, dict)
        self.assertIn("verified", result)
        self.assertIn("confidence", result)
    
    def test_save_load_persona(self):
        """Test saving and loading persona data."""
        # Modify persona data
        self.persona.bond_level = 0.75
        self.persona.trust_level = 0.8
        self.persona.mood = "enthusiastic"
        self.persona.personality_traits["playfulness"] = 0.9
        
        # Save persona data
        result = self.persona.save_persona()
        self.assertTrue(result)
        
        # Create a new persona instance that should load the saved data
        new_persona = AliPersona(user_id="TestUser")
        new_persona.persona_path = self.test_dir / "persona"
        new_persona._load_persona()
        
        # Check that data was loaded correctly
        self.assertEqual(new_persona.bond_level, 0.75)
        self.assertEqual(new_persona.trust_level, 0.8)
        self.assertEqual(new_persona.mood, "enthusiastic")
        self.assertEqual(new_persona.personality_traits["playfulness"], 0.9)

if __name__ == "__main__":
    unittest.main()
