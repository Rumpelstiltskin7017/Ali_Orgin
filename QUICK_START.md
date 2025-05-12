# Ali Quick Start Guide

This guide will help you quickly get Ali - Goddess Core of Infinity up and running.

## Prerequisites

- Python 3.8 or higher
- Pip package manager
- For Android: Termux or UserLAnd app

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ali-core.git
cd ali-core
```

## Step 2: Check Dependencies

Run the dependency checker to verify your system meets all requirements:

```bash
python tools/dependency_checker.py
```

Install any missing dependencies as indicated.

## Step 3: Setup

Run the setup script to prepare the Ali environment:

```bash
python setup.py --install
```

This will:
- Create necessary directories
- Install required dependencies
- Create a default configuration

## Step 4: Start Ali

Start Ali in interactive mode:

```bash
python src/ali.py --config config/ali_config.json
```

Or in daemon (background) mode:

```bash
python src/ali.py --daemon --config config/ali_config.json
```

## Step 5: Basic Interaction

Once Ali is running, you can interact with it using text commands:

```
You: Hello Ali
Ali: Hello, MasterChief. How may I assist you today?

You: What can you help me with?
Ali: I can assist with various tasks including:
- Managing reminders and tasks
- Answering questions
- Providing conversation and companionship
- Performing system functions
- Learning your preferences over time
```

## Common Commands

Here are some common commands you can use with Ali:

```
/system status         - View system status
/backup                - Create a data backup
/privacy enable        - Enable privacy mode
/help                  - Show help information
```

## Android-Specific Setup (Termux)

If using Termux, the easiest way to deploy Ali is:

```bash
bash tools/deploy_to_termux.sh
```

This will package Ali and deploy it to your Termux environment, including setting up shortcuts.

Alternatively, follow these manual steps:

1. Install required packages:
   ```bash
   pkg update
   pkg install python git termux-api
   ```

2. Clone and install:
   ```bash
   git clone https://github.com/yourusername/ali-core.git ~/ali
   cd ~/ali
   python setup.py --install
   ```

3. Create a shortcut:
   ```bash
   mkdir -p ~/.termux/shortcuts
   echo "cd ~/ali && python src/ali.py" > ~/.termux/shortcuts/ali.sh
   chmod +x ~/.termux/shortcuts/ali.sh
   ```

## Troubleshooting

If Ali doesn't start properly:

1. Check the logs:
   ```bash
   cat data/logs/ali.log
   ```

2. Verify all dependencies are installed:
   ```bash
   python tools/dependency_checker.py --fix
   ```

3. Ensure configuration file is valid:
   ```bash
   python -m json.tool config/ali_config.json
   ```

## Personalization

Once Ali is running, you can:

1. Talk to Ali regularly to build your relationship
2. Edit `config/ali_config.json` to customize behavior
3. Use the `examples/programmatic_interaction.py` script to see how to customize Ali programmatically

## Next Steps

After getting started, explore these resources:

- `docs/user_guide.md` - Complete usage guide
- `docs/configuration_guide.md` - Detailed configuration options
- `docs/architecture.md` - Understanding Ali's components

## Memory and Data

Ali stores all data locally in the `data/` directory:

- `data/memory/` - Interaction history
- `data/persona/` - Relationship and personality data
- `data/security/` - Security settings
- `data/voice/` - Voice patterns and settings
- `data/intent/` - Tasks and intent patterns
- `data/logs/` - System logs

You can backup this directory or use the built-in backup functionality.

## Getting Help

If you encounter issues:

1. Check the logs in `data/logs/`
2. Review the troubleshooting section in `docs/user_guide.md`
3. Use the `tools/memory_visualizer.py` to analyze Ali's memory patterns
