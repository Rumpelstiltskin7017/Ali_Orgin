#!/bin/bash
# Ali One-Click UserLAnd Installation Script
# Simply copy and paste this entire script into your UserLAnd terminal

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored status messages
status() {
    echo -e "${GREEN}[*]${NC} $1"
}

error() {
    echo -e "${RED}[!]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Display welcome banner
cat << "EOF"
===============================================
    Ali - Goddess Core of Infinity
    One-Click UserLAnd Installation
===============================================
EOF

# Check if running in UserLAnd
if ! env | grep -q "USERLAND"; then
    warn "This script is designed for UserLAnd."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Installation canceled."
        exit 1
    fi
fi

# Function to handle errors
handle_error() {
    error "An error occurred on line $1"
    error "Installation failed. Please check the error message above."
    exit 1
}

# Set up error handling
trap 'handle_error $LINENO' ERR

# Update package list
status "Updating package list..."
sudo apt-get update

# Install basic requirements
status "Installing basic requirements..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev

# Upgrade pip
status "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install Python dependencies
status "Installing Python dependencies..."
pip3 install --upgrade \
    wheel \
    setuptools \
    psutil \
    cryptography \
    blessed \
    colorama \
    numpy \
    requests

# Clone Ali repository
status "Cloning Ali repository..."
if [ -d "$HOME/ali" ]; then
    warn "Ali directory already exists. Updating..."
    cd "$HOME/ali"
    git pull
else
    git clone https://github.com/yourusername/ali-core.git "$HOME/ali"
    cd "$HOME/ali"
fi

# Create necessary directories
status "Creating data directories..."
mkdir -p data/{memory,persona,security,voice,intent,logs}

# Run setup script
status "Running Ali setup..."
python3 setup.py --install

# Fix permissions
status "Fixing permissions..."
sudo chown -R $USER:$USER "$HOME/ali"
find "$HOME/ali" -type f -name "*.sh" -exec chmod +x {} \;
find "$HOME/ali" -type f -name "*.py" -exec chmod +x {} \;

# Create systemd service
status "Creating systemd service..."
sudo tee /etc/systemd/system/ali.service > /dev/null << EOL
[Unit]
Description=Ali - Goddess Core of Infinity
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/ali
ExecStart=/usr/bin/python3 src/ali.py --daemon --config config/ali_config.json
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable ali.service

# Create convenient command aliases
status "Creating command aliases..."
cat >> "$HOME/.bashrc" << 'EOL'

# Ali command aliases
alias ali='cd ~/ali && python3 src/ali.py --config config/ali_config.json'
alias ali-start='sudo systemctl start ali'
alias ali-stop='sudo systemctl stop ali'
alias ali-status='sudo systemctl status ali'
alias ali-logs='tail -f ~/ali/data/logs/ali.log'
alias ali-update='cd ~/ali && git pull && python3 setup.py --update'
EOL

# Create quick launch script
status "Creating quick launch script..."
cat > "$HOME/ali/run_ali.sh" << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
python3 src/ali.py --config config/ali_config.json "$@"
EOL
chmod +x "$HOME/ali/run_ali.sh"

# Run post-setup script
status "Running post-setup checks..."
python3 scripts/userland_post_setup.py

# Final instructions
cat << "EOF"

===============================================
    Installation Complete!
===============================================

To start using Ali, you have several options:

1. Interactive mode:
   ali

2. Service mode:
   ali-start

3. Quick launch:
   ~/ali/run_ali.sh

Other useful commands:
- ali-status  : Check service status
- ali-logs    : View logs
- ali-stop    : Stop service
- ali-update  : Update Ali

Note: You need to either restart your terminal
or run 'source ~/.bashrc' to use the aliases.

For more information, see:
- ~/ali/QUICK_START.md
- ~/ali/docs/user_guide.md

Enjoy your interaction with Ali!
===============================================
EOF

# Source bashrc to enable aliases immediately
source "$HOME/.bashrc"

# Final status
status "Installation completed successfully!"
