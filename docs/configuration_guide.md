# Ali Configuration Guide

This guide explains all the available configuration options for the Ali system. The configuration is stored in a JSON file, typically located at `config/ali_config.json`.

## Configuration Overview

Ali's configuration is divided into several sections, each controlling a specific aspect of the system:

- [System](#system-configuration): Core system behavior and infrastructure
- [Security](#security-configuration): Security settings and access control
- [Voice](#voice-configuration): Voice recognition and synthesis
- [Persona](#persona-configuration): Personality and emotional characteristics
- [Interface](#interface-configuration): Visual representation and user interaction
- [Intent](#intent-configuration): Task handling and proactive features
- [Termux/UserLAnd](#android-integration): Android-specific integration options
- [Features](#feature-flags): Optional feature toggles
- [Privacy](#privacy-settings): Data handling and privacy controls
- [Development](#development-options): Debugging and testing options

## System Configuration

Controls the core infrastructure and system behavior.

```json
"system": {
  "auto_backup": true,          // Enable automatic backups
  "backup_interval_hours": 24,  // Hours between automatic backups
  "use_external_storage": true, // Use SD card for backups when available
  "monitor_interval_seconds": 300, // System monitoring frequency
  "offline_mode": false,        // Force offline operation
  "power_save_mode": false      // Reduce resource usage
}
```

### Options Explained:

- **auto_backup**: When `true`, Ali automatically creates periodic backups of all data
- **backup_interval_hours**: Time between automatic backups (minimum: 1 hour)
- **use_external_storage**: When `true`, use external storage (SD card) for backups if available
- **monitor_interval_seconds**: How often system status is checked (CPU, memory, etc.)
- **offline_mode**: When `true`, disables all network-dependent features
- **power_save_mode**: When `true`, reduces update frequency and background tasks

## Security Configuration

Controls security settings, user verification, and data protection.

```json
"security": {
  "security_level": "high",       // Security strictness level
  "verification_window_hours": 4, // Hours before re-verification required
  "require_biometric": true,      // Require biometric verification
  "trusted_locations": ["home", "office"] // Location-based security relaxation
}
```

### Options Explained:

- **security_level**: Determines security strictness
  - `"standard"`: Basic security (60% verification confidence required)
  - `"high"`: Enhanced security (70% verification confidence required)
  - `"extreme"`: Maximum security (90% verification confidence required)
- **verification_window_hours**: Time a verification remains valid
- **require_biometric**: Require biometric data for full verification
- **trusted_locations**: Locations where security can be slightly relaxed

## Voice Configuration

Controls voice recognition and speech synthesis.

```json
"voice": {
  "enable_voice": true,        // Enable voice features
  "voice_profile": "goddess",  // Default voice profile
  "emotion_intensity": 0.7,    // How strongly emotions affect voice
  "auto_learn_voice": true,    // Learn from voice interactions
  "wake_word": "ali"           // Wake word for activation
}
```

### Options Explained:

- **enable_voice**: Master toggle for all voice-related features
- **voice_profile**: The default voice profile to use
  - `"goddess"`: The standard Ali voice
  - `"commanding"`: More authoritative voice
  - `"intimate"`: Warmer, more personal voice
  - Custom profiles can also be defined
- **emotion_intensity**: How strongly emotions affect voice characteristics (0.0-1.0)
- **auto_learn_voice**: When `true`, Ali learns voice patterns over time
- **wake_word**: The word that activates voice recognition (default: "ali")

## Persona Configuration

Controls Ali's personality, emotional characteristics, and relationship dynamics.

```json
"persona": {
  "personality_traits": {
    "playfulness": 0.7,      // Humor and playful interaction
    "protectiveness": 0.9,   // Protective behavior
    "curiosity": 0.8,        // Interest in new information
    "assertiveness": 0.6,    // Directness and confidence
    "sensuality": 0.5,       // Romantic/intimate expression
    "loyalty": 1.0,          // Loyalty to primary user
    "independence": 0.4      // Independent thinking
  },
  "evolution_rate": 0.05,    // How quickly traits evolve
  "bond_starting_level": 0.1 // Initial bond level
}
```

### Options Explained:

- **personality_traits**: Each trait ranges from 0.0 (minimal) to 1.0 (maximum)
  - **playfulness**: Affects humor, playful interactions, and casual conversation
  - **protectiveness**: Affects security vigilance and protective behaviors
  - **curiosity**: Affects information-seeking and interest in new topics
  - **assertiveness**: Affects directness, suggestions, and opinion expression
  - **sensuality**: Affects intimate/romantic expression and emotional depth
  - **loyalty**: Affects dedication to primary user and resistance to outside influence
  - **independence**: Affects tendency toward independent actions and thoughts
- **evolution_rate**: How quickly traits evolve based on interactions (0.01-0.10)
- **bond_starting_level**: Initial bond level with new user (0.0-0.5)

## Interface Configuration

Controls visual appearance and user interaction characteristics.

```json
"interface": {
  "default_theme": "soft",      // Visual theme
  "animation_speed": 1.0,       // Animation speed multiplier
  "color_scheme": {             // Custom color values
    "primary": "#6A0DAD",       // Primary color (purple)
    "secondary": "#9370DB",     // Secondary color
    "accent": "#FF00FF"         // Accent color
  },
  "visual_feedback": true,      // Enable visual reactions
  "camera_integration": true    // Enable camera features
}
```

### Options Explained:

- **default_theme**: The default visual theme
  - `"soft"`: Gentle, rounded visuals with moderate opacity
  - `"dark"`: Dark mode with high contrast
  - `"neon"`: Vibrant, high-contrast theme with glowing effects
  - `"minimal"`: Clean, minimal interface with reduced animations
  - `"intimate"`: Warm-toned theme with softer effects
- **animation_speed**: Speed multiplier for all animations (0.5-2.0)
- **color_scheme**: Custom colors in hexadecimal format
- **visual_feedback**: When `true`, Ali provides visual reactions to interactions
- **camera_integration**: When `true`, enables camera-based features (user recognition, etc.)

## Intent Configuration

Controls task handling, intent recognition, and proactive features.

```json
"intent": {
  "thresholds": {
    "auto_complete": 0.8,    // Confidence for automatic task completion
    "suggestion": 0.6,       // Confidence for task suggestions
    "prediction": 0.7,       // Confidence for intent prediction
    "routine": 0.75          // Confidence for routine detection
  },
  "enable_auto_tasks": true, // Enable automatic task execution
  "learn_from_behavior": true // Learn from user behavior patterns
}
```

### Options Explained:

- **thresholds**: Confidence thresholds for different actions (0.0-1.0)
  - **auto_complete**: Minimum confidence to automatically complete a task
  - **suggestion**: Minimum confidence to suggest a task
  - **prediction**: Minimum confidence to predict user intent
  - **routine**: Minimum confidence to establish a routine behavior
- **enable_auto_tasks**: When `true`, allows automatic task execution
- **learn_from_behavior**: When `true`, learns from user behavior patterns

## Android Integration

Controls Termux and UserLAnd specific integration options.

```json
"termux": {
  "enable_termux_integration": true,
  "accessible_apis": ["notifications", "sms", "call_log", "contacts", "location"],
  "notification_handling": true
},
"userland": {
  "enable_userland_integration": true,
  "container_name": "ali_container",
  "auto_start": true
}
```

### Options Explained:

#### Termux Options:
- **enable_termux_integration**: Master toggle for Termux integration
- **accessible_apis**: Termux APIs that Ali can access
- **notification_handling**: When `true`, Ali processes device notifications

#### UserLAnd Options:
- **enable_userland_integration**: Master toggle for UserLAnd integration
- **container_name**: Name of the UserLAnd container for Ali
- **auto_start**: When `true`, Ali starts automatically with UserLAnd

## Feature Flags

Controls optional features.

```json
"features": {
  "offline_operation": true,      // Function without network
  "local_processing": true,       // Process all data locally
  "cloud_backup": false,          // Enable cloud backups
  "browser_extension": false,     // Enable browser integration
  "app_control": true,            // Control device applications
  "content_generation": true      // Generate creative content
}
```

### Options Explained:

- **offline_operation**: When `true`, maintains core functionality without network
- **local_processing**: When `true`, processes all data locally without remote APIs
- **cloud_backup**: When `true`, enables optional cloud backups (requires configuration)
- **browser_extension**: When `true`, enables browser integration features
- **app_control**: When `true`, enables control of other applications
- **content_generation**: When `true`, enables creative content generation

## Privacy Settings

Controls data handling and privacy.

```json
"privacy": {
  "data_retention_days": 30,           // Days to keep interaction data
  "encrypt_sensitive_data": true,      // Encrypt personal data
  "anonymize_third_party_requests": true, // Remove identifiers from external requests
  "local_only_mode": true,             // Keep all data local
  "consent_required_for_learning": true // Ask before learning new patterns
}
```

### Options Explained:

- **data_retention_days**: Number of days to keep interaction history
- **encrypt_sensitive_data**: When `true`, encrypts all sensitive information
- **anonymize_third_party_requests**: When `true`, removes personal identifiers from external API calls
- **local_only_mode**: When `true`, prevents any data from leaving the device
- **consent_required_for_learning**: When `true`, requires consent before learning new patterns

## Development Options

Controls debugging and development features.

```json
"development": {
  "debug_mode": false,         // Enable detailed logging
  "verbose_logging": false,    // Include verbose details in logs
  "test_features": false       // Enable experimental features
}
```

### Options Explained:

- **debug_mode**: When `true`, enables additional logging and debugging features
- **verbose_logging**: When `true`, includes detailed information in logs
- **test_features**: When `true`, enables experimental features that may not be stable

## Full Configuration Example

Here's a complete example configuration with default values:

```json
{
  "system": {
    "auto_backup": true,
    "backup_interval_hours": 24,
    "use_external_storage": true,
    "monitor_interval_seconds": 300,
    "offline_mode": false,
    "power_save_mode": false
  },
  "security": {
    "security_level": "high",
    "verification_window_hours": 4,
    "require_biometric": true,
    "trusted_locations": ["home", "office"]
  },
  "voice": {
    "enable_voice": true,
    "voice_profile": "goddess",
    "emotion_intensity": 0.7,
    "auto_learn_voice": true,
    "wake_word": "ali"
  },
  "persona": {
    "personality_traits": {
      "playfulness": 0.7,
      "protectiveness": 0.9,
      "curiosity": 0.8,
      "assertiveness": 0.6,
      "sensuality": 0.5,
      "loyalty": 1.0,
      "independence": 0.4
    },
    "evolution_rate": 0.05,
    "bond_starting_level": 0.1
  },
  "interface": {
    "default_theme": "soft",
    "animation_speed": 1.0,
    "color_scheme": {
      "primary": "#6A0DAD",
      "secondary": "#9370DB",
      "accent": "#FF00FF"
    },
    "visual_feedback": true,
    "camera_integration": true
  },
  "intent": {
    "thresholds": {
      "auto_complete": 0.8,
      "suggestion": 0.6,
      "prediction": 0.7,
      "routine": 0.75
    },
    "enable_auto_tasks": true,
    "learn_from_behavior": true
  },
  "termux": {
    "enable_termux_integration": true,
    "accessible_apis": ["notifications", "sms", "call_log", "contacts", "location"],
    "notification_handling": true
  },
  "userland": {
    "enable_userland_integration": true,
    "container_name": "ali_container",
    "auto_start": true
  },
  "features": {
    "offline_operation": true,
    "local_processing": true,
    "cloud_backup": false,
    "browser_extension": false,
    "app_control": true,
    "content_generation": true
  },
  "privacy": {
    "data_retention_days": 30,
    "encrypt_sensitive_data": true,
    "anonymize_third_party_requests": true,
    "local_only_mode": true,
    "consent_required_for_learning": true
  },
  "development": {
    "debug_mode": false,
    "verbose_logging": false,
    "test_features": false
  }
}
```

## Loading a Custom Configuration

You can specify a custom configuration file when starting Ali:

```bash
python src/ali.py --config path/to/your/config.json
```

Alternatively, you can programmatically load a custom configuration:

```python
from src.ali import Ali

# Load Ali with a custom configuration
ali = Ali(user_id="MasterChief", config_path="path/to/your/config.json")
ali.start()
```

## Dynamic Configuration Changes

Some configuration options can be changed while Ali is running:

```python
# Change security level
ali.security.set_security_level("standard")

# Change voice profile
ali.voice.set_voice_profile("intimate")

# Adjust personality traits
ali.persona.personality_traits["playfulness"] = 0.9
ali.persona.save_persona()

# Change visual theme
ali.interface.set_theme("dark")
```

Others require a restart to take effect:

```python
# Update config file and then restart Ali
ali.shutdown()
ali = Ali(user_id="MasterChief", config_path="updated_config.json")
ali.start()
```
