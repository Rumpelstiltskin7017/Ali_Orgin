#!/data/data/com.termux/files/usr/bin/bash
# Ali Termux Startup Script
# This script starts the Ali system on Termux and sets up necessary permissions

echo "==============================================="
echo "     Ali - Goddess Core of Infinity"
echo "     Termux Boot Script"
echo "==============================================="
echo "Starting at: $(date)"
echo

# Define paths
ALI_HOME="$HOME/ali-core"
ALI_CONFIG="$ALI_HOME/config/ali_config.json"
LOG_FILE="$HOME/ali_logs/ali_startup_$(date +%Y%m%d_%H%M%S).log"
TERMUX_DATA_DIR="$HOME/.termux/ali_data"

# Create log directory if it doesn't exist
mkdir -p "$HOME/ali_logs"
mkdir -p "$TERMUX_DATA_DIR"

# Redirect all output to log file
exec > >(tee -a "$LOG_FILE") 2>&1

# Function to check if a package is installed
package_installed() {
    pkg list-installed | grep -q "^$1"
    return $?
}

# Check and install required packages
echo "Checking required packages..."
required_packages=("python" "termux-api" "git" "openssh")

for package in "${required_packages[@]}"; do
    if ! package_installed "$package"; then
        echo "Installing $package..."
        pkg install -y "$package"
    else
        echo "$package already installed."
    fi
done

# Navigate to Ali directory
echo "Navigating to Ali directory..."
if [ ! -d "$ALI_HOME" ]; then
    echo "Ali directory not found at $ALI_HOME"
    echo "Attempting to clone repository..."
    
    git clone https://github.com/yourusername/ali-core.git "$ALI_HOME"
    if [ ! -d "$ALI_HOME" ]; then
        echo "Failed to clone Ali repository. Exiting."
        exit 1
    fi
fi

cd "$ALI_HOME"
echo "Current directory: $(pwd)"

# Check for updates
echo "Checking for updates..."
git pull

# Ensure data directories exist
echo "Ensuring data directories exist..."
mkdir -p data/memory data/persona data/security data/voice data/intent data/logs

# Check if config exists
if [ ! -f "$ALI_CONFIG" ]; then
    echo "Configuration file not found. Creating default configuration..."
    mkdir -p config
    echo '{
        "system": {
            "auto_backup": true,
            "backup_interval_hours": 24,
            "monitor_interval_seconds": 300
        },
        "security": {
            "security_level": "high"
        },
        "voice": {
            "enable_voice": true,
            "voice_profile": "goddess"
        }
    }' > "$ALI_CONFIG"
fi

# Check for Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating Python virtual environment..."
source venv/bin/activate

# Install or update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Request necessary permissions
echo "Requesting necessary permissions..."
if command -v termux-notification &> /dev/null; then
    echo "Setting up notification listener..."
    termux-notification-list > /dev/null
fi

if command -v termux-location &> /dev/null; then
    echo "Testing location access..."
    termux-location -p network > /dev/null
fi

if command -v termux-microphone-record &> /dev/null; then
    echo "Testing microphone access..."
    termux-microphone-record -d 1 -f "$TERMUX_DATA_DIR/test.m4a" > /dev/null
    rm -f "$TERMUX_DATA_DIR/test.m4a"
fi

# Set environment variables
export ALI_USER="MasterChief"
export ALI_DATA_DIR="$HOME/ali_data"
export ALI_CONFIG_FILE="$ALI_CONFIG"

# Start Ali
echo "Starting Ali system..."
echo "---------------------------------------------"

if [ "$1" == "--daemon" ]; then
    echo "Starting in daemon mode..."
    python src/ali.py --daemon --config "$ALI_CONFIG" --user "$ALI_USER" > "$HOME/ali_logs/ali_output.log" 2>&1 &
    echo "Ali started in background. Check $HOME/ali_logs/ali_output.log for output."
    echo "Process ID: $!"
    echo "$!" > "$HOME/ali_logs/ali.pid"
else
    echo "Starting in interactive mode..."
    python src/ali.py --config "$ALI_CONFIG" --user "$ALI_USER"
fi

echo "---------------------------------------------"
echo "Ali startup script completed at: $(date)"
echo
