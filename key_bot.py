#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi Bypass Key Telegram Bot - FIXED VERSION
"""

import os
import time
import json
import requests
import hashlib
from datetime import datetime

try:
    import telebot
except ImportError:
    os.system("pip install pyTelegramBotAPI")
    import telebot

# ---------- CONFIG ----------
BOT_TOKEN = "8972355563:AAGKhjO1Ly0QCIG2jcxFizfMKN4sbYfblDc"
ADMIN_ID = "8363372270"
SERVER_URL = "https://wifi-key-server.onrender.com"
API_KEY = "w1f1k3y2026"

DURATION_OPTIONS = {"1d": 1, "3d": 3, "7d": 7, "14d": 14, "30d": 30}

bot = telebot.TeleBot(BOT_TOKEN)

def is_admin(uid):
    return str(uid) == str(ADMIN_ID)

def server_req(endpoint, method="GET", data=None):
    if data is None:
        data = {}
    data["api_key"] = API_KEY
    try:
        if method == "GET":
            r = requests.get(f"{SERVER_URL}{endpoint}", params=data, timeout=10)
        else:
            r = requests.post(f"{SERVER_URL}{endpoint}", json=data, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ---------- BOT HANDLERS ----------

@bot.message_handler(commands=["start"])
def cmd_start(msg):
    if is_admin(msg.from_user.id):
        text = (
            "🔑 *WiFi Bypass Key Bot*\n"
            "━━━━━━━━━━━━━━━━━\n"
            "📌 *Admin Commands:*\n"
            "/add <device_id> <duration> — Register key\n"
            "/remove <device_id> — Remove key\n"
            "/extend <device_id> <days> — Extend key\n"
            "/list — List all keys\n"
            "/info <device_id> — Check device\n"
            "/status — Server status\n"
            "/help — Show help\n"
            "━━━━━━━━━━━━━━━━━\n"
            f"👤 Admin ID: `{ADMIN_ID}`\n"
        )
    else:
        text = (
            "🔑 *WiFi Bypass Key System*\n"
            "━━━━━━━━━━━━━━━━━\n"
            "/mykey — Show your Device ID\n"
            "/status — Check server\n"
            "/help — Show help\n"
            "━━━━━━━━━━━━━━━━━\n"
            "⚠️ Contact admin for key.\n"
        )
    bot.reply_to(msg, text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def cmd_help(msg):
    if is_admin(msg.from_user.id):
        text = (
            "🔑 *Admin Help*\n\n"
            "➕ `/add DEV-XXXXX 7` — 7 days\n"
            "➕ `/add DEV-XXXXX 1d` or `7d` or `30d`\n"
            "❌ `/remove DEV-XXXXX`\n"
            "🔄 `/extend DEV-XXXXX 7`\n"
            "📋 `/list` — All keys\n"
            "ℹ️ `/info DEV-XXXXX` — Device info\n"
            "📊 `/status` — Server health\n"
        )
    else:
        text = (
            "🔑 *User Help*\n\n"
            "🆔 `/mykey` — Your Device ID\n"
            "📊 `/status` — Server status\n"
            "💬 Contact admin for key."
        )
    bot.reply_to(msg, text, parse_mode="Markdown")


@bot.message_handler(commands=["add"])
def cmd_add(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Admin only!")
        return
    args = msg.text.split()[1:] if len(msg.text.split()) > 1 else []
    if len(args) < 2:
        bot.reply_to(msg, "⚠️ Usage: /add <device_id> <duration>\nExample: /add DEV-ABC123 7")
        return
    device_id = args[0].upper().strip()
    duration_str = args[1].lower()
    if duration_str in DURATION_OPTIONS:
        days = DURATION_OPTIONS[duration_str]
    else:
        try:
            days = int(duration_str)
        except:
            bot.reply_to(msg, f"⚠️ Invalid duration. Use: {', '.join(DURATION_OPTIONS.keys())}")
            return
    result = server_req("/api/register", method="POST", data={
        "device_id": device_id, "duration_days": days
    })
    if result.get("success"):
        text = (
            f"✅ *Key Registered!*\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"🆔 Device: `{device_id}`\n"
            f"⏳ Duration: {days} days\n"
            f"📅 Expires: {result.get('expiry', '?')}\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"Send this Device ID to the user."
        )
    else:
        text = f"❌ Failed: {result.get('error', 'Unknown')}"
    bot.reply_to(msg, text, parse_mode="Markdown")


@bot.message_handler(commands=["remove"])
def cmd_remove(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Admin only!")
        return
    args = msg.text.split()[1:]
    if not args:
        bot.reply_to(msg, "⚠️ Usage: /remove <device_id>")
        return
    device_id = args[0].upper().strip()
    result = server_req("/api/remove", method="POST", data={"device_id": device_id})
    if result.get("success"):
        bot.reply_to(msg, f"❌ Removed: `{device_id}`")
    else:
        bot.reply_to(msg, f"❌ Failed: {result.get('error', 'Unknown')}")


@bot.message_handler(commands=["extend"])
def cmd_extend(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Admin only!")
        return
    args = msg.text.split()[1:]
    if len(args) < 2:
        bot.reply_to(msg, "⚠️ Usage: /extend <device_id> <days>")
        return
    device_id = args[0].upper().strip()
    try:
        days = int(args[1])
    except:
        bot.reply_to(msg, "⚠️ Invalid days.")
        return
    result = server_req("/api/extend", method="POST", data={
        "device_id": device_id, "duration_days": days
    })
    if result.get("success"):
        bot.reply_to(msg, f"🔄 Extended `{device_id}` by {days} days\nNew expiry: {result.get('expiry', '?')}")
    else:
        bot.reply_to(msg, f"❌ Failed: {result.get('error', 'Unknown')}")


@bot.message_handler(commands=["list"])
def cmd_list(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Admin only!")
        return
    result = server_req("/api/list")
    if "error" in result:
        bot.reply_to(msg, f"❌ Server error: {result['error']}")
        return
    keys = result.get("keys", [])
    if not keys:
        bot.reply_to(msg, "📋 No keys registered.")
        return
    text = "📋 *Registered Keys*\n━━━━━━━━━━━━━━━━━\n"
    for i, k in enumerate(keys, 1):
        emoji = "🟢" if k["status"] == "ACTIVE" else "🔴"
        text += (
            f"{emoji} *{i}.* `{k['device_id']}`\n"
            f"   📅 Exp: {k['expiry']}\n"
            f"   ⏳ Remaining: {k['remaining_days']}d {k['remaining_hours']}h\n"
            f"   📊 Status: {k['status']}\n\n"
        )
    bot.reply_to(msg, text, parse_mode="Markdown")


@bot.message_handler(commands=["info"])
def cmd_info(msg):
    if not is_admin(msg.from_user.id):
        bot.reply_to(msg, "❌ Admin only!")
        return
    args = msg.text.split()[1:]
    if not args:
        bot.reply_to(msg, "⚠️ Usage: /info <device_id>")
        return
    device_id = args[0].upper().strip()
    result = server_req("/api/list")
    if "error" in result:
        bot.reply_to(msg, f"❌ Server error: {result['error']}")
        return
    for k in result.get("keys", []):
        if k["device_id"] == device_id:
            text = (
                f"ℹ️ *Device Info*\n"
                f"━━━━━━━━━━━━━━━━━\n"
                f"🆔 ID: `{k['device_id']}`\n"
                f"📅 Expiry: {k['expiry']}\n"
                f"⏳ Remaining: {k['remaining_days']}d {k['remaining_hours']}h\n"
                f"📊 Status: {k['status']}\n"
            )
            bot.reply_to(msg, text, parse_mode="Markdown")
            return
    bot.reply_to(msg, f"❌ Device `{device_id}` not found.")


@bot.message_handler(commands=["status"])
def cmd_status(msg):
    result = server_req("/ping")
    if "error" in result:
        bot.reply_to(msg, f"❌ Server unreachable: {result['error']}\nMake sure key_server.py is running!")
        return
    text = (
        "📊 *Server Status*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"🟢 Server: ONLINE\n"
        f"📦 Keys: {result.get('keys_count', 0)}\n"
        f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}\n"
    )
    bot.reply_to(msg, text, parse_mode="Markdown")


@bot.message_handler(func=lambda m: True)
def handle_text(msg):
    text = msg.text.strip().upper()
    if text.startswith("DEV-") and len(text) >= 8:
        if is_admin(msg.from_user.id):
            bot.reply_to(msg,
                f"🔍 Device ID: `{text}`\n\n"
                f"Register: `/add {text} 7`",
                parse_mode="Markdown"
            )
        else:
            bot.reply_to(msg,
                f"📌 ID received: `{text}`\n"
                f"Wait for admin to register your key.",
                parse_mode="Markdown"
            )

if __name__ == "__main__":
    print("=" * 50)
    print("  WiFi Bypass Key Bot")
    print(f"  Bot Token: {BOT_TOKEN[:10]}...")
    print(f"  Admin ID: {ADMIN_ID}")
    print(f"  Server: {SERVER_URL}")
    print(f"  API Key: {API_KEY}")
    print("=" * 50)
    
    # Check server
    try:
        r = requests.get(f"{SERVER_URL}/ping", timeout=5)
        print(f"[+] Server: {r.json()}")
    except:
        print("[-] Server not reachable!")
    
    print("[+] Bot starting...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
