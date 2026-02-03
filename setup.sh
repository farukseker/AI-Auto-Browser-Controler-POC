#!/bin/bash
# Setup script for AI Selenium Automation

set -e

echo "=============================================="
echo "AI Selenium Automation - Setup Script"
echo "=============================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✓ Python $python_version detected"
else
    echo "✗ Python 3.8+ required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p screenshots
mkdir -p logs
echo "✓ Directories created"

# Copy environment template
echo ""
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "✓ Created .env file (please edit with your API key)"
else
    echo "✓ .env file already exists"
fi

# Check Chrome installation
echo ""
echo "Checking Chrome installation..."
if command -v google-chrome &> /dev/null; then
    chrome_version=$(google-chrome --version)
    echo "✓ $chrome_version"
elif command -v chromium &> /dev/null; then
    chromium_version=$(chromium --version)
    echo "✓ $chromium_version"
else
    echo "⚠ Chrome/Chromium not found"
    echo "  Install Chrome: https://www.google.com/chrome/"
fi

# Install ChromeDriver
echo ""
echo "ChromeDriver will be managed automatically by webdriver-manager"
echo "✓ Setup complete"

echo ""
echo "=============================================="
echo "Next Steps:"
echo "=============================================="
echo ""
echo "1. Edit .env file with your OpenRouter API key:"
echo "   nano .env"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the application:"
echo "   python main.py                  # Interactive mode"
echo "   python main.py --demo           # Demo mode"
echo "   python main.py --task 'Go to google.com'"
echo ""
echo "4. For help:"
echo "   python main.py --help"
echo ""
