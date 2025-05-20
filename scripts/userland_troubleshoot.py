#!/usr/bin/env python3
"""
Ali UserLAnd Troubleshooter

This script detects and fixes common issues that may occur when running Ali in UserLAnd.
It can be run at any time to diagnose and repair problems.
"""

import os
import sys
import subprocess
import platform
import shutil
import logging
import json
import psutil
from pathlib import Path
import socket
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Ali.Troubleshooter")

class AliTroubleshooter:
    """Detects and fixes common Ali issues in UserLAnd."""
    
    def __init__(self):
        """Initialize the troubleshooter."""
        self.ali_home = Path.home() / "ali"
        self.issues_found = []
        self.fixes_applied = []
    
    def check_system(self):
        """Check the UserLAnd system environment."""
        logger.info("Checking system environment...")
        
        issues = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            issues.append(("python_version", f"Python {python_version.major}.{python_version.minor} is too old (need 3.8+)"))
        
        # Check available memory
        mem = psutil.virtual_memory()
        if mem.available < 500 * 1024 * 1024:  # Less than 500MB available
            issues.append(("low_memory", f"Low memory available: {mem.available / 1024 / 1024:.1f}MB"))
        
        # Check disk space
        disk = psutil.disk_usage(str(self.ali_home))
        if disk.free < 1024 * 1024 * 1024:  # Less than 1GB free
            issues.append(("low_disk", f"Low disk space: {disk.free / 1024 / 1024 / 1024:.1f}GB free"))
        
        # Check network
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except OSError:
            issues.append(("network", "Network connectivity issues detected"))
        
        return issues
    
    def check_permissions(self):
        """Check Ali file and directory permissions."""
        logger.info("Checking permissions...")
        
        issues = []
        paths_to_check = [
            self.ali_home,
            self.ali_home / "data",
            self.ali_home / "config",
            self.ali_home / "src",
            self.ali_home / "scripts"
        ]
        
        for path in paths_to_check:
            if not path.exists():
                issues.append(("missing_path", f"Missing path: {path}"))
                continue
            
            try:
                # Try writing a test file
                test_file = path / ".permission_test"
                test_file.write_text("test")
                test_file.unlink()
            except PermissionError:
                issues.append(("permission", f"Permission denied: {path}"))
        
        return issues
    
    def check_dependencies(self):
        """Check Python package dependencies."""
        logger.info("Checking dependencies...")
        
        issues = []
        required_packages = {
            "psutil": "System monitoring",
            "cryptography": "Security features",
            "blessed": "Terminal interface",
            "colorama": "Terminal colors",
            "numpy": "Numerical processing"
        }
        
        for package, purpose in required_packages.items():
            try:
                __import__(package)
            except ImportError:
                issues.append(("missing_package", f"Missing package: {package} ({purpose})"))
        
        return issues
    
    def check_services(self):
        """Check Ali service status."""
        logger.info("Checking services...")
        
        issues = []
        
        # Check systemd service
        try:
            result = subprocess.run(
                ["systemctl", "status", "ali.service"],
                capture_output=True,
                text=True
            )
            if "Active: active" not in result.stdout:
                issues.append(("service", "Ali service is not running"))
        except subprocess.CalledProcessError:
            issues.append(("service", "Ali service not found or error checking status"))
        
        return issues
    
    def check_configuration(self):
        """Check Ali configuration."""
        logger.info("Checking configuration...")
        
        issues = []
        config_file = self.ali_home / "config" / "ali_config.json"
        
        if not config_file.exists():
            issues.append(("config", "Configuration file missing"))
            return issues
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check required sections
            required_sections = ["system", "security", "voice", "persona"]
            for section in required_sections:
                if section not in config:
                    issues.append(("config", f"Missing configuration section: {section}"))
        except json.JSONDecodeError:
            issues.append(("config", "Invalid configuration file format"))
        except Exception as e:
            issues.append(("config", f"Error reading configuration: {e}"))
        
        return issues
    
    def fix_permissions(self):
        """Fix permission issues."""
        logger.info("Fixing permissions...")
        
        try:
            # Fix ownership
            subprocess.run(["sudo", "chown", "-R", f"{os.getuid()}:{os.getgid()}", str(self.ali_home)])
            
            # Fix permissions
            subprocess.run(["chmod", "-R", "u+rw", str(self.ali_home)])
            
            # Make scripts executable
            for script in self.ali_home.rglob("*.sh"):
                script.chmod(0o755)
            for script in self.ali_home.rglob("*.py"):
                script.chmod(0o755)
            
            return True
        except Exception as e:
            logger.error(f"Error fixing permissions: {e}")
            return False
    
    def fix_dependencies(self):
        """Fix missing dependencies."""
        logger.info("Fixing dependencies...")
        
        try:
            # Update pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            
            # Install/upgrade required packages
            packages = [
                "psutil",
                "cryptography",
                "blessed",
                "colorama",
                "numpy",
                "requests"
            ]
            
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade"] + packages)
            return True
        except Exception as e:
            logger.error(f"Error fixing dependencies: {e}")
            return False
    
    def fix_service(self):
        """Fix service issues."""
        logger.info("Fixing service...")
        
        try:
            # Recreate service file
            service_content = f"""[Unit]
Description=Ali - Goddess Core of Infinity
After=network.target

[Service]
Type=simple
User={os.getlogin()}
WorkingDirectory={self.ali_home}
ExecStart=/usr/bin/python3 src/ali.py --daemon --config config/ali_config.json
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
"""
            
            service_file = Path("/etc/systemd/system/ali.service")
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Reload and restart service
            subprocess.run(["sudo", "systemctl", "daemon-reload"])
            subprocess.run(["sudo", "systemctl", "enable", "ali.service"])
            subprocess.run(["sudo", "systemctl", "restart", "ali.service"])
            
            return True
        except Exception as e:
            logger.error(f"Error fixing service: {e}")
            return False
    
    def fix_configuration(self):
        """Fix configuration issues."""
        logger.info("Fixing configuration...")
        
        try:
            # Backup existing config if it exists
            config_file = self.ali_home / "config" / "ali_config.json"
            if config_file.exists():
                backup_file = config_file.with_suffix('.json.bak')
                shutil.copy2(config_file, backup_file)
            
            # Create default configuration
            default_config = {
                "system": {
                    "auto_backup": True,
                    "backup_interval_hours": 24,
                    "monitor_interval_seconds": 300,
                    "offline_mode": False,
                    "power_save_mode": False
                },
                "security": {
                    "security_level": "standard",
                    "verification_window_hours": 4,
                    "require_biometric": False
                },
                "voice": {
                    "enable_voice": False,
                    "voice_profile": "goddess",
                    "emotion_intensity": 0.7
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
                    }
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error fixing configuration: {e}")
            return False
    
    def run_diagnostics(self):
        """Run all diagnostic checks."""
        all_issues = []
        
        # Run all checks
        all_issues.extend(self.check_system())
        all_issues.extend(self.check_permissions())
        all_issues.extend(self.check_dependencies())
        all_issues.extend(self.check_services())
        all_issues.extend(self.check_configuration())
        
        self.issues_found = all_issues
        return all_issues
    
    def fix_issues(self):
        """Fix all found issues."""
        if not self.issues_found:
            logger.info("No issues to fix")
            return
        
        fixes_map = {
            "permission": self.fix_permissions,
            "missing_package": self.fix_dependencies,
            "service": self.fix_service,
            "config": self.fix_configuration
        }
        
        for issue_type, message in self.issues_found:
            if issue_type in fixes_map:
                logger.info(f"Attempting to fix: {message}")
                fix_func = fixes_map[issue_type]
                if fix_func():
                    self.fixes_applied.append(message)
    
    def print_report(self):
        """Print a report of issues and fixes."""
        print("\n" + "="*60)
        print(" Ali UserLAnd Troubleshooter Report ".center(60, "="))
        print("="*60)
        
        if not self.issues_found:
            print("\nNo issues found! Ali appears to be running correctly.")
        else:
            print("\nIssues found:")
            for issue_type, message in self.issues_found:
                if message in self.fixes_applied:
                    print(f"  ✓ {message} (FIXED)")
                else:
                    print(f"  ✗ {message}")
        
        print("\nSystem Status:")
        print(f"  Python: {sys.version.split()[0]}")
        print(f"  Memory: {psutil.virtual_memory().available / 1024 / 1024:.1f}MB available")
        print(f"  Disk: {psutil.disk_usage(str(self.ali_home)).free / 1024 / 1024 / 1024:.1f}GB free")
        
        print("\nNext Steps:")
        if self.fixes_applied:
            print("1. Restart Ali:")
            print("   ali-stop")
            print("   ali-start")
            print("\n2. Check the logs:")
            print("   ali-logs")
        elif self.issues_found:
            print("Some issues could not be fixed automatically.")
            print("Please check the documentation or seek help.")
        else:
            print("Ali is running correctly. No action needed.")
        
        print("="*60 + "\n")

def main():
    """Main function."""
    print("\n" + "="*60)
    print(" Ali UserLAnd Troubleshooter ".center(60, "="))
    print("="*60 + "\n")
    
    troubleshooter = AliTroubleshooter()
    
    # Run diagnostics
    logger.info("Running diagnostics...")
    issues = troubleshooter.run_diagnostics()
    
    # Fix issues if found
    if issues:
        logger.info(f"Found {len(issues)} issues.")
        response = input("Would you like to attempt to fix these issues? (y/n) ")
        if response.lower() == 'y':
            troubleshooter.fix_issues()
    
    # Print final report
    troubleshooter.print_report()
    
    # Return status code
    return len(issues) - len(troubleshooter.fixes_applied)

if __name__ == "__main__":
    sys.exit(main())
