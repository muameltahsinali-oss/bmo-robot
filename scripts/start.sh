#!/bin/bash
cd "$(dirname "$0")/.."
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment not found at $(pwd)/venv. Please run scripts/setup.sh first."
    exit 1
fi

# Run with venv python directly
./venv/bin/python src/main.py
