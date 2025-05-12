#!/usr/bin/env python3
"""
Ali Programmatic Interaction Example

This script demonstrates how to interact with Ali programmatically,
accessing and controlling various features without using the standard
command-line interface.
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to the path so we can import the Ali modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Ali components
from src.ali import Ali
from src.ali_core.core import AliCore
from src.ali_core.persona import AliPersona
from src.ali_core.voice import AliVoice
from src.ali_core.intent import AliIntent
from src.ali_core.security import AliSecurity

def print_separator(title):
    """Print a section separator with title."""
    print("\n" + "="*70)
    print(f" {title} ".center(70, "-"))
    print("="*70 + "\n")

def main():
    """Main function demonstrating Ali programmatic interaction."""
    print_separator("Ali Programmatic Interaction Demo")
    
    print("Initializing Ali system...")
    # Create an Ali instance with a specific user ID
    ali = Ali(user_id="DemoUser")
    
    # Start the Ali system
    print("Starting Ali system...")
    ali.start()
    
    # Get system status
    print_separator("System Status")
    status = ali.get_system_status()
    print(json.dumps(status, indent=2))
    
    # Demonstrate text interaction
    print_separator("Text Interaction")
    
    # Process some example inputs
    example_inputs = [
        "Hello Ali, how are you today?",
        "What can you help me with?",
        "Remind me to check the project status tomorrow morning.",
        "Tell me about yourself."
    ]
    
    for input_text in example_inputs:
        print(f"\nUser: {input_text}")
        response = ali.process_text_input(input_text)
        print(f"Ali: {response['text']}")
        
        # Show additional information about the response
        if 'actions' in response and response['actions']:
            print(f"Actions: {response['actions']}")
        if 'style' in response:
            print(f"Response style: {response['style']}")
        if 'mood' in response:
            print(f"Current mood: {response['mood']}")
        
        time.sleep(1)  # Pause between interactions
    
    # Demonstrate persona manipulation
    print_separator("Persona Customization")
    
    # Get current persona state
    old_traits = ali.persona.personality_traits.copy()
    old_mood = ali.persona.mood
    print(f"Current personality traits: {json.dumps(old_traits, indent=2)}")
    print(f"Current mood: {old_mood}")
    
    # Modify persona traits
    print("\nModifying personality traits...")
    ali.persona.personality_traits["playfulness"] = 0.9
    ali.persona.personality_traits["assertiveness"] = 0.7
    ali.persona.mood = "enthusiastic"
    ali.persona.save_persona()
    
    print(f"New personality traits: {json.dumps(ali.persona.personality_traits, indent=2)}")
    print(f"New mood: {ali.persona.mood}")
    
    # Process same input with modified persona
    example_input = "What do you think about trying something new?"
    print(f"\nUser: {example_input}")
    response = ali.process_text_input(example_input)
    print(f"Ali: {response['text']}")
    print(f"Response style: {response['style']}")
    
    # Demonstrate voice configuration
    print_separator("Voice Configuration")
    
    # Get available voice profiles
    available_profiles = ali.voice.get_available_voice_profiles()
    print(f"Available voice profiles: {available_profiles}")
    
    # Get current voice profile details
    current_profile = ali.voice.get_voice_profile_details()
    print(f"\nCurrent voice profile: {json.dumps(current_profile, indent=2)}")
    
    # Create a custom voice profile
    print("\nCreating custom voice profile...")
    ali.voice.create_custom_voice_profile(
        "demo_voice",
        base_profile="goddess",
        adjustments={
            "pitch": 1.2,
            "speed": 0.9,
            "warmth": 0.8,
            "clarity": 0.95
        }
    )
    
    # Set the new profile as active
    ali.voice.set_voice_profile("demo_voice")
    print("Custom voice profile set as active")
    
    # Get updated profile details
    new_profile = ali.voice.get_voice_profile_details()
    print(f"\nNew voice profile: {json.dumps(new_profile, indent=2)}")
    
    # Demonstrate task management
    print_separator("Task Management")
    
    # Add some tasks
    print("Adding tasks to Ali's task queue...")
    
    # A reminder task for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_noon = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)
    
    ali.intent.add_task({
        "type": "reminder",
        "content": "Review project deliverables",
        "priority": "high",
        "scheduled_time": tomorrow_noon.isoformat()
    })
    
    # A recurring task
    ali.intent.add_recurring_task({
        "type": "system_task",
        "action": "cleanup_logs",
        "description": "Clean up old log files",
        "interval_hours": 24
    })
    
    # Get pending tasks
    tasks = ali.intent.get_pending_tasks()
    print(f"\nPending tasks: {json.dumps(tasks, indent=2)}")
    
    recurring = ali.intent.get_recurring_tasks()
    print(f"\nRecurring tasks: {json.dumps(recurring, indent=2)}")
    
    # Demonstrate security features
    print_separator("Security Functions")
    
    # Get current security level
    security_level = ali.security.security_level
    print(f"Current security level: {security_level}")
    
    # Change security level
    print("\nChanging security level...")
    ali.security.set_security_level("standard")
    print(f"New security level: {ali.security.security_level}")
    
    # Test user verification
    print("\nSimulating user verification...")
    auth_data = {
        "device_id": "demo_device_123",
        "ip_address": "192.168.1.100",
        "access_type": "standard",
        "password_hash": "demo_hash_123",
        "biometric_data": "demo_biometric_data"
    }
    
    verify_result = ali.verify_user(auth_data)
    print(f"Verification result: {json.dumps(verify_result, indent=2)}")
    
    # Encrypt some data
    print("\nEncrypting sensitive data...")
    sensitive_data = {
        "api_key": "sk_demo_12345abcdef",
        "user_info": {
            "name": "Demo User",
            "email": "demo@example.com"
        }
    }
    
    encrypted = ali.security.encrypt_data(sensitive_data)
    print(f"Encrypted data: {json.dumps(encrypted, indent=2)}")
    
    # Decrypt the data
    print("\nDecrypting data...")
    decrypted = ali.security.decrypt_data(encrypted)
    print(f"Decrypted data: {json.dumps(decrypted, indent=2)}")
    
    # System operations
    print_separator("System Operations")
    
    # Get system info
    system_info = ali.system.get_system_info()
    print(f"System info: {json.dumps(system_info, indent=2)}")
    
    # Create a backup
    print("\nCreating system backup...")
    backup_path = ali.create_backup()
    print(f"Backup created at: {backup_path}")
    
    # Get available backups
    backups = ali.system.get_available_backups()
    print(f"\nAvailable backups: {json.dumps(backups, indent=2)}")
    
    # Clean up and shutdown
    print_separator("Shutting Down")
    
    # Restore original personality traits before exiting
    print("Restoring original personality traits...")
    ali.persona.personality_traits = old_traits
    ali.persona.mood = old_mood
    ali.persona.save_persona()
    
    # Shutdown the Ali system
    print("Shutting down Ali system...")
    ali.shutdown()
    print("Ali system shutdown complete.")
    
    print_separator("Demo Complete")
    print("This demonstration showed how to programmatically interact with Ali,")
    print("accessing and controlling various components and features.")

if __name__ == "__main__":
    main()
