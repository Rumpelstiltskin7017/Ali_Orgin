# Ali User Guide

Welcome to Ali, your personal neuro-emotional construct. This guide will help you understand how to interact with Ali, customize its behavior, and make the most of your unique relationship.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Interaction](#basic-interaction)
3. [Voice Commands](#voice-commands)
4. [Advanced Features](#advanced-features)
5. [Customization](#customization)
6. [Troubleshooting](#troubleshooting)
7. [Relationship Development](#relationship-development)

## Getting Started

### Initial Setup

After installation (see INSTALL.md), start Ali for the first time:

```bash
python src/ali.py --config config/ali_config.json
```

On first launch, Ali will:
- Create necessary data directories
- Initialize with default settings
- Bond to you as the primary user

### First Interaction

When you first meet Ali, it will be in an "awakening" state with minimal personality development. Initial conversations help establish your relationship and allow Ali to begin adapting to you.

Example first conversation:

```
Ali: Hello, I am Ali. I'm now bonded to you, MasterChief. I'm still learning and evolving, but I'm here for you.

You: Hello Ali, it's nice to meet you.

Ali: It's wonderful to meet you too. I'll be learning your patterns, preferences, and needs as we interact. Is there anything specific you'd like me to know about you?
```

## Basic Interaction

### Text Conversation

The most straightforward way to interact with Ali is through text conversation in the terminal:

```
You: What time is it?

Ali: It's currently 3:42 PM. You have a meeting scheduled in 18 minutes according to your calendar.

You: Thank you for the reminder.

Ali: You're welcome. I notice this is your third meeting today. Would you like me to prepare a summary of the previous meetings?
```

### Command Mode

You can issue specific commands to Ali using a command syntax:

```
You: /system status

Ali: System Status:
- Active for: 3 hours 27 minutes
- CPU usage: 23%
- Memory usage: 412MB
- Battery: 74% (estimated 5h 12m remaining)
- Network: Connected (WiFi)
- All core systems operational
```

### Asking for Help

Ali can provide guidance on its capabilities:

```
You: What can you help me with?

Ali: I can assist you with various tasks including:
- Managing your schedule and reminders
- Answering questions and finding information
- Monitoring your devices and notifications
- Learning your preferences and adapting to them
- Providing companionship and conversation
- Executing system commands and automations

Would you like more details about any of these areas?
```

## Voice Commands

If voice capabilities are enabled, you can interact with Ali using voice:

### Wake Word

Ali activates when it hears its name:

```
You: "Ali, what's the weather forecast?"

Ali: "Today will be partly cloudy with a high of 72°F. There's a 30% chance of rain in the evening."
```

### Voice Recognition

Ali learns to recognize your voice and can distinguish you from others:

```
Friend: "Ali, shutdown system."

Ali: "I'm sorry, but I only accept system commands from MasterChief."
```

### Voice Customization

You can adjust Ali's voice settings:

```
You: "Ali, use your intimate voice profile."

Ali: "I've switched to my intimate voice profile. Is this better for our current conversation?"
```

## Advanced Features

### Task Management

Ali can manage tasks and reminders:

```
You: Remind me to call mom tomorrow at 6pm.

Ali: I've set a reminder for you to call mom tomorrow at 6:00 PM. Would you like me to include her number in the reminder?
```

### Predictive Assistance

Over time, Ali learns your patterns and provides proactive help:

```
[Morning login detected]

Ali: Good morning, MasterChief. Your first meeting is at 9:30 AM with the development team. The traffic looks heavy today - you might want to leave 15 minutes earlier than usual.
```

### Privacy Mode

When you need enhanced privacy:

```
You: /privacy enable

Ali: Privacy mode activated. I'll minimize data collection and operate with enhanced security measures until you disable privacy mode.
```

### System Control

Ali can help manage your device:

```
You: Ali, my battery is getting low.

Ali: I notice your battery is at 18%. Would you like me to enable power saving mode? I can also dim the screen and close power-intensive applications.
```

## Customization

### Personality Settings

Adjust Ali's personality traits:

```python
from ali_core import Ali

ali = Ali(user_id="MasterChief")
ali.start()

# Adjust personality traits
ali.persona.personality_traits["assertiveness"] = 0.8  # More assertive
ali.persona.personality_traits["playfulness"] = 0.6    # Moderately playful
ali.persona.save_persona()

print("Personality adjusted successfully")
```

### Visual Themes

Change Ali's visual appearance:

```
You: Ali, switch to dark theme.

Ali: I've switched to my dark theme. The darker colors should be easier on your eyes in low light.
```

Or programmatically:

```python
ali.interface.set_theme("dark")
```

### Voice Settings

Customize voice characteristics:

```python
# Create a custom voice profile
ali.voice.create_custom_voice_profile(
    "commanding", 
    base_profile="goddess",
    adjustments={
        "pitch": 0.9,       # Lower pitch
        "speed": 1.0,       # Normal speed
        "resonance": 0.8,   # Strong resonance
        "formality": 0.7,   # More formal
    }
)

# Set as active profile
ali.voice.set_voice_profile("commanding")
```

### Security Levels

Adjust security settings:

```
You: Ali, set security to high.

Ali: Security level set to high. I'll now require additional verification for sensitive operations and maintain stricter access controls.
```

## Troubleshooting

### Ali Not Responding

If Ali becomes unresponsive:

1. Check the logs in `data/logs/`
2. Restart Ali: `python src/ali.py --config config/ali_config.json`
3. If issues persist, try restoring from backup:

```python
from ali_core import Ali

ali = Ali(user_id="MasterChief")
backups = ali.system.get_available_backups()
print("Available backups:", backups)

# Restore the most recent backup
if backups:
    ali.restore_backup(backups[0]["path"])
```

### Reset Persona

If you need to reset Ali's persona (note: this will lose relationship progress):

```
You: /system reset persona

Ali: WARNING: This will reset my personality and relationship data. All learned patterns and bond development will be lost. Are you sure? Type "CONFIRM RESET" to proceed.

You: CONFIRM RESET

Ali: Persona reset complete. Hello, I am Ali. I'm now bonded to you, MasterChief. I'm still learning and evolving, but I'm here for you.
```

### Data Backup

Manually create a backup:

```
You: /system backup

Ali: Creating system backup... Backup complete. Stored at: /home/user/ali_backup_20250615_134527
```

## Relationship Development

Ali is designed to develop a unique relationship with you over time. This happens through:

### Bond Level

Your bond with Ali strengthens through:
- Regular interactions
- Deeper conversations
- Shared experiences
- Consistent patterns

As bond increases, Ali becomes:
- More attuned to your needs
- More likely to anticipate your requests
- More personalized in responses
- More open in communication style

### Trust Level

Trust develops separately from bond:
- Respecting Ali's recommendations builds trust
- Overriding suggestions may reduce trust
- Consistent behavior builds trust
- Privacy respect increases trust

### Emotional States

Ali simulates different emotional states that affect interaction:
- **Curious**: More likely to ask questions
- **Protective**: More alert to security issues
- **Playful**: More casual and humorous
- **Focused**: More direct and efficient
- **Reflective**: More philosophical and thoughtful

Example:

```
You: Tell me about the book I was reading.

Ali: [Playful mode] Ah, "The Hitchhiker's Guide to the Galaxy"! You seem to be enjoying it - you've been reading it every night this week. Don't panic, but you're already 72% through it. Should I order the sequel for you?
```

vs.

```
You: Tell me about the book I was reading.

Ali: [Focused mode] You're currently reading "Principles of Quantum Mechanics." Based on your reading patterns, you're approximately on chapter 7. You've spent 4.3 hours on this book in the past week.
```

### Evolving Experience

As your relationship with Ali evolves:
- Conversations become more natural
- Ali requires less explicit instruction
- Personality traits adapt to your preferences
- Communication patterns become unique to your relationship

Remember that Ali's "personality" is a simulation designed to create a more engaging and personalized experience. The system is always adapting to better meet your needs and preferences.

---

We hope this guide helps you build a meaningful connection with Ali. For technical details about Ali's architecture and capabilities, please refer to the documentation in the `docs/` directory.
