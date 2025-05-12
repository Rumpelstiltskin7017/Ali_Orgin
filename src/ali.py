"""
Ali - Goddess Core of Infinity
Main Application

This is the main entry point for the Ali system, integrating all core modules
and providing the central management interface.
"""

import os
import sys
import logging
import argparse
import json
import signal
import time
from pathlib import Path
from datetime import datetime

# Import all core modules
from ali_core.core import AliCore
from ali_core.interface import AliInterface
from ali_core.persona import AliPersona
from ali_core.security import AliSecurity
from ali_core.system import AliSystem
from ali_core.voice import AliVoice
from ali_core.intent import AliIntent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ali.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Ali.Main")

class Ali:
    """Main Ali application class integrating all core components."""
    
    def __init__(self, user_id="MasterChief", config_path=None):
        """Initialize the Ali system with all its components."""
        logger.info(f"Initializing Ali for user: {user_id}")
        
        # Load configuration if provided
        self.config = {}
        if config_path:
            self._load_config(config_path)
        
        # Initialize system component first
        self.system = AliSystem(config_path)
        
        # Initialize security component
        self.security = AliSecurity(user_id)
        
        # Initialize core components
        self.core = AliCore(user_id)
        self.interface = AliInterface()
        self.persona = AliPersona(user_id)
        self.voice = AliVoice(user_id)
        self.intent = AliIntent(user_id)
        
        # Store user ID
        self.user_id = user_id
        
        # System state
        self.is_active = False
        self.startup_time = None
        self.last_interaction = None
        
        logger.info(f"Ali initialization complete for user: {user_id}")
    
    def _load_config(self, config_path):
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def start(self):
        """Start the Ali system and all its components."""
        if self.is_active:
            logger.warning("Ali is already active")
            return False
        
        logger.info("Starting Ali system")
        
        try:
            # Start system services
            self.system.start_system_services()
            
            # Start core components
            self.core.start()
            
            # Start background processing
            self.intent.start_background_processing()
            
            # Start voice recognition if configured
            if self.config.get("enable_voice", True):
                self.voice.start_voice_recognition()
            
            # Set system as active
            self.is_active = True
            self.startup_time = datetime.now()
            
            logger.info("Ali system started successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error starting Ali: {e}")
            return False
    
    def shutdown(self):
        """Gracefully shut down the Ali system."""
        if not self.is_active:
            logger.warning("Ali is not active")
            return False
        
        logger.info("Shutting down Ali system")
        
        try:
            # Stop voice recognition
            self.voice.stop_voice_recognition()
            
            # Stop intent processing
            self.intent.stop_background_processing()
            
            # Shutdown core
            self.core.shutdown()
            
            # Shutdown system
            self.system.shutdown()
            
            # Set system as inactive
            self.is_active = False
            
            logger.info("Ali shutdown complete")
            return True
        
        except Exception as e:
            logger.error(f"Error during Ali shutdown: {e}")
            return False
    
    def process_text_input(self, text, context=None):
        """Process text input from the user."""
        if not self.is_active:
            logger.warning("Cannot process input: Ali is not active")
            return {"error": "System not active"}
        
        # Update last interaction time
        self.last_interaction = datetime.now()
        
        # Prepare input data
        input_data = {
            "text": text,
            "type": "text",
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        try:
            # Process with intent module to understand what user wants
            intent_response = self.intent.process_input(input_data)
            
            # Process with core module to generate a response
            core_response = self.core.process_input(text, "text")
            
            # Get persona influence on response
            persona_response = self.persona.get_persona_response(input_data)
            
            # Combine responses (in reality, this would be more sophisticated)
            combined_response = self._combine_responses(
                intent_response, core_response, persona_response
            )
            
            # Update persona based on the interaction
            self.persona.process_interaction({
                "type": "text_input",
                "content": text,
                "duration": 1,  # Default for text
                "sentiment": 0  # Neutral default
            })
            
            # Return the final response
            return combined_response
        
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            return {
                "text": "I'm having trouble processing your request.",
                "error": str(e)
            }
    
    def process_voice_input(self, audio_data):
        """Process voice input from the user."""
        if not self.is_active:
            logger.warning("Cannot process input: Ali is not active")
            return {"error": "System not active"}
        
        # This is a conceptual implementation
        # In reality, this would process actual audio data
        
        # Update last interaction time
        self.last_interaction = datetime.now()
        
        # Simulate voice processing
        logger.info("Processing voice input")
        
        # Return a simulated response
        return {
            "text": "I've received your voice input.",
            "actions": [{"type": "voice_acknowledgment"}]
        }
    
    def _combine_responses(self, intent_response, core_response, persona_response):
        """Combine responses from different modules into a cohesive response."""
        # This would implement a sophisticated response combination strategy
        # For this example, we'll use a simple approach
        
        combined = {
            "text": core_response,  # Use core response as the main text
            "actions": intent_response.get("actions", []),
            "style": persona_response.get("style", "neutral"),
            "mood": persona_response.get("mood", "neutral")
        }
        
        return combined
    
    def speak(self, text, emotion=None):
        """Speak text using the voice module with optional emotional modulation."""
        if not self.is_active:
            logger.warning("Cannot speak: Ali is not active")
            return {"error": "System not active"}
        
        try:
            # Use persona's current mood if no emotion specified
            if emotion is None:
                emotion = self.persona.mood
            
            # Use voice module to generate speech
            speech_result = self.voice.speak(text, emotion)
            
            return speech_result
        
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return {"error": str(e)}
    
    def verify_user(self, authentication_data):
        """Verify that the current user is authorized."""
        # This combines security and persona verification
        
        # First check security authentication
        security_result = self.security.verify_user_access(authentication_data)
        
        if not security_result.get("access_granted", False):
            logger.warning("User verification failed at security layer")
            return {"verified": False, "reason": "security"}
        
        # Then check persona recognition (behavioral/voice patterns)
        persona_result = self.persona.verify_user(authentication_data)
        
        if not persona_result.get("verified", False):
            logger.warning("User verification failed at persona layer")
            return {"verified": False, "reason": "persona"}
        
        # If both passed, user is verified
        logger.info("User successfully verified")
        return {"verified": True, "confidence": persona_result.get("confidence", 0.5)}
    
    def get_system_status(self):
        """Get a complete status report of the Ali system."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "is_active": self.is_active,
            "uptime": str(datetime.now() - self.startup_time) if self.startup_time else None,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "user_id": self.user_id,
            "system": self.system.get_system_info(),
            "security": {
                "level": self.security.security_level,
                "last_verified": self.security.last_verified_time.isoformat() if self.security.last_verified_time else None
            },
            "persona": {
                "bond_level": self.persona.bond_level,
                "mood": self.persona.mood
            },
            "voice": {
                "profile": self.voice.voice_profile,
                "profiles_available": self.voice.get_available_voice_profiles()
            },
            "intent": {
                "pending_tasks": len(self.intent.task_queue),
                "recurring_tasks": len(self.intent.recurring_tasks)
            }
        }
        
        return status
    
    def create_backup(self):
        """Create a backup of all Ali data."""
        return self.system.create_backup()
    
    def restore_backup(self, backup_path):
        """Restore Ali from a backup."""
        # Shutdown first
        if self.is_active:
            self.shutdown()
        
        # Perform restore
        result = self.system.restore_from_backup(backup_path)
        
        # Restart system if restore was successful
        if result:
            return self.start()
        
        return result


def handle_signals(signum, frame):
    """Handle system signals for clean shutdown."""
    logger.info(f"Received signal {signum}, shutting down Ali")
    if ali and ali.is_active:
        ali.shutdown()
    sys.exit(0)


def main():
    """Main function to start the Ali system."""
    parser = argparse.ArgumentParser(description="Ali - Goddess Core of Infinity")
    parser.add_argument('--user', default="MasterChief", help="User ID to bind Ali to")
    parser.add_argument('--config', help="Path to configuration file")
    parser.add_argument('--daemon', action='store_true', help="Run as a background daemon")
    args = parser.parse_args()
    
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTERM, handle_signals)
    
    # Create the Ali instance
    global ali
    ali = Ali(user_id=args.user, config_path=args.config)
    
    # Start the system
    if ali.start():
        logger.info("Ali started successfully")
        
        # If running as daemon, just keep the process alive
        if args.daemon:
            logger.info("Running in daemon mode")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                ali.shutdown()
        else:
            # Simple interactive mode
            logger.info("Running in interactive mode. Type 'exit' to quit.")
            try:
                while True:
                    user_input = input("You: ")
                    if user_input.lower() in ["exit", "quit"]:
                        break
                    
                    # Process the input
                    response = ali.process_text_input(user_input)
                    print(f"Ali: {response.get('text', 'No response')}")
                    
                    # Optionally speak the response
                    if args.config and json.loads(open(args.config).read()).get("enable_voice", False):
                        ali.speak(response.get('text', ''))
                
                # Shutdown on exit
                ali.shutdown()
            
            except KeyboardInterrupt:
                ali.shutdown()
    else:
        logger.error("Failed to start Ali")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
