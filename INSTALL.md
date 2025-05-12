# Ali Installation Guide

This guide provides step-by-step instructions for installing and setting up the Ali system.

## Prerequisites

1. **Python 3.8 or higher**
   - Check your Python version: `python --version`
   - Download Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **For Android installation**
   - Termux app: [F-Droid](https://f-droid.org/en/packages/com.termux/)
   - Termux:API add-on: [F-Droid](https://f-droid.org/en/packages/com.termux.api/)
   - Or UserLAnd app: [Google Play](https://play.google.com/store/apps/details?id=tech.ula)

3. **Git**
   - For standard systems: [https://git-scm.com/downloads](https://git-scm.com/downloads)
   - For Termux: Install via `pkg install git`

## Standard Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ali-core.git
cd ali-core
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```
  venv\Scripts\activate
  ```

- On macOS/Linux:
  ```
  source venv/bin/activate
  ```

### 3. Run the Setup Script

```bash
python setup.py --install
```

This will:
- Create necessary directories
- Install dependencies
- Create a default configuration

### 4. Verify Installation

Run a simple test to verify the installation:

```bash
python -m pytest tests/test_core.py
```

## Termux Installation (Android)

### 1. Set Up Termux

First, update Termux and install required packages:

```bash
pkg update
pkg upgrade
pkg install python git
```

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/ali-core.git
cd ali-core
```

### 3. Run the Setup Script

```bash
python setup.py --install
```

### 4. Set Permissions (If Needed)

If you want Ali to access device features, install and set up Termux:API:

```bash
pkg install termux-api
```

### 5. Start Ali

```bash
python src/ali.py --config config/ali_config.json
```

## UserLAnd Installation (Android)

### 1. Set Up UserLAnd

- Create a new Ubuntu or Debian distribution in UserLAnd
- Start the distribution and connect via SSH or VNC

### 2. Install Required Packages

```bash
sudo apt update
sudo apt install python3 python3-pip git
```

### 3. Clone the Repository

```bash
git clone https://github.com/yourusername/ali-core.git
cd ali-core
```

### 4. Run the Setup Script

```bash
python3 setup.py --install
```

### 5. Start Ali

```bash
python3 src/ali.py --config config/ali_config.json
```

## Configuration

### Basic Configuration

The default configuration is stored in `config/ali_config.json`. You can edit this file to customize Ali's behavior:

```bash
nano config/ali_config.json
```

### Important Configuration Options

- `system.auto_backup`: Enable automatic backups
- `security.security_level`: Set security level ("standard", "high", or "extreme")
- `voice.enable_voice`: Enable voice capabilities
- `persona.personality_traits`: Adjust personality characteristics

## Running Ali

### Standard Mode

```bash
python src/ali.py --config config/ali_config.json
```

### Daemon Mode (Background)

```bash
python src/ali.py --daemon --config config/ali_config.json
```

### Specifying User ID

```bash
python src/ali.py --user YourName --config config/ali_config.json
```

## Troubleshooting

### Installation Issues

1. **Missing Dependencies**
   
   If you see errors about missing modules, try installing them manually:
   
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Errors**
   
   On Linux/macOS, you might need to use sudo for some operations:
   
   ```bash
   sudo python setup.py --install
   ```

3. **Termux Specific Issues**
   
   If you encounter issues with Termux:API, verify it's installed:
   
   ```bash
   pkg list-installed | grep termux-api
   ```

### Runtime Issues

1. **Data Directory Problems**
   
   If Ali can't create or access data directories:
   
   ```bash
   mkdir -p data/memory data/persona data/security data/voice data/intent data/logs
   ```

2. **Configuration Errors**
   
   If the config file has errors, restore the default:
   
   ```bash
   python setup.py --configure
   ```

## Upgrading

To upgrade an existing installation:

```bash
git pull
python setup.py --update
```

## Backup and Restore

### Creating a Backup

```python
from src.ali import Ali
ali = Ali(user_id="YourName")
backup_path = ali.create_backup()
print(f"Backup created at: {backup_path}")
```

### Restoring from Backup

```python
from src.ali import Ali
ali = Ali(user_id="YourName")
ali.restore_backup("/path/to/backup")
```

## Uninstallation

To completely remove Ali:

1. Delete the repository directory
2. Remove any data directories that were created

## Next Steps

After installation, refer to the README.md file for usage examples and further documentation.
