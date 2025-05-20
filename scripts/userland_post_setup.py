#!/usr/bin/env python3
"""
Ali UserLAnd Post-Setup Script
Helps users get started with Ali after installation by:
- Verifying the installation
- Setting up initial configuration
- Running basic tests
- Providing quick fixes for common issues
"""

import os
import sys
import subprocess
import json
import logging
import platform
import shutil
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Ali.PostSetup")

class AliPostSetup:
    """Handles post-installation setup and verification."""
    
    def __init__(self):
        """Initialize the post-setup helper."""
        self.ali_home = Path.home() / "ali"
        self.config_file = self.ali_home / "config" / "ali_config.json"
        self.data_dir = self.ali_home / "data"
        self.log_dir = self.data_dir / "logs"
        
        # Track what we've fixed
        self.fixes_applied = []
    
    def verify_installation(self):
        """Verify that Ali was installed correctly."""
        logger.info("Verifying Ali installation...")
        
        checks = [
            (self.ali_home.exists(), "Ali home directory exists"),
            (self.config_file.exists(), "Configuration file exists"),
            ((self.ali_home / "src" / "ali.py").exists(), "Main Ali script exists"),
            (self.data_dir.exists(), "Data directory exists"),
            (self.log_dir.exists(), "Log directory exists")
        ]
        
        all_passed = True
        for check, message in checks:
            if check:
                logger.info(f"✓ {message}")
            else:
                logger.error(f"✗ {message}")
                all_passed = False
        
        return all_passed
    
    def fix_permissions(self):
        """Fix common permission issues."""
        logger.info("Fixing permissions...")
        
        try:
            # Make Ali directory fully accessible to the user
            os.system(f"chmod -R u+rw {self.ali_home}")
            
            # Make scripts executable
            scripts_dir = self.ali_home / "scripts"
            if scripts_dir.exists():
                for script in scripts_dir.glob("*.sh"):
                    os.chmod(script, 0o755)
            
            # Make run script executable
            run_script = self.ali_home / "run_ali.sh"
            if run_script.exists():
                os.chmod(run_script, 0o755)
            
            self.fixes_applied.append("permissions")
            logger.info("Permissions fixed successfully")
            return True
        except Exception as e:
            logger.error(f"Error fixing permissions: {e}")
            return False
    
    def verify_python_environment(self):
        """Verify Python environment and dependencies."""
        logger.info("Verifying Python environment...")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version < (3, 8):
                logger.error(f"Python version {python_version.major}.{python_version.minor} is too old (need 3.8+)")
                return False
            
            # Try importing required packages
            required_packages = [
                "psutil",
                "cryptography",
                "blessed",
                "colorama",
                "numpy"
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                logger.warning(f"Missing packages: {', '.join(missing_packages)}")
                logger.info("Attempting to install missing packages...")
                
                subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
                self.fixes_applied.append("dependencies")
            
            logger.info("Python environment verified successfully")
            return True
        except Exception as e:
            logger.error(f"Error verifying Python environment: {e}")
            return False
    
    def test_ali_startup(self):
        """Test if Ali can start properly."""
        logger.info("Testing Ali startup...")
        
        try:
            # Try starting Ali with --test flag
            process = subprocess.run(
                [sys.executable, str(self.ali_home / "src" / "ali.py"), "--test"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                logger.info("Ali startup test successful")
                return True
            else:
                logger.error(f"Ali startup test failed: {process.stderr}")
                return False
        except subprocess.TimeoutExpired:
            logger.error("Ali startup test timed out")
            return False
        except Exception as e:
            logger.error(f"Error testing Ali startup: {e}")
            return False
    
    def setup_quick_access(self):
        """Set up quick access methods for Ali."""
        logger.info("Setting up quick access...")
        
        try:
            # Create desktop shortcut if running in a GUI environment
            if os.environ.get('DISPLAY'):
                desktop_file = Path.home() / "Desktop" / "ali.desktop"
                with open(desktop_file, 'w') as f:
                    f.write("""[Desktop Entry]
Name=Ali
Comment=Goddess Core of Infinity
Exec=python3 ~/ali/src/ali.py
Terminal=true
Type=Application
Categories=Utility;
""")
                os.chmod(desktop_file, 0o755)
            
            # Create aliases file
            aliases_file = self.ali_home / "aliases.sh"
            with open(aliases_file, 'w') as f:
                f.write("""# Ali aliases
alias ali='cd ~/ali && python3 src/ali.py'
alias ali-logs='tail -f ~/ali/data/logs/ali.log'
alias ali-status='systemctl status ali.service'
alias ali-restart='systemctl restart ali.service'
""")
            
            # Add source to .bashrc if not already there
            bashrc = Path.home() / ".bashrc"
            source_line = f"source {aliases_file}"
            
            if bashrc.exists():
                with open(bashrc, 'r') as f:
                    content = f.read()
                if source_line not in content:
                    with open(bashrc, 'a') as f:
                        f.write(f"\n# Ali aliases\n{source_line}\n")
            
            self.fixes_applied.append("quick_access")
            logger.info("Quick access setup complete")
            return True
        except Exception as e:
            logger.error(f"Error setting up quick access: {e}")
            return False
    
    def verify_system_resources(self):
        """Check if system has adequate resources."""
        logger.info("Checking system resources...")
        
        try:
            import psutil
            
            # Check CPU
            cpu_count = psutil.cpu_count()
            logger.info(f"CPU cores: {cpu_count}")
            
            # Check memory
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            logger.info(f"Total memory: {memory_gb:.1f} GB")
            
            # Check disk space
            disk = psutil.disk_usage(str(self.ali_home))
            disk_gb = disk.free / (1024**3)
            logger.info(f"Free disk space: {disk_gb:.1f} GB")
            
            # Warn if resources are low
            warnings = []
            if cpu_count < 2:
                warnings.append("Low CPU cores")
            if memory_gb < 2:
                warnings.append("Low memory")
            if disk_gb < 1:
                warnings.append("Low disk space")
            
            if warnings:
                logger.warning(f"Resource warnings: {', '.join(warnings)}")
                return False
            
            logger.info("System resources look good")
            return True
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return False
    
    def run_startup_test(self):
        """Run a series of startup tests."""
        logger.info("Running startup tests...")
        
        tests = [
            ("Config loading", self._test_config_loading),
            ("Data directory access", self._test_data_access),
            ("Log writing", self._test_log_writing),
            ("Basic interaction", self._test_basic_interaction)
        ]
        
        all_passed = True
        for name, test_func in tests:
            try:
                logger.info(f"Running test: {name}")
                if test_func():
                    logger.info(f"✓ {name} test passed")
                else:
                    logger.error(f"✗ {name} test failed")
                    all_passed = False
            except Exception as e:
                logger.error(f"✗ {name} test error: {e}")
                all_passed = False
        
        return all_passed
    
    def _test_config_loading(self):
        """Test if configuration can be loaded."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return isinstance(config, dict)
        except Exception:
            return False
    
    def _test_data_access(self):
        """Test if data directories are accessible."""
        try:
            test_file = self.data_dir / "test_access"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def _test_log_writing(self):
        """Test if logs can be written."""
        try:
            test_log = self.log_dir / "test.log"
            test_log.write_text("test log entry")
            test_log.unlink()
            return True
        except Exception:
            return False
    
    def _test_basic_interaction(self):
        """Test basic interaction with Ali."""
        try:
            process = subprocess.run(
                [sys.executable, str(self.ali_home / "src" / "ali.py"), "--test-interaction"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return process.returncode == 0
        except Exception:
            return False
    
    def apply_fixes(self):
        """Apply any necessary fixes based on test results."""
        logger.info("Applying fixes...")
        
        # List of potential fixes and their corresponding methods
        fixes = [
            (self.fix_permissions, "permissions"),
            (self.verify_python_environment, "python environment"),
            (self.setup_quick_access, "quick access")
        ]
        
        for fix_func, name in fixes:
            try:
                logger.info(f"Applying fix: {name}")
                if fix_func():
                    logger.info(f"✓ Successfully applied {name} fix")
                else:
                    logger.error(f"✗ Failed to apply {name} fix")
            except Exception as e:
                logger.error(f"✗ Error applying {name} fix: {e}")
    
    def print_summary(self):
        """Print a summary of what was done."""
        print("\n" + "="*60)
        print(" Ali Post-Setup Summary ".center(60, "="))
        print("="*60)
        
        if self.fixes_applied:
            print("\nFixes applied:")
            for fix in self.fixes_applied:
                print(f"  ✓ {fix}")
        else:
            print("\nNo fixes were necessary.")
        
        print("\nNext steps:")
        print("1. Start Ali:")
        print("   cd ~/ali && python3 src/ali.py")
        print("\n2. View logs:")
        print("   tail -f ~/ali/data/logs/ali.log")
        print("\n3. For quick access, source your aliases:")
        print("   source ~/.bashrc")
        
        print("\nUseful commands:")
        print("- ali           (start Ali)")
        print("- ali-logs      (view logs)")
        print("- ali-status    (check service status)")
        print("- ali-restart   (restart service)")
        
        print("\nFor more information, see:")
        print("- ~/ali/QUICK_START.md")
        print("- ~/ali/docs/user_guide.md")
        
        print("="*60 + "\n")

def main():
    """Main function."""
    print("\n" + "="*60)
    print(" Ali Post-Setup Helper ".center(60, "="))
    print("="*60 + "\n")
    
    post_setup = AliPostSetup()
    
    # Run verifications and tests
    installation_ok = post_setup.verify_installation()
    if not installation_ok:
        logger.warning("Installation verification failed, attempting fixes...")
        post_setup.apply_fixes()
    
    # Verify Python environment
    python_ok = post_setup.verify_python_environment()
    if not python_ok:
        logger.warning("Python environment needs attention")
    
    # Check system resources
    resources_ok = post_setup.verify_system_resources()
    if not resources_ok:
        logger.warning("System resources may be insufficient")
    
    # Run startup test
    startup_ok = post_setup.run_startup_test()
    if not startup_ok:
        logger.warning("Startup tests failed, attempting fixes...")
        post_setup.apply_fixes()
    
    # Print summary
    post_setup.print_summary()
    
    # Return status
    return 0 if installation_ok and python_ok and startup_ok else 1

if __name__ == "__main__":
    sys.exit(main())
