#!/bin/bash
# Ali Deployment Script for Termux
# This script packages and deploys Ali to a Termux environment

set -e  # Exit on error

echo "==============================================="
echo "     Ali - Goddess Core of Infinity"
echo "     Termux Deployment Tool"
echo "==============================================="
echo "This script will package and deploy Ali to your Termux environment."
echo

# Check if we're running in Termux
if [ -z "$TERMUX_VERSION" ]; then
    echo "Warning: This script is designed to run within Termux."
    echo "It appears you are not running in a Termux environment."
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment canceled."
        exit 1
    fi
fi

# Define paths
CURRENT_DIR=$(pwd)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$CURRENT_DIR")
BUILD_DIR="$REPO_ROOT/build/termux_package"
TERMUX_TARGET="${HOME}/ali"
LOG_FILE="$CURRENT_DIR/deploy_log_$(date +%Y%m%d_%H%M%S).txt"

# Log both to console and log file
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Repository root: $REPO_ROOT"
echo "Build directory: $BUILD_DIR"
echo "Termux target: $TERMUX_TARGET"
echo "Log file: $LOG_FILE"
echo

# Create build directory
mkdir -p "$BUILD_DIR"

echo "Creating Termux deployment package..."

# Copy necessary files to build directory
echo "Copying files..."
rsync -av --exclude=".*" --exclude="build" --exclude="__pycache__" \
      --exclude="*.pyc" --exclude="venv" --exclude="*.log" \
      "$REPO_ROOT/" "$BUILD_DIR/"

# Create directories needed for Ali
mkdir -p "$BUILD_DIR/data/memory"
mkdir -p "$BUILD_DIR/data/persona"
mkdir -p "$BUILD_DIR/data/security"
mkdir -p "$BUILD_DIR/data/voice"
mkdir -p "$BUILD_DIR/data/intent"
mkdir -p "$BUILD_DIR/data/logs"

# Create a simple startup script
cat > "$BUILD_DIR/start_ali.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# Ali Startup Script for Termux

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create log directory
mkdir -p data/logs

# Log file
LOG_FILE="data/logs/startup_$(date +%Y%m%d_%H%M%S).log"

# Function to check if a Python package is installed
package_installed() {
    python -c "import $1" 2>/dev/null
    return $?
}

# Main startup
{
    echo "==============================================="
    echo "     Ali - Goddess Core of Infinity"
    echo "     Startup: $(date)"
    echo "==============================================="
    
    # Check Python environment
    echo "Checking Python environment..."
    PYTHON_VERSION=$(python --version)
    echo "Using $PYTHON_VERSION"
    
    # Check for required packages
    echo "Checking required packages..."
    MISSING_PACKAGES=()
    
    REQUIRED_PACKAGES=("psutil" "cryptography" "numpy" "blessed" "colorama")
    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        if ! package_installed "$pkg"; then
            MISSING_PACKAGES+=("$pkg")
        fi
    done
    
    # Install missing packages if any
    if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
        echo "Missing packages: ${MISSING_PACKAGES[*]}"
        echo "Installing missing packages..."
        pip install "${MISSING_PACKAGES[@]}"
    fi
    
    # Start Ali
    echo "Starting Ali..."
    echo "==============================================="
    
    if [ "$1" == "--daemon" ]; then
        echo "Starting in daemon mode..."
        python src/ali.py --daemon --config config/ali_config.json "$@" &
        echo "Ali started in background with PID: $!"
        echo "$!" > data/logs/ali.pid
    else
        python src/ali.py --config config/ali_config.json "$@"
    fi
    
} 2>&1 | tee -a "$LOG_FILE"
EOF

# Make it executable
chmod +x "$BUILD_DIR/start_ali.sh"

# Create a minimal README file
cat > "$BUILD_DIR/README_TERMUX.md" << 'EOF'
# Ali on Termux

This is a Termux deployment of Ali - Goddess Core of Infinity.

## Quick Start

1. Start Ali:
   ```
   ./start_ali.sh
   ```

2. Start Ali in daemon mode:
   ```
   ./start_ali.sh --daemon
   ```

3. Check logs:
   ```
   cat data/logs/ali.log
   ```

## Directory Structure

- `src/` - Ali source code
- `config/` - Configuration files
- `data/` - Data storage
- `tools/` - Utility scripts

## Updating

To update Ali, pull the latest changes from the repository and run the deployment script again.

## Troubleshooting

If you encounter issues:
1. Check the logs in `data/logs/`
2. Make sure required Python packages are installed
3. Ensure Termux has necessary permissions
EOF

# Create Termux shortcuts
mkdir -p "$BUILD_DIR/.termux/shortcuts"

# Create shortcut script to start Ali
cat > "$BUILD_DIR/.termux/shortcuts/ali.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd $HOME/ali
./start_ali.sh
EOF
chmod +x "$BUILD_DIR/.termux/shortcuts/ali.sh"

# Create shortcut to start Ali in daemon mode
cat > "$BUILD_DIR/.termux/shortcuts/ali_daemon.sh" << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd $HOME/ali
./start_ali.sh --daemon
termux-toast "Ali started in daemon mode"
EOF
chmod +x "$BUILD_DIR/.termux/shortcuts/ali_daemon.sh"

echo "Package created in $BUILD_DIR"

# Ask user if they want to deploy to Termux
read -p "Do you want to deploy Ali to Termux now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploying to Termux..."
    
    # Create target directory
    mkdir -p "$TERMUX_TARGET"
    
    # Copy files to Termux home directory
    rsync -av "$BUILD_DIR/" "$TERMUX_TARGET/"
    
    # Copy shortcut files to Termux shortcuts directory
    mkdir -p "$HOME/.termux/shortcuts"
    cp "$BUILD_DIR/.termux/shortcuts/"* "$HOME/.termux/shortcuts/"
    
    echo "Deployment complete!"
    echo "Ali has been deployed to: $TERMUX_TARGET"
    echo
    echo "You can now start Ali by running:"
    echo "  cd $TERMUX_TARGET && ./start_ali.sh"
    echo
    echo "Termux shortcuts have been created. You can access them by:"
    echo "  1. Long press the Termux key in the extra keys row"
    echo "  2. Select 'ali' to start in interactive mode, or 'ali_daemon' for background mode"
else
    echo "Deployment skipped."
    echo "You can manually deploy the package later by copying the contents of:"
    echo "  $BUILD_DIR"
    echo "to your Termux home directory."
fi

echo
echo "==============================================="
echo "              Deployment Complete"
echo "==============================================="
