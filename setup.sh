#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "==========================================="
echo "       KernHell - Linux/macOS Setup"
echo "==========================================="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed."
    echo "Please install Python 3 using your package manager (e.g., apt, brew)."
    exit 1
fi

# Install the Package
# We try to install globally or to user space
echo "[INFO] Installing KernHell..."
if pip install .; then
    echo "[SUCCESS] Installed via pip."
else
    echo "[WARNING] Standard install failed (likely permission or externally-managed environment)."
    echo "[INFO] Trying with --break-system-packages (for newer Linux distros) or sudo..."
    
    # Try with --break-system-packages if available (handling PEP 668)
    if pip install . --break-system-packages 2>/dev/null; then
         echo "[SUCCESS] Installed with --break-system-packages."
    else
         echo "[ERROR] Installation failed. Please run this script with 'sudo' or check your python environment."
         exit 1
    fi
fi

# Install Playwright Browsers
echo "[INFO] Installing Playwright browsers..."
playwright install

echo ""
echo "==========================================="
echo "[SUCCESS] KernHell installed successfully!"
echo ""
echo "Usage:"
echo "  kernhell --help"
echo "  kernhell heal <script.py>"
echo ""
echo "Setup API Key:"
echo "  export GEMINI_API_KEY='your_key'"
echo "  (Add this to your ~/.bashrc or ~/.zshrc to make it permanent)"
echo "==========================================="
