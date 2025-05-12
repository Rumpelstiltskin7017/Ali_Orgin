"""
Ali System Module
---------------
Implements the infrastructure aspects of the Ali system:
- Device integration (Termux, UserLAnd)
- Storage management
- Background processes
- Offline resilience
- System monitoring

This module handles the underlying system-level functionality of Ali.
"""

import logging
import os
import json
import platform
import subprocess
import shutil
import psutil
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time

logger = logging.getLogger("Ali.System")

class AliSystem:
    """System-level management for the Ali infrastructure."""
    
    def __init__(self, config_path=None):
        """Initialize the Ali system manager."""
        # System identification
        self.is_android = 'ANDROID_ROOT' in os.environ
        self.is_termux = 'TERMUX_VERSION' in os.environ
        self.system_type = self._detect_system_type()
        
        # Storage paths
        self.base_path = Path(os.path.expanduser("~"))
        self.data_path = self.base_path / "ali_data"
        self.backup_path = self.base_path / "ali_backup"
        self.sd_card_path = None  # Will be detected if available
        
        # System status
        self.system_status = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "storage_usage": 0,
            "battery_level": 100,
            "network_status": "unknown",
            "last_backup": None
        }
        
        # Background threads
        self.monitor_thread = None
        self.backup_thread = None
        self.active = True
        
        # Load configuration if provided
        self.config = {
            "auto_backup": True,
            "backup_interval_hours": 24,
            "use_external_storage": True,
            "monitor_interval_seconds": 300,  # 5 minutes
            "offline_mode": False,
            "power_save_mode": False,
        }
        
        if config_path:
            self._load_config(config_path)
        
        # Ensure data directories exist
        self._setup_directories()
        
        # Detect external storage if on Android
        if self.is_android and self.config["use_external_storage"]:
            self._detect_external_storage()
        
        logger.info(f"Ali System initialized on {self.system_type}")
    
    def _detect_system_type(self):
        """Detect the type of system Ali is running on."""
        system = platform.system()
        
        if self.is_termux:
            return "Termux"
        elif 'USERLAND_' in os.environ:
            return "UserLAnd"
        elif self.is_android:
            return "Android"
        elif system == "Linux":
            return "Linux"
        elif system == "Darwin":
            return "macOS"
        elif system == "Windows":
            return "Windows"
        else:
            return "Unknown"
    
    def _setup_directories(self):
        """Set up required data directories."""
        try:
            # Create main data directory
            self.data_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self.data_path / "memory").mkdir(exist_ok=True)
            (self.data_path / "persona").mkdir(exist_ok=True)
            (self.data_path / "security").mkdir(exist_ok=True)
            (self.data_path / "logs").mkdir(exist_ok=True)
            
            # Create backup directory
            self.backup_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("Data directories set up successfully")
        except Exception as e:
            logger.error(f"Error setting up directories: {e}")
    
    def _load_config(self, config_path):
        """Load system configuration from file."""
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def _detect_external_storage(self):
        """Detect external storage on Android devices."""
        # Common paths for SD cards on Android
        possible_paths = [
            "/storage/sdcard1",
            "/storage/extSdCard",
            "/storage/external_SD",
            "/storage/emulated/0/external_sd",
            "/mnt/media_rw/sdcard1",
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                try:
                    # Check if we can write to it
                    test_file = Path(path) / "ali_test"
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    
                    # If we can write, set it as SD card path
                    self.sd_card_path = Path(path)
                    logger.info(f"External storage detected at {path}")
                    break
                except:
                    continue
        
        if not self.sd_card_path:
            logger.warning("No writeable external storage detected")
    
    def start_system_services(self):
        """Start background system services."""
        # Start system monitoring
        self.monitor_thread = threading.Thread(target=self._system_monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Start backup service if configured
        if self.config["auto_backup"]:
            self.backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
            self.backup_thread.start()
        
        logger.info("System services started")
        return True
    
    def _system_monitor_loop(self):
        """Background loop for monitoring system status."""
        while self.active:
            try:
                self._update_system_status()
                
                # Adjust behavior based on system status
                self._adapt_to_system_status()
                
                # Wait for next check
                time.sleep(self.config["monitor_interval_seconds"])
            except Exception as e:
                logger.error(f"Error in system monitor: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def _update_system_status(self):
        """Update the current system status metrics."""
        try:
            # CPU usage
            self.system_status["cpu_usage"] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_status["memory_usage"] = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage(str(self.data_path))
            self.system_status["storage_usage"] = disk.percent
            
            # Battery status (if available)
            try:
                battery = psutil.sensors_battery()
                if battery:
                    self.system_status["battery_level"] = battery.percent
                    self.system_status["power_plugged"] = battery.power_plugged
            except:
                pass
            
            # Network status
            if self._check_network_connection():
                self.system_status["network_status"] = "connected"
            else:
                self.system_status["network_status"] = "disconnected"
            
            # Log the status update
            logger.debug(f"System status updated: {self.system_status}")
        except Exception as e:
            logger.error(f"Error updating system status: {e}")
    
    def _check_network_connection(self):
        """Check if the system has an active network connection."""
        try:
            # Try to connect to a reliable host
            result = subprocess.run(
                ["ping", "-c", "1", "8.8.8.8"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=3
            )
            return result.returncode == 0
        except:
            return False
    
    def _adapt_to_system_status(self):
        """Adapt system behavior based on status."""
        # Enter power save mode if battery is low
        if (self.system_status.get("battery_level", 100) < 20 and 
            not self.system_status.get("power_plugged", False)):
            self.config["power_save_mode"] = True
            logger.info("Entering power save mode due to low battery")
        elif self.system_status.get("battery_level", 0) > 30:
            self.config["power_save_mode"] = False
        
        # Adjust monitor interval based on power mode
        if self.config["power_save_mode"]:
            self.config["monitor_interval_seconds"] = 600  # 10 minutes
        else:
            self.config["monitor_interval_seconds"] = 300  # 5 minutes
        
        # Enter offline mode if network is unavailable
        if self.system_status["network_status"] == "disconnected":
            self.config["offline_mode"] = True
            logger.info("Entering offline mode due to network disconnection")
        else:
            self.config["offline_mode"] = False
    
    def _backup_loop(self):
        """Background loop for performing automatic backups."""
        while self.active:
            try:
                # Check if it's time for a backup
                if self.system_status["last_backup"]:
                    last_backup = datetime.fromisoformat(self.system_status["last_backup"])
                    elapsed = datetime.now() - last_backup
                    if elapsed.total_seconds() < self.config["backup_interval_hours"] * 3600:
                        # Not time yet
                        time.sleep(3600)  # Check again in an hour
                        continue
                
                # Perform backup
                self.create_backup()
                
                # Wait until next backup interval
                time.sleep(self.config["backup_interval_hours"] * 3600)
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")
                time.sleep(3600)  # Wait an hour before retrying
    
    def create_backup(self):
        """Create a backup of all Ali data."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"ali_backup_{timestamp}"
            
            # Determine backup location
            backup_dir = self.backup_path
            if self.sd_card_path and self.config["use_external_storage"]:
                sd_backup_dir = self.sd_card_path / "ali_backup"
                sd_backup_dir.mkdir(exist_ok=True)
                backup_dir = sd_backup_dir
            
            # Create backup directory
            backup_path = backup_dir / backup_name
            backup_path.mkdir(parents=True)
            
            # Copy data directory
            shutil.copytree(self.data_path, backup_path / "data", dirs_exist_ok=True)
            
            # Save configuration
            with open(backup_path / "config.json", 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Update last backup time
            self.system_status["last_backup"] = datetime.now().isoformat()
            
            # Clean up old backups (keep last 5)
            self._cleanup_old_backups(backup_dir)
            
            logger.info(f"Backup created at {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def _cleanup_old_backups(self, backup_dir):
        """Clean up old backups, keeping only the 5 most recent ones."""
        try:
            backups = sorted([
                d for d in backup_dir.iterdir() 
                if d.is_dir() and d.name.startswith("ali_backup_")
            ], key=lambda d: d.name, reverse=True)
            
            # Keep the 5 most recent
            for old_backup in backups[5:]:
                shutil.rmtree(old_backup)
                logger.info(f"Removed old backup: {old_backup}")
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def restore_from_backup(self, backup_path):
        """Restore Ali data from a backup."""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists() or not backup_dir.is_dir():
                logger.error(f"Backup not found: {backup_path}")
                return False
            
            # Verify backup structure
            if not (backup_dir / "data").exists():
                logger.error(f"Invalid backup structure at {backup_path}")
                return False
            
            # Stop services
            self.active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            if self.backup_thread:
                self.backup_thread.join(timeout=5)
            
            # Backup current data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = self.backup_path / f"pre_restore_{timestamp}"
            shutil.copytree(self.data_path, current_backup)
            
            # Clear current data
            shutil.rmtree(self.data_path)
            self.data_path.mkdir(parents=True)
            
            # Restore from backup
            shutil.copytree(backup_dir / "data", self.data_path, dirs_exist_ok=True)
            
            # Restore configuration if available
            if (backup_dir / "config.json").exists():
                with open(backup_dir / "config.json", 'r') as f:
                    self.config.update(json.load(f))
            
            logger.info(f"Successfully restored from backup: {backup_path}")
            
            # Restart services
            self.active = True
            self.start_system_services()
            
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            # Try to re-activate services even after failure
            self.active = True
            self.start_system_services()
            return False
    
    def get_available_backups(self):
        """Get a list of available backups."""
        backups = []
        
        # Check internal backups
        try:
            for backup_dir in self.backup_path.glob("ali_backup_*"):
                if backup_dir.is_dir():
                    backup_info = {
                        "path": str(backup_dir),
                        "timestamp": self._parse_backup_timestamp(backup_dir.name),
                        "location": "internal"
                    }
                    backups.append(backup_info)
        except Exception as e:
            logger.error(f"Error reading internal backups: {e}")
        
        # Check SD card backups if available
        if self.sd_card_path:
            sd_backup_dir = self.sd_card_path / "ali_backup"
            if sd_backup_dir.exists():
                try:
                    for backup_dir in sd_backup_dir.glob("ali_backup_*"):
                        if backup_dir.is_dir():
                            backup_info = {
                                "path": str(backup_dir),
                                "timestamp": self._parse_backup_timestamp(backup_dir.name),
                                "location": "external"
                            }
                            backups.append(backup_info)
                except Exception as e:
                    logger.error(f"Error reading external backups: {e}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        return backups
    
    def _parse_backup_timestamp(self, backup_name):
        """Parse timestamp from backup directory name."""
        try:
            # Extract timestamp portion (ali_backup_YYYYMMDD_HHMMSS)
            timestamp_str = backup_name.split("_", 2)[2]
            return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except:
            # If parsing fails, return a default old date
            return datetime(2000, 1, 1)
    
    def execute_system_command(self, command, timeout=30):
        """Execute a system command securely."""
        try:
            # Security check - don't allow dangerous commands
            if self._is_dangerous_command(command):
                logger.warning(f"Dangerous command blocked: {command}")
                return {
                    "success": False,
                    "output": "Command blocked for security reasons",
                    "error": "Security restriction"
                }
            
            # Execute the command
            logger.info(f"Executing system command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {timeout} seconds",
                "code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "code": -1
            }
    
    def _is_dangerous_command(self, command):
        """Check if a command might be dangerous."""
        # Simple check for obviously dangerous commands
        dangerous_patterns = [
            "rm -rf", "mkfs", "dd if=", "format", "> /dev/",
            ":(){:|:&};:", "chmod -R 777", "wget", "curl",
            "sudo", "apt-get", "apt", "npm install -g"
        ]
        
        command_lower = command.lower()
        return any(pattern in command_lower for pattern in dangerous_patterns)
    
    def get_system_info(self):
        """Get detailed system information."""
        info = {
            "timestamp": datetime.now().isoformat(),
            "system_type": self.system_type,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "is_android": self.is_android,
            "is_termux": self.is_termux,
            "cpu_count": os.cpu_count(),
            "status": self.system_status,
            "data_path": str(self.data_path),
            "backup_path": str(self.backup_path),
            "external_storage": str(self.sd_card_path) if self.sd_card_path else None,
            "config": self.config
        }
        
        # Add memory information
        try:
            memory = psutil.virtual_memory()
            info["memory"] = {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "used_percent": memory.percent
            }
        except:
            info["memory"] = "unavailable"
        
        # Add disk information
        try:
            disk = psutil.disk_usage(str(self.data_path))
            info["disk"] = {
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024),
                "used_percent": disk.percent
            }
        except:
            info["disk"] = "unavailable"
        
        return info
    
    def shutdown(self):
        """Gracefully shut down the Ali system."""
        logger.info("Initiating Ali system shutdown")
        
        # Stop background threads
        self.active = False
        
        # Wait for threads to complete
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        
        # Create final backup
        self.create_backup()
        
        logger.info("Ali system shutdown complete")
        return True
