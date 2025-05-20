#!/usr/bin/env python3
"""
Ali - Goddess Core of Infinity
Setup Script

This script manages installation and setup of the Ali system.
"""

import os
import sys
import subprocess
import argparse
import platform
import json
from pathlib import Path

def check_python_version():
    """Check if the Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Error: Ali requires Python {required_version[0]}.{required_version[1]} or higher.")
        print(f"Current Python version is {current_version[0]}.{current_version[1]}.")
        return False
    
    return True

def check_termux():
    """Check if running in Termux environment."""
    return 'TERMUX_VERSION' in os.environ

def check_userland():
    """Check if running in UserLAnd environment."""
    return any(key.startswith('USERLAND_') for key in os.environ)

def is_android():
    """Check if running on Android."""
    return 'ANDROID_ROOT' in os.environ or check_termux() or check_userland()

def create_directories():
    """Create required directories for Ali."""
    directories = [
        "data",
        "data/memory",
        "data/persona",
        "data/security",
        "data/voice",
        "data/intent",
        "data/logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies."""
    requirements_file = "requirements.txt"
    
    if not Path(requirements_file).exists():
        print(f"Error: {requirements_file} not found.")
        return False
    
    print("Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def configure_termux():
    """Configure Termux-specific settings."""
    if not check_termux():
        return True
    
    print("Configuring Termux environment...")
    
    try:
        # Check for Termux API package
        result = subprocess.run(
            ["pkg", "list-installed", "termux-api"], 
            capture_output=True, 
            text=True
        )
        
        if "termux-api" not in result.stdout:
            print("Installing Termux API package...")
            subprocess.run(["pkg", "install", "termux-api"], check=True)
        
        # Create Termux boot script to auto-start Ali
        termux_boot_dir = Path(os.environ.get('HOME', '.')) / ".termux" / "boot"
        termux_boot_dir.mkdir(parents=True, exist_ok=True)
        
        boot_script = termux_boot_dir / "start-ali.sh"
        with open(boot_script, 'w') as f:
            f.write("#!/data/data/com.termux/files/usr/bin/bash\n")
            f.write("cd $HOME/ali\n")
            f.write("python src/ali.py --daemon --config config/ali_config.json > $HOME/ali_boot.log 2>&1 &\n")
        
        # Make boot script executable
        os.chmod(boot_script, 0o755)
        
        print("Termux configuration complete.")
        return True
    
    except Exception as e:
        print(f"Error configuring Termux: {e}")
        return False

def configure_userland():
    """Configure UserLAnd-specific settings."""
    if not check_userland():
        return True
    
    print("Configuring UserLAnd environment...")
    
    try:
        # Create systemd service if systemd is available
        if Path("/bin/systemctl").exists():
            service_path = Path("/etc/systemd/system/ali.service")
            
            if not service_path.exists():
                print("Creating systemd service for Ali...")
                
                service_content = """
[Unit]
Description=Ali Goddess Core of Infinity
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/ali
ExecStart=/usr/bin/python3 src/ali.py --daemon --config config/ali_config.json
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
                """
                
                # Write service file
                with open(service_path, 'w') as f:
                    f.write(service_content)
                
                # Enable and start service
                subprocess.run(["systemctl", "enable", "ali.service"], check=True)
                subprocess.run(["systemctl", "start", "ali.service"], check=True)
        
        print("UserLAnd configuration complete.")
        return True
    
    except Exception as e:
        print(f"Error configuring UserLAnd: {e}")
        return False

def create_default_config():
    """Create default configuration if not present."""
    config_path = Path("config/ali_config.json")
    
    if config_path.exists():
        print("Configuration file already exists.")
        return True
    
    print("Creating default configuration...")
    
    # This is a simplified version - the actual config was created separately
    default_config = {
        "system": {
            "auto_backup": True,
            "backup_interval_hours": 24,
            "monitor_interval_seconds": 300
        },
        "security": {
            "security_level": "high"
        },
        "voice": {
            "enable_voice": True,
            "voice_profile": "goddess"
        }
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"Default configuration created at {config_path}")
        return True
    except Exception as e:
        print(f"Error creating default configuration: {e}")
        return False

def run_tests():
    """Run system tests."""
    print("Running system tests...")
    
    try:
        # Check for test directory
        if not Path("tests").exists():
            print("Tests directory not found. Skipping tests.")
            return True
        
        # Run pytest if available
        subprocess.run([sys.executable, "-m", "pytest", "tests"], check=True)
        print("Tests completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Test failures: {e}")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Ali - Setup Script")
    parser.add_argument('--install', action='store_true', help="Install Ali")
    parser.add_argument('--update', action='store_true', help="Update existing installation")
    parser.add_argument('--test', action='store_true', help="Run tests")
    parser.add_argument('--configure', action='store_true', help="Configure environment")
    args = parser.parse_args()
    
    # Default to install if no arguments provided
    if not (args.install or args.update or args.test or args.configure):
        args.install = True
    
    # Display banner
    print("=" * 60)
    print("            Ali - Goddess Core of Infinity             ")
    print("                  Setup Utility                        ")
    print("=" * 60)
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Termux: {'Yes' if check_termux() else 'No'}")
    print(f"UserLAnd: {'Yes' if check_userland() else 'No'}")
    print(f"Android: {'Yes' if is_android() else 'No'}")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Handle different modes
    if args.install:
        print("Installing Ali...")
        
        create_directories()
        if not install_dependencies():
            return 1
        
        create_default_config()
        
        if check_termux():
            configure_termux()
        elif check_userland():
            configure_userland()
        
        print("Ali installation complete!")
    
    if args.update:
        print("Updating Ali...")
        
        if not install_dependencies():
            return 1
        
        print("Ali update complete!")
    
    if args.test:
        if not run_tests():
            return 1
    
    if args.configure:
        print("Configuring environment...")
        
        create_directories()
        create_default_config()
        
        if check_termux():
            configure_termux()
        elif check_userland():
            configure_userland()
        
        print("Configuration complete!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
