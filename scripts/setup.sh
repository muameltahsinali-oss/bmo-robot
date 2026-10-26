#!/bin/bash
set -e

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# Update System
echo "Updating System..."
sudo apt-get update && sudo apt-get upgrade -y

# Install System Dependencies
echo "Installing Dependencies..."
# Swapped libatlas-base-dev -> libopenblas-dev (better compat)
# Swapped libtiff5 -> libtiff-dev (generic link to correct version)
sudo apt-get install -y python3-pip python3-venv libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportaudio2 libopenblas-dev libopenjp2-7 libtiff-dev
sudo apt-get install -y ffmpeg vlc libvlc-dev

# Create Venv
echo "Creating Virtual Environment..."
python3 -m venv venv --system-site-packages

# Install Python Libs
echo "Installing Python Libraries..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Generate Assets
echo "Generating Face Assets..."
./venv/bin/python scripts/generate_assets.py

echo "Setup Complete! Run ./start.sh to begin."
