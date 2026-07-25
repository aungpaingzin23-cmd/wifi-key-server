#!/bin/bash
# WiFi Bypass Key System - Start Script
# Run this in Termux to start both Key Server and Telegram Bot

echo "============================================"
echo "  WiFi Bypass Key System"
echo "  Starting Key Server + Telegram Bot"
echo "============================================"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "[+] Installing Flask..."
    pip install flask
fi

# Check if pyTelegramBotAPI is installed
if ! python3 -c "import telebot" 2>/dev/null; then
    echo "[+] Installing pyTelegramBotAPI..."
    pip install pyTelegramBotAPI
fi

# Create data directory
mkdir -p ~/key_data

echo ""
echo "[1/2] Starting Key Server..."
python3 "$(dirname "$0")/key_server.py" &
SERVER_PID=$!
echo "[+] Key Server PID: $SERVER_PID"

# Wait for server to start
sleep 3

echo "[2/2] Starting Telegram Bot..."
python3 "$(dirname "$0")/key_bot.py" &
BOT_PID=$!
echo "[+] Telegram Bot PID: $BOT_PID"

echo ""
echo "============================================"
echo "  System Running!"
echo "  Server: http://localhost:2060"
echo "  Server PID: $SERVER_PID"
echo "  Bot PID: $BOT_PID"
echo "  Press Ctrl+C to stop"
echo "============================================"

# Handle cleanup
trap "kill $SERVER_PID $BOT_PID 2>/dev/null; echo '[!] Stopped.'; exit" INT TERM

wait
