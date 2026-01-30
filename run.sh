#!/bin/bash
# PROJECT TITAN - Quick Start Script

echo "🦅 PROJECT TITAN - Initializing..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Run TITAN
echo "🚀 Launching TITAN Intelligence System..."
python3 main.py

echo "✅ TITAN cycle complete!"
