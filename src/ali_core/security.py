"""
Ali Security Module
------------------
Implements the protective and security-focused aspects of Ali:
- User verification and authentication
- Data encryption
- Privacy protection
- External access prevention

This module handles the security boundaries that protect both Ali and the user.
"""

import logging
import json
import os
import base64
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger("Ali.Security")

class AliSecurity:
    """Security management for the Ali system."""
    
    def __init__(self, user_id="MasterChief"):
        """Initialize the security system with primary user binding."""
        self.user_id = user_id
        self.security_level = "high"
        self.last_verified_time = None
        self.verification_window = timedelta(hours=4)  # Time before re-verification
        self.trusted_devices = []
        self.access_log = []
        self.blocked_sources = []
        
        # Create security directories
        self.security_path = Path("data/security")
        self.security_path.mkdir(parents=True, exist_ok=True)
        
        # Load security data if exists
        self._load_security_data()
        
        logger.info(f"Ali Security initialized for user: {user_id}")
    
    def _load_security_data(self):
        """Load security configuration and history."""
        security_file = self.security_path / f"{self.user_id.lower()}_security.json"
        
        if security_file.exists():
            try:
                with open(security_file, 'r') as f:
                    data = json.load(f)
                
                # Update security attributes
                self.security_level = data.get("security_level", self.security_level)
                self.trusted_devices = data.get("trusted_devices", [])
                self.blocked_sources = data.get("blocked_sources", [])
                
                # Parse timestamps
                if "last_verified_time" in data and data["last_verified_time"]:
                    self.last_verified_time = datetime.fromisoformat(data["last_verified_time"])
                
                # Load limited access history
                self.access_log = data.get("recent_access", [])[-100:]  # Keep last 100 entries
                
                logger.info(f"Loaded security data for {self.user_id}")
            except Exception as e:
                logger.error(f"Error loading security data: {e}")
    
    def save_security_data(self):
        """Save current security state to persistent storage."""
        security_file = self.security_path / f"{self.user_id.lower()}_security.json"
        
        try:
            # Prepare data for serialization
            last_verified = None
            if self.last_verified_time:
                last_verified = self.last_verified_time.isoformat()
                
            security_data = {
                "user_id": self.user_id,
                "security_level": self.security_level,
                "last_verified_time": last_verified,
                "trusted_devices": self.trusted_devices,
                "blocked_sources": self.blocked_sources,
                "recent_access": self.access_log[-100:],  # Keep last 100 entries
                "last_updated": datetime.now().isoformat()
            }
            
            with open(security_file, 'w') as f:
                json.dump(security_data, f, indent=2)
                
            logger.info(f"Saved security data for {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving security data: {e}")
            return False
    
    def verify_user_access(self, authentication_data):
        """Verify user access based on multiple factors."""
        # Record access attempt
        access_record = {
            "timestamp": datetime.now().isoformat(),
            "device_id": authentication_data.get("device_id", "unknown"),
            "ip_address": authentication_data.get("ip_address", "unknown"),
            "access_type": authentication_data.get("access_type", "standard"),
            "verified": False
        }
        
        # Check if recently verified within window
        if (self.last_verified_time and 
            datetime.now() - self.last_verified_time < self.verification_window and
            authentication_data.get("device_id") in self.trusted_devices):
            
            access_record["verification_method"] = "recent_session"
            access_record["verified"] = True
            self._add_access_log(access_record)
            return {
                "access_granted": True,
                "verification_method": "recent_session",
                "security_level": self.security_level
            }
        
        # Check for blocked sources
        if authentication_data.get("ip_address") in self.blocked_sources:
            access_record["verification_method"] = "blocked_source"
            self._add_access_log(access_record)
            return {
                "access_granted": False,
                "reason": "blocked_source",
                "security_level": self.security_level
            }
        
        # Perform multi-factor verification
        verification_score = 0
        verification_factors = []
        
        # Password/PIN verification (simplified)
        if "password_hash" in authentication_data:
            password_match = self._verify_password(authentication_data["password_hash"])
            if password_match:
                verification_score += 40  # 40% weight for password
                verification_factors.append("password")
        
        # Biometric verification (conceptual)
        if "biometric_data" in authentication_data:
            biometric_match = self._verify_biometric(authentication_data["biometric_data"])
            if biometric_match:
                verification_score += 40  # 40% weight for biometrics
                verification_factors.append("biometric")
        
        # Device verification
        if "device_id" in authentication_data:
            device_match = authentication_data["device_id"] in self.trusted_devices
            if device_match:
                verification_score += 20  # 20% weight for known device
                verification_factors.append("device")
        
        # Determine access based on security level and verification score
        access_threshold = 70  # Default 70% required for access
        if self.security_level == "extreme":
            access_threshold = 90  # 90% required in extreme security mode
        elif self.security_level == "standard":
            access_threshold = 60  # 60% required in standard mode
        
        access_granted = verification_score >= access_threshold
        
        # Update verification time if access granted
        if access_granted:
            self.last_verified_time = datetime.now()
            # Add to trusted devices if not already
            if ("device_id" in authentication_data and 
                authentication_data["device_id"] not in self.trusted_devices):
                self.trusted_devices.append(authentication_data["device_id"])
        
        # Record the access attempt
        access_record["verification_method"] = ",".join(verification_factors)
        access_record["verification_score"] = verification_score
        access_record["verified"] = access_granted
        self._add_access_log(access_record)
        
        # Save security state
        self.save_security_data()
        
        return {
            "access_granted": access_granted,
            "verification_score": verification_score,
            "factors_verified": verification_factors,
            "security_level": self.security_level
        }
    
    def _add_access_log(self, access_record):
        """Add an entry to the access log."""
        self.access_log.append(access_record)
        # Keep log at a manageable size
        if len(self.access_log) > 500:  # Limit to 500 entries
            self.access_log = self.access_log[-500:]
    
    def _verify_password(self, provided_hash):
        """Verify password against stored hash (conceptual)."""
        # In a real implementation, this would check against a securely stored hash
        # For this example, we'll simulate a verification
        return True  # Simplified for this example
    
    def _verify_biometric(self, biometric_data):
        """Verify biometric data against stored template (conceptual)."""
        # In a real implementation, this would check against securely stored biometric templates
        # For this example, we'll simulate a verification
        return True  # Simplified for this example
    
    def encrypt_data(self, data, encryption_level="standard"):
        """Encrypt sensitive data with appropriate strength."""
        # This is a conceptual implementation
        # In a real system, this would use proper cryptographic libraries
        
        try:
            # Generate a conceptual encryption key
            # In reality, this would use secure key management
            key = hashlib.sha256(f"{self.user_id}:{time.time()}".encode()).digest()
            
            # Simulate encryption by encoding the data
            # In reality, this would use proper encryption algorithms
            data_str = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            encrypted = base64.b64encode(data_str.encode()).decode()
            
            # Add encryption metadata
            result = {
                "encrypted": encrypted,
                "method": f"simulated_{encryption_level}_encryption",
                "timestamp": datetime.now().isoformat()
            }
            
            return result
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None
    
    def decrypt_data(self, encrypted_package):
        """Decrypt data that was encrypted by Ali."""
        # This is a conceptual implementation
        # In a real system, this would use proper cryptographic libraries
        
        try:
            # Extract the encrypted data
            encrypted = encrypted_package.get("encrypted")
            if not encrypted:
                return None
            
            # Simulate decryption
            # In reality, this would use proper decryption algorithms
            decrypted_bytes = base64.b64decode(encrypted)
            decrypted_str = decrypted_bytes.decode()
            
            # Try to parse as JSON if possible
            try:
                return json.loads(decrypted_str)
            except:
                return decrypted_str
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
    
    def set_security_level(self, level):
        """Set the security level for Ali."""
        valid_levels = ["standard", "high", "extreme"]
        if level not in valid_levels:
            logger.error(f"Invalid security level: {level}")
            return False
        
        self.security_level = level
        logger.info(f"Security level set to: {level}")
        self.save_security_data()
        return True
    
    def add_to_blocklist(self, source_id):
        """Add a source to the blocklist."""
        if source_id not in self.blocked_sources:
            self.blocked_sources.append(source_id)
            logger.info(f"Added to blocklist: {source_id}")
            self.save_security_data()
        return True
    
    def remove_from_blocklist(self, source_id):
        """Remove a source from the blocklist."""
        if source_id in self.blocked_sources:
            self.blocked_sources.remove(source_id)
            logger.info(f"Removed from blocklist: {source_id}")
            self.save_security_data()
        return True
    
    def get_security_report(self):
        """Generate a security status report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "security_level": self.security_level,
            "trusted_devices_count": len(self.trusted_devices),
            "blocked_sources_count": len(self.blocked_sources),
            "last_verified": self.last_verified_time.isoformat() if self.last_verified_time else None,
            "verification_window_hours": self.verification_window.total_seconds() / 3600,
            "recent_access_attempts": len(self.access_log[-20:]),  # Last 20 attempts
            "recent_failures": sum(1 for log in self.access_log[-20:] if not log.get("verified", False))
        }
        
        return report
