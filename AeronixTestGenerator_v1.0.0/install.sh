#!/bin/bash
# Aeronix Test Generator Installation Script

echo "Installing Aeronix Test Generator v1.0.0"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$python_version" ]]; then
    echo "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python $python_version found"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Create desktop shortcut (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    cat > ~/Desktop/AeronixTestGenerator.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Aeronix Test Generator
Comment=PCB Test Plan Generator
Exec=python3 $(pwd)/UI.py
Icon=applications-engineering
Terminal=false
Categories=Development;Engineering;
EOF
    chmod +x ~/Desktop/AeronixTestGenerator.desktop
    echo "Desktop shortcut created"
fi

echo "Installation complete!"
echo "Run: python3 UI.py"
