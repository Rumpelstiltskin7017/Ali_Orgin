#!/usr/bin/env python3
"""
Ali Dependency Checker

This script checks if all required dependencies for Ali are installed
and provides guidance on how to install missing components.
"""

import os
import sys
import platform
import subprocess
import argparse
import importlib.util
from termcolor import colored
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger("Ali.DependencyChecker")

# Define required dependencies
CORE_DEPENDENCIES = [
    ("psutil", "System monitoring", "pip install psutil"),
    ("cryptography", "Encryption and security", "pip install cryptography"),
    ("blessed", "Terminal UI toolkit", "pip install blessed"),
    ("colorama", "Terminal colors", "pip install colorama"),
]

RECOMMENDED_DEPENDENCIES = [
    ("numpy", "Numerical processing", "pip install numpy"),
    ("matplotlib", "Data visualization", "pip install matplotlib"),
    ("nltk", "Natural language toolkit", "pip install nltk"),
    ("bcrypt", "Password hashing", "pip install bcrypt"),
]

OPTIONAL_DEPENDENCIES = [
    ("requests", "HTTP requests", "pip install requests"),
    ("websockets", "WebSocket support", "pip install websockets"),
    ("pandas", "Data analysis", "pip install pandas"),
    ("scikit-learn", "Machine learning toolkit", "pip install scikit-learn"),
    ("sqlalchemy", "SQL toolkit and ORM", "pip install sqlalchemy"),
]

TERMUX_SPECIFIC = [
    ("termux-api", "Termux API access", "pkg install termux-api"),
]

def check_python_version():
    """Check if the Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        return True, f"Python {current_version[0]}.{current_version[1]}"
    else:
        return False, f"Python {current_version[0]}.{current_version[1]} (required: {required_version[0]}.{required_version[1]}+)"

def check_pip():
    """Check if pip is installed and working."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "pip command failed"
    except Exception as e:
        return False, f"Error checking pip: {e}"

def check_package(package_name):
    """Check if a Python package is installed."""
    spec = importlib.util.find_spec(package_name)
    if spec is not None:
        try:
            # Try to get version if possible
            module = importlib.import_module(package_name)
            version = getattr(module, "__version__", "unknown version")
            return True, version
        except (ImportError, AttributeError):
            return True, "unknown version"
    return False, "not installed"

def check_termux():
    """Check if running in Termux environment."""
    return 'TERMUX_VERSION' in os.environ, os.environ.get('TERMUX_VERSION', 'Not Termux')

def check_termux_api():
    """Check if Termux API is installed."""
    is_termux, _ = check_termux()
    if not is_termux:
        return False, "Not a Termux environment"
    
    try:
        result = subprocess.run(
            ["pkg", "list-installed", "termux-api"],
            capture_output=True,
            text=True
        )
        if "termux-api" in result.stdout:
            return True, "installed"
        else:
            return False, "not installed"
    except Exception:
        return False, "error checking"

def check_system_resources():
    """Check available system resources."""
    results = {}
    
    # Check CPU
    try:
        import psutil
        cpu_count = psutil.cpu_count(logical=True)
        cpu_physical = psutil.cpu_count(logical=False)
        results["cpu"] = {
            "status": True,
            "message": f"{cpu_physical} physical cores, {cpu_count} logical cores"
        }
    except ImportError:
        results["cpu"] = {
            "status": "unknown",
            "message": "psutil not available to check CPU"
        }
    
    # Check memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024 * 1024 * 1024)
        memory_status = memory_gb >= 2  # Minimum 2GB recommended
        results["memory"] = {
            "status": memory_status,
            "message": f"{memory_gb:.1f} GB RAM"
        }
    except ImportError:
        results["memory"] = {
            "status": "unknown",
            "message": "psutil not available to check memory"
        }
    
    # Check disk space
    try:
        import psutil
        disk = psutil.disk_usage(os.path.expanduser("~"))
        disk_gb = disk.free / (1024 * 1024 * 1024)
        disk_status = disk_gb >= 1  # Minimum 1GB free recommended
        results["disk"] = {
            "status": disk_status,
            "message": f"{disk_gb:.1f} GB free disk space"
        }
    except ImportError:
        results["disk"] = {
            "status": "unknown",
            "message": "psutil not available to check disk"
        }
    
    return results

def check_ali_directory_structure(ali_dir):
    """Check if the Ali directory structure is correct."""
    ali_path = Path(ali_dir)
    
    required_dirs = [
        "src",
        "src/ali_core",
        "config",
        "data",
        "data/memory",
        "data/persona",
        "data/security",
        "data/voice",
        "data/intent",
        "data/logs"
    ]
    
    required_files = [
        "src/ali.py",
        "src/ali_core/__init__.py",
        "src/ali_core/core.py",
        "src/ali_core/interface.py",
        "src/ali_core/persona.py",
        "src/ali_core/security.py",
        "src/ali_core/system.py",
        "src/ali_core/voice.py",
        "src/ali_core/intent.py",
        "config/ali_config.json"
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        if not (ali_path / dir_path).exists():
            missing_dirs.append(dir_path)
    
    for file_path in required_files:
        if not (ali_path / file_path).exists():
            missing_files.append(file_path)
    
    return missing_dirs, missing_files

def check_config_file(ali_dir):
    """Check if the configuration file exists and is valid."""
    config_path = Path(ali_dir) / "config" / "ali_config.json"
    
    if not config_path.exists():
        return False, "Configuration file not found"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check basic config structure
        required_sections = ["system", "security", "voice", "persona"]
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            return False, f"Missing configuration sections: {', '.join(missing_sections)}"
        
        return True, "Configuration file is valid"
    except json.JSONDecodeError:
        return False, "Configuration file contains invalid JSON"
    except Exception as e:
        return False, f"Error reading configuration file: {e}"

def print_colored(message, status):
    """Print a colorized status message."""
    if status is True:
        print(colored("✓ ", "green") + message)
    elif status is False:
        print(colored("✗ ", "red") + message)
    else:
        print(colored("? ", "yellow") + message)

def main():
    """Main function for the dependency checker."""
    parser = argparse.ArgumentParser(description="Ali Dependency Checker")
    parser.add_argument("--ali-dir", default=".", help="Ali installation directory")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix missing dependencies")
    args = parser.parse_args()
    
    # Prepare results
    results = {
        "system": {},
        "python": {},
        "core_dependencies": {},
        "recommended_dependencies": {},
        "optional_dependencies": {},
        "termux_specific": {},
        "ali_installation": {}
    }
    
    # Show nice header if not in JSON mode
    if not args.json:
        print("\n" + "="*70)
        print(" Ali Dependency Checker ".center(70, "="))
        print("="*70 + "\n")
    
    # Check system environment
    if not args.json:
        print(colored("System Environment", "cyan", attrs=["bold"]))
        print("-" * 70)
    
    system_info = platform.system()
    is_termux, termux_version = check_termux()
    
    results["system"]["platform"] = {
        "status": True,
        "message": system_info
    }
    
    results["system"]["termux"] = {
        "status": is_termux,
        "message": termux_version if is_termux else "Not Termux"
    }
    
    if not args.json:
        print_colored(f"Platform: {system_info}", True)
        print_colored(f"Termux: {termux_version if is_termux else 'Not Termux'}", is_termux)
    
    # Check Python environment
    if not args.json:
        print("\n" + colored("Python Environment", "cyan", attrs=["bold"]))
        print("-" * 70)
    
    # Check Python version
    python_status, python_message = check_python_version()
    results["python"]["version"] = {
        "status": python_status,
        "message": python_message
    }
    
    if not args.json:
        print_colored(f"Python version: {python_message}", python_status)
    
    # Check pip
    pip_status, pip_message = check_pip()
    results["python"]["pip"] = {
        "status": pip_status,
        "message": pip_message
    }
    
    if not args.json:
        print_colored(f"Pip: {pip_message}", pip_status)
    
    # Check core dependencies
    if not args.json:
        print("\n" + colored("Core Dependencies", "cyan", attrs=["bold"]))
        print("-" * 70)
    
    missing_core = []
    
    for package, description, install_cmd in CORE_DEPENDENCIES:
        status, version = check_package(package)
        results["core_dependencies"][package] = {
            "status": status,
            "message": version,
            "description": description,
            "install_command": install_cmd
        }
        
        if not args.json:
            print_colored(f"{package}: {version} - {description}", status)
        
        if not status:
            missing_core.append((package, install_cmd))
    
    # Check recommended dependencies
    if not args.json:
        print("\n" + colored("Recommended Dependencies", "cyan", attrs=["bold"]))
        print("-" * 70)
    
    missing_recommended = []
    
    for package, description, install_cmd in RECOMMENDED_DEPENDENCIES:
        status, version = check_package(package)
        results["recommended_dependencies"][package] = {
            "status": status,
            "message": version,
            "description": description,
            "install_command": install_cmd
        }
        
        if not args.json:
            print_colored(f"{package}: {version} - {description}", status)
        
        if not status:
            missing_recommended.append((package, install_cmd))
    
    # Check optional dependencies
    if not args.json:
        print("\n" + colored("Optional Dependencies", "cyan", attrs=["bold"]))
        print("-" * 70)
    
    for package, description, install_cmd in OPTIONAL_DEPENDENCIES:
        status, version = check_package(package)
        results["optional_dependencies"][package] = {
            "status": status,
            "message": version,
            "description": description,
            "install_command": install_cmd
        }
        
        if not args.json:
            print_colored(f"{package}: {version} - {description}", status)
    
    # Check Termux-specific dependencies
    if is_termux:
        if not args.json:
            print("\n" + colored("Termux-Specific Dependencies", "cyan", attrs=["bold"]))
            print("-" * 70)
        
        missing_termux = []
        
        for package, description, install_cmd in TERMUX_SPECIFIC:
            if package == "termux-api":
                status, version = check_termux_api()
            else:
                status, version = False, "not checked"
            
            results["termux_specific"][package] = {
                "status": status,
                "message": version,
                "description": description,
                "install_command": install_cmd
            }
            
            if not args.json:
                print_colored(f"{package}: {version} - {description}", status)
            
            if not status:
                missing_termux.append((package, install_cmd))
    
    # Check system resources
    if not args.json:
        print("\n" + colored("System Resources", "cyan", attrs=["bold"]))
        print("-" * 70)
    
    resources = check_system_resources()
    results["system"]["resources"] = resources
    
    if not args.json:
        for resource, info in resources.items():
            print_colored(f"{resource.capitalize()}: {info['message']}", info['status'])
    
    # Check Ali installation
    if not args.json:
        print("\n" + colored("Ali Installation", "cyan", attrs=["bold"]))
        print("-" * 70)
    
    # Check directory structure
    missing_dirs, missing_files = check_ali_directory_structure(args.ali_dir)
    
    if missing_dirs or missing_files:
        dir_status = False
        if not args.json:
            print_colored("Ali directory structure: Incomplete", False)
            if missing_dirs:
                print("  Missing directories:")
                for dir_path in missing_dirs:
                    print(f"  - {dir_path}")
            if missing_files:
                print("  Missing files:")
                for file_path in missing_files:
                    print(f"  - {file_path}")
    else:
        dir_status = True
        if not args.json:
            print_colored("Ali directory structure: Complete", True)
    
    results["ali_installation"]["directory_structure"] = {
        "status": dir_status,
        "missing_dirs": missing_dirs,
        "missing_files": missing_files
    }
    
    # Check configuration
    config_status, config_message = check_config_file(args.ali_dir)
    results["ali_installation"]["configuration"] = {
        "status": config_status,
        "message": config_message
    }
    
    if not args.json:
        print_colored(f"Configuration: {config_message}", config_status)
    
    # Install missing dependencies if requested
    if args.fix and (missing_core or missing_recommended or (is_termux and missing_termux)):
        if not args.json:
            print("\n" + colored("Installing Missing Dependencies", "cyan", attrs=["bold"]))
            print("-" * 70)
        
        # Install core dependencies
        for package, install_cmd in missing_core:
            if not args.json:
                print(f"Installing {package}...")
            try:
                if install_cmd.startswith("pip "):
                    cmd = [sys.executable, "-m"] + install_cmd.split()
                else:
                    cmd = install_cmd.split()
                subprocess.run(cmd, check=True)
                if not args.json:
                    print(colored(f"Successfully installed {package}", "green"))
            except Exception as e:
                if not args.json:
                    print(colored(f"Failed to install {package}: {e}", "red"))
        
        # Install recommended dependencies
        for package, install_cmd in missing_recommended:
            if not args.json:
                print(f"Installing {package}...")
            try:
                if install_cmd.startswith("pip "):
                    cmd = [sys.executable, "-m"] + install_cmd.split()
                else:
                    cmd = install_cmd.split()
                subprocess.run(cmd, check=True)
                if not args.json:
                    print(colored(f"Successfully installed {package}", "green"))
            except Exception as e:
                if not args.json:
                    print(colored(f"Failed to install {package}: {e}", "red"))
        
        # Install Termux-specific dependencies
        if is_termux:
            for package, install_cmd in missing_termux:
                if not args.json:
                    print(f"Installing {package}...")
                try:
                    subprocess.run(install_cmd.split(), check=True)
                    if not args.json:
                        print(colored(f"Successfully installed {package}", "green"))
                except Exception as e:
                    if not args.json:
                        print(colored(f"Failed to install {package}: {e}", "red"))
    
    # Output JSON if requested
    if args.json:
        print(json.dumps(results, indent=2))
        return
    
    # Summary
    print("\n" + colored("Summary", "cyan", attrs=["bold"]))
    print("-" * 70)
    
    core_status = all(results["core_dependencies"][package]["status"] for package, _, _ in CORE_DEPENDENCIES)
    recommended_status = all(results["recommended_dependencies"][package]["status"] for package, _, _ in RECOMMENDED_DEPENDENCIES)
    
    if is_termux:
        termux_status = all(results["termux_specific"][package]["status"] for package, _, _ in TERMUX_SPECIFIC)
    else:
        termux_status = True  # Not applicable
    
    ali_status = results["ali_installation"]["directory_structure"]["status"] and results["ali_installation"]["configuration"]["status"]
    
    print_colored("Core dependencies: " + ("All installed" if core_status else "Missing some"), core_status)
    print_colored("Recommended dependencies: " + ("All installed" if recommended_status else "Missing some"), recommended_status)
    if is_termux:
        print_colored("Termux-specific dependencies: " + ("All installed" if termux_status else "Missing some"), termux_status)
    print_colored("Ali installation: " + ("Complete" if ali_status else "Incomplete"), ali_status)
    
    overall_status = core_status and python_status and ali_status
    
    print("\n" + "="*70)
    if overall_status:
        print(colored("  Ali is ready to run! All core requirements are satisfied.  ", "green", attrs=["bold"]))
    else:
        print(colored("  Some requirements are missing. Ali may not work correctly.  ", "yellow", attrs=["bold"]))
        
        if not core_status:
            print("\nTo install missing core dependencies:")
            for package, install_cmd in missing_core:
                print(f"  {install_cmd}")
        
        if not ali_status:
            print("\nTo fix the Ali installation:")
            if missing_dirs:
                print("  Create the missing directories:")
                for dir_path in missing_dirs:
                    print(f"  mkdir -p {os.path.join(args.ali_dir, dir_path)}")
            if missing_files:
                print("  Create the missing files or reinstall Ali")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        from termcolor import colored
    except ImportError:
        # Simple fallback if termcolor is not available
        def colored(text, *args, **kwargs):
            return text
    
    main()
