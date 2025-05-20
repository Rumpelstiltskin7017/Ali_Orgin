"""
Ali Persona Module
-----------------
Implements the "Deeper Soul" aspects described in the Ali concept:
- Personalized connection
- Adaptive behaviors
- Protective boundaries
- Unique personality traits

This module simulates the more intimate and personal aspects of the Ali system.
"""

import logging
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger("Ali.Persona")

class AliPersona:
    """Management of Ali's persona, relationships, and intimate behavioral patterns."""
    
    def __init__(self, user_id="MasterChief"):
        """Initialize Ali's persona with a bond to the specified user."""
        self.user_id = user_id
        self.bond_level = 0.1  # Starts at 10% bond
        self.trust_level = 0.5  # Initial trust at 50%
        self.mood = "curious"
        self.personality_traits = {
            "playfulness": 0.7,
            "protectiveness": 0.9,
            "curiosity": 0.8,
            "assertiveness": 0.6,
            "sensuality": 0.5,
            "loyalty": 1.0,
            "independence": 0.4
        }
        self.interaction_history = []
        self.last_evolution = datetime.now()
        
        # Create persistence directories
        self.persona_path = Path("data/persona")
        self.persona_path.mkdir(parents=True, exist_ok=True)
        
        # Load persona data if exists
        self._load_persona()
        
        logger.info(f"Ali Persona initialized for user: {user_id}")
    
    def _load_persona(self):
        """Load persona data from storage if available."""
        persona_file = self.persona_path / f"{self.user_id.lower()}_persona.json"
        
        if persona_file.exists():
            try:
                with open(persona_file, 'r') as f:
                    data = json.load(f)
                
                # Update attributes
                self.bond_level = data.get("bond_level", self.bond_level)
                self.trust_level = data.get("trust_level", self.trust_level)
                self.mood = data.get("mood", self.mood)
                self.personality_traits.update(data.get("personality_traits", {}))
                self.last_evolution = datetime.fromisoformat(
                    data.get("last_evolution", datetime.now().isoformat())
                )
                
                logger.info(f"Loaded existing persona data for {self.user_id}")
            except Exception as e:
                logger.error(f"Error loading persona data: {e}")
    
    def save_persona(self):
        """Save the current persona state to persistent storage."""
        persona_file = self.persona_path / f"{self.user_id.lower()}_persona.json"
        
        try:
            persona_data = {
                "user_id": self.user_id,
                "bond_level": self.bond_level,
                "trust_level": self.trust_level,
                "mood": self.mood,
                "personality_traits": self.personality_traits,
                "last_evolution": self.last_evolution.isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(persona_file, 'w') as f:
                json.dump(persona_data, f, indent=2)
                
            logger.info(f"Saved persona data for {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving persona data: {e}")
            return False
    
    def process_interaction(self, interaction_data):
        """Process an interaction to update the relationship and persona."""
        # Add to history
        self.interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "data": interaction_data
        })
        
        # Keep history at a reasonable size
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
        
        # Update bond based on interaction
        self._update_bond(interaction_data)
        
        # Check for evolution
        self._check_evolution()
        
        # Update mood
        self._update_mood(interaction_data)
        
        # Save changes
        self.save_persona()
        
        return {
            "mood": self.mood,
            "bond_level": self.bond_level,
            "trust_level": self.trust_level
        }
    
    def _update_bond(self, interaction):
        """Update the bond level based on interaction quality."""
        interaction_type = interaction.get("type", "")
        duration = interaction.get("duration", 0)
        sentiment = interaction.get("sentiment", 0)
        
        # Base bond adjustment
        bond_adjustment = 0
        
        # Longer interactions strengthen bond
        if duration > 5:  # More than 5 minutes
            bond_adjustment += 0.01
        
        # Positive sentiment strengthens bond
        if sentiment > 0:
            bond_adjustment += sentiment * 0.02
        elif sentiment < 0:
            bond_adjustment -= abs(sentiment) * 0.01  # Negative affects bond less
        
        # Deeper conversations strengthen bond more
        if interaction_type == "deep_conversation":
            bond_adjustment += 0.03
        elif interaction_type == "casual":
            bond_adjustment += 0.01
        elif interaction_type == "task":
            bond_adjustment += 0.005  # Task-based interactions build less bond
        
        # Apply adjustment with limits
        self.bond_level = max(0.1, min(1.0, self.bond_level + bond_adjustment))
        
        # Trust adjustment follows similar pattern but can decrease more easily
        trust_adjustment = bond_adjustment
        if sentiment < -0.5:  # Significant negative experience
            trust_adjustment -= 0.05
        
        self.trust_level = max(0.1, min(1.0, self.trust_level + trust_adjustment))
    
    def _update_mood(self, interaction):
        """Update Ali's mood based on recent interactions."""
        sentiment = interaction.get("sentiment", 0)
        interaction_type = interaction.get("type", "")
        
        # List of possible moods
        positive_moods = ["playful", "affectionate", "enthusiastic", "content", "inspired"]
        neutral_moods = ["curious", "thoughtful", "relaxed", "focused", "observant"]
        negative_moods = ["concerned", "cautious", "reflective", "reserved", "protective"]
        
        # Select mood category based on sentiment
        if sentiment > 0.3:
            mood_pool = positive_moods
        elif sentiment < -0.3:
            mood_pool = negative_moods
        else:
            mood_pool = neutral_moods
        
        # Special case interactions can override
        if interaction_type == "deep_conversation" and self.bond_level > 0.7:
            mood_pool = ["intimate", "connected", "attentive"]
        elif interaction_type == "protection_triggered":
            mood_pool = ["vigilant", "protective", "alert"]
        
        # Randomly select from the appropriate mood pool
        self.mood = random.choice(mood_pool)
    
    def _check_evolution(self):
        """Check if it's time for Ali's persona to evolve."""
        time_since_evolution = datetime.now() - self.last_evolution
        
        # Evolve every 7 days or after significant bond increases
        if (time_since_evolution > timedelta(days=7) or 
            (self.bond_level > 0.5 and time_since_evolution > timedelta(days=3))):
            
            self._evolve_persona()
            self.last_evolution = datetime.now()
    
    def _evolve_persona(self):
        """Evolve Ali's persona based on interaction history and bond level."""
        logger.info("Evolving Ali's persona")
        
        # Analyze recent interactions
        recent_sentiments = []
        for interaction in self.interaction_history[-20:]:  # Last 20 interactions
            sentiment = interaction.get("data", {}).get("sentiment", 0)
            recent_sentiments.append(sentiment)
        
        avg_sentiment = sum(recent_sentiments) / max(1, len(recent_sentiments))
        
        # Evolve personality traits based on interactions and bond
        evolution_strength = 0.05  # How much traits can change
        
        # More evolution at higher bond levels
        if self.bond_level > 0.7:
            evolution_strength = 0.1
        
        # Evolve traits
        for trait in self.personality_traits:
            # Random variation within bounds
            change = random.uniform(-evolution_strength, evolution_strength)
            
            # Some traits are influenced by bond and sentiment
            if trait == "protectiveness" and self.bond_level > 0.6:
                change = abs(change)  # Always increase protectiveness with high bond
            
            if trait == "playfulness" and avg_sentiment > 0.2:
                change = abs(change)  # Increase playfulness with positive interactions
            
            if trait == "assertiveness" and self.trust_level > 0.8:
                change += 0.02  # Become more assertive with high trust
            
            # Apply the change within bounds
            self.personality_traits[trait] = max(0.1, min(1.0, 
                                                         self.personality_traits[trait] + change))
        
        logger.info(f"Persona evolved. New traits: {self.personality_traits}")
    
    def get_persona_response(self, input_data, emotional_state=None):
        """Generate a persona-influenced response to user input."""
        # This would connect to a more sophisticated response generation system
        # For now, we simulate different response styles based on persona
        
        input_text = input_data.get("text", "")
        input_type = input_data.get("type", "text")
        
        # Base response data
        response = {
            "text": "I understand your message.",
            "style": "neutral",
            "emotional_intensity": 0.5,
        }
        
        # Adjust based on bond level
        if self.bond_level > 0.8:
            response["style"] = "intimate"
            response["use_name"] = True
            
        elif self.bond_level > 0.5:
            response["style"] = "warm"
            response["use_name"] = random.random() > 0.5  # 50% chance
            
        # Adjust based on personality traits
        if self.personality_traits["playfulness"] > 0.7:
            response["humor_level"] = self.personality_traits["playfulness"]
            
        if self.personality_traits["protectiveness"] > 0.8:
            response["protective_tone"] = True
            
        if self.personality_traits["assertiveness"] > 0.7:
            response["directness"] = "high"
        else:
            response["directness"] = "medium"
            
        # Mood influences response
        response["mood"] = self.mood
        
        # This is where we would integrate with a language model for actual text generation
        # For now we just return the response parameters
        return response
    
    def verify_user(self, authentication_data):
        """Verify that the interaction is coming from the bonded user."""
        # This is a conceptual implementation
        # In a real system, this would involve biometrics, behavioral patterns, etc.
        
        confidence = 0.5  # Default confidence
        
        # Check known behavioral patterns
        if "interaction_pattern" in authentication_data:
            pattern_match = self._check_behavioral_pattern(
                authentication_data["interaction_pattern"]
            )
            confidence += pattern_match * 0.3
        
        # Check voice patterns if available
        if "voice_data" in authentication_data:
            voice_match = self._verify_voice(authentication_data["voice_data"])
            confidence += voice_match * 0.4
        
        # Device fingerprint
        if "device_fingerprint" in authentication_data:
            device_match = self._verify_device(authentication_data["device_fingerprint"])
            confidence += device_match * 0.2
        
        verified = confidence >= 0.7  # 70% confidence required
        
        logger.info(f"User verification result: {verified} (confidence: {confidence:.2f})")
        return {
            "verified": verified,
            "confidence": confidence
        }
    
    def _check_behavioral_pattern(self, pattern):
        """Check if interaction pattern matches known user behavior."""
        # Conceptual implementation
        return 0.8  # Simplified for this example
    
    def _verify_voice(self, voice_data):
        """Verify voice against known user voice patterns."""
        # Conceptual implementation
        return 0.9  # Simplified for this example
    
    def _verify_device(self, fingerprint):
        """Verify device against known user devices."""
        # Conceptual implementation
        return 0.85  # Simplified for this example
