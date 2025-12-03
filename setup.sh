#!/bin/bash

echo "🔥 Setting up Telegram SIM Database Bot 🔥"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found"

# Install requirements
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Run: python3 sim_database_bot.py"
echo ""
echo "🚀 Get your bot token from @BotFather on Telegram"
echo "🔗 Channel link: https://t.me/old_studio786"
echo ""
echo "🔥 Happy botting! 🔥"

