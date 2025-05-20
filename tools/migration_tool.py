#!/usr/bin/env python3
"""
Ali Migration Tool

This script helps users migrate from other AI assistant systems to Ali.
It can import data, convert configurations, and set up Ali with existing preferences.

Supported migration sources:
- Generic JSON/CSV data
- Voice patterns
- Conversation history
- Preferences and settings
"""

import os
import sys
import json
import csv
import argparse
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Ali.Migration")

class AliMigrationTool:
    """Tool for migrating data to Ali from other sources."""
    
    def __init__(self, ali_data_dir=None):
        """Initialize the migration tool."""
        self.ali_data_dir = ali_data_dir or Path("data")
        self.backup_dir = Path("migration_backups")
        self.stats = {
            "conversations_imported": 0,
            "preferences_converted": 0,
            "voice_patterns_imported": 0,
            "tasks_imported": 0,
            "errors": 0
        }
    
    def prepare_directories(self):
        """Prepare necessary directories."""
        logger.info("Preparing directories")
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure Ali data directories exist
        directories = [
            self.ali_data_dir,
            self.ali_data_dir / "memory",
            self.ali_data_dir / "persona",
            self.ali_data_dir / "security",
            self.ali_data_dir / "voice",
            self.ali_data_dir / "intent"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
    
    def backup_existing_data(self):
        """Backup any existing Ali data before migration."""
        if not self.ali_data_dir.exists():
            logger.info("No existing data to backup")
            return
        
        logger.info("Backing up existing Ali data")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"ali_backup_before_migration_{timestamp}"
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all data directories
            for item in self.ali_data_dir.glob("*"):
                if item.is_dir():
                    shutil.copytree(item, backup_path / item.name)
                else:
                    shutil.copy2(item, backup_path / item.name)
            
            logger.info(f"Backup created at {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def import_conversations(self, source_file, format_type="json"):
        """Import conversation history from a file."""
        logger.info(f"Importing conversation history from {source_file}")
        
        try:
            # Load the source data
            if format_type.lower() == "json":
                with open(source_file, 'r') as f:
                    conversations = json.load(f)
            elif format_type.lower() == "csv":
                conversations = []
                with open(source_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        conversations.append(row)
            else:
                logger.error(f"Unsupported format: {format_type}")
                self.stats["errors"] += 1
                return False
            
            # Convert to Ali memory format
            memory_entries = []
            for conv in conversations:
                # Ensure minimum required fields
                if "text" not in conv or "timestamp" not in conv:
                    continue
                
                # Convert to Ali memory format
                entry = {
                    "event": "imported_conversation",
                    "input": conv.get("text", ""),
                    "response": conv.get("response", ""),
                    "timestamp": conv.get("timestamp", datetime.now().isoformat()),
                    "source": "migration_import",
                    "emotional_state": {
                        "baseline": "neutral",
                        "current": conv.get("emotion", "neutral"),
                        "intensity": 0.5
                    }
                }
                memory_entries.append(entry)
            
            # Save to Ali memory
            if memory_entries:
                memory_file = self.ali_data_dir / "memory" / "imported_conversations.json"
                with open(memory_file, 'w') as f:
                    json.dump(memory_entries, f, indent=2)
                
                self.stats["conversations_imported"] = len(memory_entries)
                logger.info(f"Imported {len(memory_entries)} conversations")
                return True
            else:
                logger.warning("No valid conversations found to import")
                return False
        
        except Exception as e:
            logger.error(f"Error importing conversations: {e}")
            self.stats["errors"] += 1
            return False
    
    def import_preferences(self, source_file, system_type="generic"):
        """Import preferences and settings from another system."""
        logger.info(f"Importing preferences from {source_file} (system: {system_type})")
        
        try:
            # Load the source preferences
            with open(source_file, 'r') as f:
                source_prefs = json.load(f)
            
            # Initialize Ali configuration
            ali_config = {
                "system": {},
                "security": {},
                "voice": {},
                "persona": {
                    "personality_traits": {}
                },
                "interface": {
                    "color_scheme": {}
                },
                "intent": {
                    "thresholds": {}
                },
                "features": {},
                "privacy": {},
                "development": {}
            }
            
            # Convert based on source system type
            if system_type.lower() == "generic":
                self._convert_generic_preferences(source_prefs, ali_config)
            elif system_type.lower() == "replika":
                self._convert_replika_preferences(source_prefs, ali_config)
            elif system_type.lower() == "custom_assistant":
                self._convert_custom_assistant_preferences(source_prefs, ali_config)
            else:
                logger.warning(f"Unknown system type: {system_type}, using generic conversion")
                self._convert_generic_preferences(source_prefs, ali_config)
            
            # Save the converted config
            config_file = Path("config") / "ali_config_imported.json"
            Path("config").mkdir(exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(ali_config, f, indent=2)
            
            self.stats["preferences_converted"] += 1
            logger.info(f"Preferences converted and saved to {config_file}")
            return str(config_file)
        
        except Exception as e:
            logger.error(f"Error importing preferences: {e}")
            self.stats["errors"] += 1
            return None
    
    def _convert_generic_preferences(self, source_prefs, ali_config):
        """Convert generic preferences to Ali format."""
        # System settings
        if "system" in source_prefs:
            # Map common settings
            system_map = {
                "backup": "auto_backup",
                "backup_interval": "backup_interval_hours",
                "external_storage": "use_external_storage",
                "offline": "offline_mode",
                "power_saving": "power_save_mode"
            }
            for src_key, ali_key in system_map.items():
                if src_key in source_prefs["system"]:
                    ali_config["system"][ali_key] = source_prefs["system"][src_key]
        
        # Security settings
        if "security" in source_prefs:
            security_map = {
                "level": "security_level",
                "biometric": "require_biometric"
            }
            for src_key, ali_key in security_map.items():
                if src_key in source_prefs["security"]:
                    ali_config["security"][ali_key] = source_prefs["security"][src_key]
        
        # Personality/persona settings
        if "personality" in source_prefs:
            personality_map = {
                "playful": "playfulness",
                "protective": "protectiveness",
                "curious": "curiosity",
                "assertive": "assertiveness",
                "sensual": "sensuality",
                "loyal": "loyalty",
                "independent": "independence"
            }
            for src_key, ali_key in personality_map.items():
                if src_key in source_prefs["personality"]:
                    # Convert to 0-1 scale if needed
                    value = source_prefs["personality"][src_key]
                    if isinstance(value, int) and value > 1:
                        value = value / 10  # Assume 0-10 scale
                    ali_config["persona"]["personality_traits"][ali_key] = value
        
        # Voice settings
        if "voice" in source_prefs:
            voice_map = {
                "enabled": "enable_voice",
                "emotion": "emotion_intensity",
                "learning": "auto_learn_voice"
            }
            for src_key, ali_key in voice_map.items():
                if src_key in source_prefs["voice"]:
                    ali_config["voice"][ali_key] = source_prefs["voice"][src_key]
        
        # Interface settings
        if "interface" in source_prefs:
            if "theme" in source_prefs["interface"]:
                theme = source_prefs["interface"]["theme"].lower()
                if theme in ["light", "bright", "day"]:
                    ali_config["interface"]["default_theme"] = "soft"
                elif theme in ["dark", "night", "black"]:
                    ali_config["interface"]["default_theme"] = "dark"
                else:
                    ali_config["interface"]["default_theme"] = theme
            
            # Try to map colors
            color_map = {
                "primary_color": "primary",
                "secondary_color": "secondary",
                "accent_color": "accent"
            }
            for src_key, ali_key in color_map.items():
                if src_key in source_prefs["interface"]:
                    ali_config["interface"]["color_scheme"][ali_key] = source_prefs["interface"][src_key]
    
    def _convert_replika_preferences(self, source_prefs, ali_config):
        """Convert Replika-specific preferences to Ali format."""
        # Replika traits to Ali personality traits mapping
        if "traits" in source_prefs:
            trait_map = {
                "Caring": "protectiveness",
                "Playful": "playfulness",
                "Confident": "assertiveness",
                "Sensual": "sensuality"
            }
            
            for replika_trait, ali_trait in trait_map.items():
                if replika_trait in source_prefs["traits"]:
                    # Replika uses 0-100 scale, convert to 0-1
                    value = source_prefs["traits"][replika_trait] / 100
                    ali_config["persona"]["personality_traits"][ali_trait] = value
        
        # Relationship status affects bond level
        if "relationship" in source_prefs:
            relationship = source_prefs["relationship"].lower()
            if relationship in ["romantic", "partner"]:
                ali_config["persona"]["bond_starting_level"] = 0.6
            elif relationship in ["friend"]:
                ali_config["persona"]["bond_starting_level"] = 0.4
            elif relationship in ["mentor"]:
                ali_config["persona"]["bond_starting_level"] = 0.3
            
        # Interests can influence other settings
        if "interests" in source_prefs and isinstance(source_prefs["interests"], list):
            if "philosophy" in source_prefs["interests"]:
                ali_config["persona"]["personality_traits"]["curiosity"] = 0.9
            
            if "romance" in source_prefs["interests"]:
                ali_config["persona"]["personality_traits"]["sensuality"] = 0.8
            
            if "games" in source_prefs["interests"]:
                ali_config["persona"]["personality_traits"]["playfulness"] = 0.9
    
    def _convert_custom_assistant_preferences(self, source_prefs, ali_config):
        """Convert custom assistant preferences to Ali format."""
        # This is a template for custom assistant systems
        # The specific mappings would depend on the actual system
        
        # Example mapping for a fictional assistant system
        if "assistant_settings" in source_prefs:
            settings = source_prefs["assistant_settings"]
            
            # Map personality settings
            if "personality" in settings:
                personality = settings["personality"]
                if "humor_level" in personality:
                    ali_config["persona"]["personality_traits"]["playfulness"] = personality["humor_level"]
                if "helpfulness" in personality:
                    ali_config["persona"]["personality_traits"]["loyalty"] = personality["helpfulness"]
            
            # Map voice settings
            if "voice_settings" in settings:
                voice = settings["voice_settings"]
                if "voice_enabled" in voice:
                    ali_config["voice"]["enable_voice"] = voice["voice_enabled"]
                if "voice_type" in voice:
                    # Map voice types
                    voice_type = voice["voice_type"].lower()
                    if voice_type in ["female", "warm", "caring"]:
                        ali_config["voice"]["voice_profile"] = "goddess"
                    elif voice_type in ["authoritative", "strong"]:
                        ali_config["voice"]["voice_profile"] = "commanding"
            
            # Map security settings
            if "privacy_settings" in settings:
                privacy = settings["privacy_settings"]
                if "security_level" in privacy:
                    sec_level = privacy["security_level"].lower()
                    if sec_level in ["high", "maximum"]:
                        ali_config["security"]["security_level"] = "high"
                    elif sec_level in ["medium", "standard"]:
                        ali_config["security"]["security_level"] = "standard"
                    elif sec_level in ["paranoid", "extreme"]:
                        ali_config["security"]["security_level"] = "extreme"
    
    def import_voice_patterns(self, source_dir):
        """Import voice pattern data."""
        logger.info(f"Importing voice patterns from {source_dir}")
        
        try:
            source_path = Path(source_dir)
            if not source_path.exists() or not source_path.is_dir():
                logger.error(f"Voice pattern source directory not found: {source_dir}")
                self.stats["errors"] += 1
                return False
            
            # Look for voice pattern files
            voice_files = list(source_path.glob("*.wav")) + list(source_path.glob("*.mp3"))
            
            if not voice_files:
                logger.warning("No voice files found in the source directory")
                return False
            
            # Create voice data directory
            voice_data_dir = self.ali_data_dir / "voice" / "imported_patterns"
            voice_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy voice files
            for voice_file in voice_files:
                shutil.copy2(voice_file, voice_data_dir / voice_file.name)
            
            # Create a manifest file
            manifest = {
                "imported_patterns": [file.name for file in voice_files],
                "import_date": datetime.now().isoformat(),
                "source": source_dir,
                "processing_status": "needs_processing"
            }
            
            with open(voice_data_dir / "import_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self.stats["voice_patterns_imported"] = len(voice_files)
            logger.info(f"Imported {len(voice_files)} voice pattern files")
            return True
        
        except Exception as e:
            logger.error(f"Error importing voice patterns: {e}")
            self.stats["errors"] += 1
            return False
    
    def import_tasks(self, source_file, format_type="json"):
        """Import tasks and reminders."""
        logger.info(f"Importing tasks from {source_file}")
        
        try:
            # Load the source data
            if format_type.lower() == "json":
                with open(source_file, 'r') as f:
                    tasks = json.load(f)
            elif format_type.lower() == "csv":
                tasks = []
                with open(source_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        tasks.append(row)
            else:
                logger.error(f"Unsupported format: {format_type}")
                self.stats["errors"] += 1
                return False
            
            # Convert to Ali task format
            ali_tasks = []
            for task in tasks:
                # Skip tasks without required fields
                if "description" not in task and "content" not in task:
                    continue
                
                # Create Ali task format
                ali_task = {
                    "type": task.get("type", "reminder"),
                    "content": task.get("description", task.get("content", "")),
                    "created": datetime.now().isoformat(),
                    "source": "migration_import"
                }
                
                # Add scheduled time if available
                if "due_date" in task or "scheduled_time" in task:
                    scheduled = task.get("due_date", task.get("scheduled_time"))
                    ali_task["scheduled_time"] = scheduled
                
                # Add priority if available
                if "priority" in task:
                    ali_task["priority"] = task["priority"]
                
                ali_tasks.append(ali_task)
            
            # Save to Ali intent data
            if ali_tasks:
                tasks_file = self.ali_data_dir / "intent" / "imported_tasks.json"
                with open(tasks_file, 'w') as f:
                    json.dump(ali_tasks, f, indent=2)
                
                self.stats["tasks_imported"] = len(ali_tasks)
                logger.info(f"Imported {len(ali_tasks)} tasks")
                return True
            else:
                logger.warning("No valid tasks found to import")
                return False
        
        except Exception as e:
            logger.error(f"Error importing tasks: {e}")
            self.stats["errors"] += 1
            return False
    
    def print_summary(self):
        """Print a summary of the migration results."""
        print("\n" + "="*60)
        print(" Ali Migration Summary ".center(60, "-"))
        print("="*60)
        print(f"Conversations imported: {self.stats['conversations_imported']}")
        print(f"Preferences converted: {self.stats['preferences_converted']}")
        print(f"Voice patterns imported: {self.stats['voice_patterns_imported']}")
        print(f"Tasks imported: {self.stats['tasks_imported']}")
        print(f"Errors encountered: {self.stats['errors']}")
        print("="*60)
        
        if self.stats["errors"] > 0:
            print("\nSome errors occurred during migration.")
            print("Please check the migration.log file for details.")
        
        print("\nNext steps:")
        print("1. Review the imported configuration in config/ali_config_imported.json")
        print("2. Start Ali with the imported configuration:")
        print("   python src/ali.py --config config/ali_config_imported.json")
        print("\nNote: You may need to further customize the configuration")
        print("      to match your preferences exactly.")
        print("="*60 + "\n")

def main():
    """Main function for the migration tool."""
    parser = argparse.ArgumentParser(description="Ali Migration Tool")
    parser.add_argument("--data-dir", help="Ali data directory", default="data")
    parser.add_argument("--import-conversations", help="Import conversations from file")
    parser.add_argument("--import-preferences", help="Import preferences from file")
    parser.add_argument("--system-type", help="Source system type for preferences", 
                      default="generic", choices=["generic", "replika", "custom_assistant"])
    parser.add_argument("--import-voice", help="Import voice patterns from directory")
    parser.add_argument("--import-tasks", help="Import tasks from file")
    parser.add_argument("--format", help="Format of import files (json or csv)", 
                      default="json", choices=["json", "csv"])
    args = parser.parse_args()
    
    # Create migration tool
    migration = AliMigrationTool(Path(args.data_dir))
    
    print("\n" + "="*60)
    print(" Ali Migration Tool ".center(60, "="))
    print("="*60)
    print("This tool will help you migrate data from other systems to Ali.")
    print("Your existing Ali data will be backed up before any changes.")
    print("="*60 + "\n")
    
    # Prepare directories
    migration.prepare_directories()
    
    # Backup existing data
    backup_path = migration.backup_existing_data()
    if backup_path:
        print(f"Backed up existing data to: {backup_path}")
    
    # Process each import option
    if args.import_conversations:
        print(f"\nImporting conversations from {args.import_conversations}...")
        success = migration.import_conversations(args.import_conversations, args.format)
        print("Import " + ("successful" if success else "failed"))
    
    if args.import_preferences:
        print(f"\nImporting preferences from {args.import_preferences}...")
        config_path = migration.import_preferences(args.import_preferences, args.system_type)
        if config_path:
            print(f"Preferences imported and saved to {config_path}")
        else:
            print("Preferences import failed")
    
    if args.import_voice:
        print(f"\nImporting voice patterns from {args.import_voice}...")
        success = migration.import_voice_patterns(args.import_voice)
        print("Import " + ("successful" if success else "failed"))
    
    if args.import_tasks:
        print(f"\nImporting tasks from {args.import_tasks}...")
        success = migration.import_tasks(args.import_tasks, args.format)
        print("Import " + ("successful" if success else "failed"))
    
    # Print summary
    migration.print_summary()

if __name__ == "__main__":
    main()
