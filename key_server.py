#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFi Bypass Key Server - Cloud Version (Render.com compatible)
"""

import json
import os
import time
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------- CONFIG ----------
PORT = int(os.environ.get("PORT", 10000))
API_KEY = "w1f1k3y2026"

# Data storage - use /tmp on Render (ephemeral) or home dir on Termux
if os.path.exists("/opt/render/project/src"):
    DATA_DIR = "/opt/render/project/src/key_data"
else:
    DATA_DIR = os.path.join(os.path.expanduser("~"), "key_data")

os.makedirs(DATA_DIR, exist_ok=True)
KEYS_FILE = os.path.join(DATA_DIR, "keys.json")
LOG_FILE = os.path.join(DATA_DIR, "server.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line.strip())
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except:
        pass

def load_keys():
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"keys": {}}

def save_keys(data):
    try:
        with open(KEYS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log(f"ERROR saving: {e}")

def check_api_key():
    """Check API key from header, query param, or JSON body"""
    key = request.headers.get("X-API-Key", "")
    if key:
        return key == API_KEY
    key = request.args.get("api_key", "")
    if key:
        return key == API_KEY
    data = request.get_json(silent=True) or {}
    key = data.get("api_key", "")
    if key:
        return key == API_KEY
    return False

# Load from file on every request (Render free tier may sleep and lose in-memory state)
def get_keys_db():
    return load_keys()

KEYS_DB = load_keys()
log(f"Server initialized with {len(KEYS_DB.get('keys', {}))} keys on port {PORT}")

def _mk_dev_id(raw_id):
    return raw_id.upper().strip()

# ---------- API ENDPOINTS ----------

@app.route("/api/keys", methods=["GET"])
def api_keys():
    """Script calls this to check if device is approved."""
    KEYS_DB = get_keys_db()
    ct = time.time()
    valid_keys = []
    expirations = {}
    for dev_id, info in KEYS_DB["keys"].items():
        exp = info.get("expiry", 0)
        if exp > ct:
            valid_keys.append(dev_id)
            expirations[dev_id] = exp
    log(f"Key check - {len(valid_keys)} active")
    return jsonify({"keys": valid_keys, "expirations": expirations})

@app.route("/api/register", methods=["POST"])
def api_register():
    """Register a new device key (admin only)."""
    data = request.get_json(silent=True) or {}
    if not check_api_key():
        log("FAILED register - bad api_key")
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    KEYS_DB = get_keys_db()
    device_id = _mk_dev_id(data.get("device_id", ""))
    duration_days = int(data.get("duration_days", 1))

    if not device_id:
        return jsonify({"success": False, "error": "device_id required"}), 400

    expiry = time.time() + (duration_days * 86400)
    KEYS_DB["keys"][device_id] = {
        "expiry": expiry,
        "created": time.time(),
        "duration_days": duration_days,
        "status": "active"
    }
    save_keys(KEYS_DB)
    expiry_str = datetime.fromtimestamp(expiry).strftime("%Y-%m-%d %H:%M:%S")
    log(f"REGISTERED: {device_id} -> {expiry_str} ({duration_days}d)")
    return jsonify({"success": True, "device_id": device_id, "expiry": expiry_str, "expiry_ts": expiry})

@app.route("/api/remove", methods=["POST"])
def api_remove():
    """Remove a device key (admin only)."""
    data = request.get_json(silent=True) or {}
    if not check_api_key():
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    KEYS_DB = get_keys_db()
    device_id = _mk_dev_id(data.get("device_id", ""))
    if device_id in KEYS_DB["keys"]:
        del KEYS_DB["keys"][device_id]
        save_keys(KEYS_DB)
        log(f"REMOVED: {device_id}")
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Not found"}), 404

@app.route("/api/extend", methods=["POST"])
def api_extend():
    """Extend a device key duration (admin only)."""
    data = request.get_json(silent=True) or {}
    if not check_api_key():
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    KEYS_DB = get_keys_db()
    device_id = _mk_dev_id(data.get("device_id", ""))
    duration_days = int(data.get("duration_days", 7))
    if device_id not in KEYS_DB["keys"]:
        return jsonify({"success": False, "error": "Not found"}), 404
    current_exp = KEYS_DB["keys"][device_id].get("expiry", 0)
    if current_exp < time.time():
        current_exp = time.time()
    new_exp = current_exp + (duration_days * 86400)
    KEYS_DB["keys"][device_id]["expiry"] = new_exp
    KEYS_DB["keys"][device_id]["duration_days"] = duration_days
    save_keys(KEYS_DB)
    log(f"EXTENDED: {device_id} +{duration_days}d")
    return jsonify({"success": True, "expiry": datetime.fromtimestamp(new_exp).strftime("%Y-%m-%d %H:%M:%S")})

@app.route("/api/list", methods=["GET"])
def api_list():
    """List all keys (admin only)."""
    if not check_api_key():
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    KEYS_DB = get_keys_db()
    ct = time.time()
    result = []
    for dev_id, info in KEYS_DB["keys"].items():
        exp = info.get("expiry", 0)
        status = "ACTIVE" if exp > ct else "EXPIRED"
        result.append({
            "device_id": dev_id,
            "expiry": datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M:%S"),
            "remaining_days": max(0, int((exp - ct) / 86400)),
            "remaining_hours": max(0, int((exp - ct) / 3600)),
            "status": status
        })
    return jsonify({"keys": result})

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "keys_count": len(KEYS_DB["keys"])})

if __name__ == "__main__":
    print("=" * 50)
    print("  WiFi Bypass Key Server")
    print(f"  Running on port {PORT}")
    print(f"  API Key: {API_KEY}")
    print("=" * 50)
    log("Server started")
    app.run(host="0.0.0.0", port=PORT, debug=False)
