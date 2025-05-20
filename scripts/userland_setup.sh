#!/bin/bash
# Ali UserLAnd Setup Script
# This script prepares and launches Ali in a UserLAnd environment

set -e  # Exit on error

echo "==============================================="
echo "     Ali - Goddess Core of Infinity"
echo "     UserLAnd Setup Script"
echo "==============================================="

# Function to log messages with timestamps
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if we're in UserLAnd
check_userland() {
    if ! env | grep -q "USERLAND"; then
        log "Warning: This script is designed for UserLAnd."
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Setup canceled."
            exit 1
        fi
    fi
}

# Function to install system dependencies
install_system_deps() {
    log "Updating system package list..."
    sudo apt-get update

    log "Installing system dependencies..."
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
}

# Function to set up Python environment
setup_python() {
    log "Setting up Python environment..."
    
    # Update pip
    python3 -m pip install --upgrade pip
    
    # Install core Python packages
    pip3 install --upgrade \
        wheel \
        setuptools \
        cryptography \
        psutil \
        blessed \
        colorama \
        numpy \
        requests
}

# Function to clone/update Ali repository
setup_ali() {
    local install_dir="$HOME/ali"
    
    if [ -d "$install_dir/.git" ]; then
        log "Updating existing Ali installation..."
        cd "$install_dir"
        git pull
    else
        log "Cloning Ali repository..."
        git clone https://github.com/yourusername/ali-core.git "$install_dir"
        cd "$install_dir"
    fi
}

# Function to create systemd service for Ali
create_service() {
    log "Creating systemd service for Ali..."
    
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

    sudo systemctl daemon-reload
    sudo systemctl enable ali.service
}

# Function to create convenient aliases
create_aliases() {
    log "Creating convenient aliases..."
    
    # Add aliases to .bashrc if they don't exist
    if ! grep -q "# Ali aliases" ~/.bashrc; then
        cat >> ~/.bashrc << 'EOL'

# Ali aliases
alias ali='cd ~/ali && python3 src/ali.py --config config/ali_config.json'
alias ali-start='sudo systemctl start ali'
alias ali-stop='sudo systemctl stop ali'
alias ali-status='sudo systemctl status ali'
alias ali-logs='tail -f ~/ali/data/logs/ali.log'
EOL
    fi
    
    # Create a simple launch script
    cat > ~/ali/run_ali.sh << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
python3 src/ali.py --config config/ali_config.json "$@"
EOL
    chmod +x ~/ali/run_ali.sh
}

# Function to perform first-time setup
setup_first_time() {
    log "Performing first-time setup..."
    
    cd ~/ali
    
    # Create data directories
    mkdir -p data/{memory,persona,security,voice,intent,logs}
    
    # Run dependency checker
    python3 tools/dependency_checker.py --fix
    
    # Run setup script
    python3 setup.py --install
}

# Function to check and fix common issues
fix_common_issues() {
    log "Checking for common issues..."
    
    # Fix permissions
    sudo chown -R $USER:$USER ~/ali
    
    # Fix Python command if needed
    if ! command -v python >/dev/null; then
        sudo ln -s $(which python3) /usr/local/bin/python
    fi
    
    # Fix pip command if needed
    if ! command -v pip >/dev/null; then
        sudo ln -s $(which pip3) /usr/local/bin/pip
    fi
}

# Main execution
main() {
    log "Starting Ali setup for UserLAnd..."
    
    # Check if running in UserLAnd
    check_userland
    
    # Install system dependencies
    install_system_deps
    
    # Set up Python
    setup_python
    
    # Set up Ali
    setup_ali
    
    # Create service
    create_service
    
    # Create aliases
    create_aliases
    
    # Perform first-time setup
    setup_first_time
    
    # Fix common issues
    fix_common_issues
    
    log "Setup complete!"
    echo
    echo "You can now start Ali in several ways:"
    echo "1. Interactive mode: ali"
    echo "2. Daemon mode: ali-start"
    echo "3. Run script: ~/ali/run_ali.sh"
    echo
    echo "Other useful commands:"
    echo "- Check status: ali-status"
    echo "- View logs: ali-logs"
    echo "- Stop service: ali-stop"
    echo
    echo "Please source your .bashrc or restart your shell to use the aliases:"
    echo "source ~/.bashrc"
}

# Run main function
main "$@" 2>&1 | tee ~/ali_setup_$(date +%Y%m%d_%H%M%S).log

