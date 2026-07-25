# WiFi Bypass Key System

Termux မှာ run မယ့် **Key Server + Telegram Bot** System ပါ။

---

## System Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   User Device    │     │   Your Termux    │     │   Telegram Bot   │
│  scan_keyed.py   │────▶│  key_server.py   │◀────│   key_bot.py     │
│                  │     │  (localhost:2060) │     │  (Admin Only)    │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                        │                        │
        │  Key Check Request     │  Key Register          │
        │─────────────────────────────────────────────────▶│
        │                        │         ◀─────────────────│
        │  Key Response          │   Admin: /add DEV-XX 7   │
        │◀───────────────────────────────────────────────────│
```

---

## Termux Setup

### Step 1: Install Dependencies

```bash
pkg update && pkg upgrade
pkg install python
pip install flask pyTelegramBotAPI requests
```

### Step 2: Copy Files to Termux

```bash
mkdir -p ~/key_system
# Copy all 3 files to ~/key_system/
#   key_server.py
#   key_bot.py
#   scan_keyed.py
#   start.sh
```

### Step 3: Start the System

```bash
cd ~/key_system
chmod +x start.sh
./start.sh
```

**OR** manually:

```bash
# Terminal 1: Start Key Server
python3 ~/key_system/key_server.py &

# Terminal 2: Start Telegram Bot
python3 ~/key_system/key_bot.py
```

---

## Telegram Bot Commands (Admin Only)

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show help menu | `/start` |
| `/add` | Register new key | `/add DEV-ABC123 7` |
| `/remove` | Remove a key | `/remove DEV-ABC123` |
| `/extend` | Extend key duration | `/extend DEV-ABC123 14` |
| `/list` | List all keys | `/list` |
| `/info` | Check device info | `/info DEV-ABC123` |
| `/status` | Server health check | `/status` |
| `/secret` | Show admin secret | `/secret` |
| `/mykey` | Show your device ID | `/mykey` |

### Duration Shortcuts

| Shortcut | Days |
|----------|------|
| `1d` | 1 day |
| `3d` | 3 days |
| `7d` | 7 days |
| `14d` | 14 days |
| `30d` | 30 days |

---

## How to Sell Keys

### Step 1: User runs scan_keyed.py
User က Script run ပြီး Device ID ပြလာမယ်:
```
[*] Device ID : DEV-XXXXXXXXXXXX
```

### Step 2: User sends Device ID to you
User က Telegram မှာ Device ID ပို့မယ်

### Step 3: You register the key via Bot
Telegram Bot မှာ:
```
/add DEV-XXXXXXXXXXXX 7
```

### Step 4: User can now use the script
User က Script ပြန် run ရင် Key verified ဖြစ်ပြီး အလုပ်လုပ်မယ်

---

## Configuration

### key_server.py
- Server runs on `http://localhost:2060`
- Admin secret is auto-generated on first run
- Keys stored in `~/key_data/keys.json`

### key_bot.py
- Bot Token: `8972355563:AAGKhjO1Ly0QCIG2jcxFizfMKN4sbYfblDc`
- Admin ID: `8363372270`
- Server URL: `http://localhost:2060`

### scan_keyed.py (for users)
- Key Server: `http://localhost:2060/api/keys`
- Secret Key: `W1F1_BYP@S_S3CR3T_2026`

---

## Notes

- Key Server နဲ့ Telegram Bot နှစ်ခုစလုံး Termux မှာ run နေရမယ်
- User တွေ scan_keyed.py run တာနဲ့ Key Server ကို auto-connect လုပ်မယ်
- Key expired ဖြစ်ရင် Script အလုပ်မလုပ်တော့ဘူး
- `/extend` command နဲ့ key ဖြည့်ပေးနိုင်တယ်

---

## Troubleshooting

### Server not starting
```bash
# Check if port 2060 is in use
netstat -tlnp | grep 2060
# Kill existing process
kill $(lsof -t -i:2060) 2>/dev/null
```

### Bot not responding
```bash
# Check if bot is running
ps aux | grep key_bot
# Restart bot
python3 ~/key_system/key_bot.py &
```

### Keys not working
```bash
# Check server status
curl http://localhost:2060/ping
# List all keys
curl "http://localhost:2060/api/list?admin_secret=YOUR_SECRET"
```
