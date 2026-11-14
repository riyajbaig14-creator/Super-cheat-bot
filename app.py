#!/usr/bin/env python3
# YUTA FULL SETUP — INDIA (v5.2) · FAST API · single-file
# Dev: @YUTA_005

import hashlib, requests, json, os, sys, re, base64, time, uuid, random
from urllib.parse import quote
from datetime import datetime, timezone, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings; warnings.filterwarnings("ignore")

# ── try.py login imports ────────────────────────────────────────────────────
import ssl, hmac, string
import asyncio
import aiohttp
try:
    from protobuf_decoder.protobuf_decoder import Parser
    HAS_PARSER = True
except ImportError:
    HAS_PARSER = False
    Parser = None

DEV_HANDLE = "@YUTA_005"
BRAND      = "YUTA FULL SETUP · INDIA"

# ── NO-OP UI ────────────────────────────────────────────────────────────────
def _clr(t): return t
def clear(): pass
def banner(): pass
def print_box(*a, **k): pass
def step_start(*a, **k): pass
def step_ok(*a, **k): pass
def step_fail(*a, **k): pass
class Spinner:
    def __init__(self, *a, **k): pass
    def __enter__(self): return self
    def __exit__(self, *a): pass

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
SAVED_FOLDER = os.path.join(BASE_DIR, "SAVED")
ACCOUNTS_FILE = os.path.join(BASE_DIR, "accounts.json")
OUT_FILE      = os.path.join(SAVED_FOLDER, "full_setup_results.json")

# ── INDIA CONSTANTS ─────────────────────────────────────────────────────────
LOGIN_HOSTS = [
    "loginbp.ggwhitehawk.com",
    "loginbp.ggblueshark.com",
    "loginbp.ggpolarbear.com",
    "loginbp.ppmainecoonghj.com",
    "loginbp.ind.freefiremobile.com",
]
CLIENT_HOSTS = [
    "clientbp.ind.freefiremobile.com",
    "clientbp.ggpolarbear.com",
    "clientbp.ggblueshark.com",
    "clientbp.ppmainecoonghj.com",
    "client.ind.freefiremobile.com",
]

# ═══════════════════════════════════════════════════════════════════════════
#  ⭐ NEW LOGIN SYSTEM (try.py flow) — replaces old GRANT_ENDPOINTS/Grant/ML
# ═══════════════════════════════════════════════════════════════════════════
APP_ID = 100067
SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
GARENA_BASE = "https://100067.connect.garena.com/api/v2/oauth"
GRANT_URL   = f"{GARENA_BASE}/guest/token:grant"
DATADOME_URL = "https://datadome.garena.com/js/"

MIN_REGISTER_INTERVAL = 1.0
REGISTER_BACKOFF_START = 10.0
REGISTER_BACKOFF_MAX = 60.0
REGISTER_MAX_RETRIES = 6
DATADOME_MAX_RETRIES = 4

USER_AGENT_MSDK = "GarenaMSDK/4.0.44(V2538 ;Android 16;en;US;app 1.132.1 2019121227;)"

SESSION_HASH = "1ac4b80ecf0478a44203bf8fac6120f5"

_KEYSTREAM = bytes([
    0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
    0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,
])

GGRE_RAW = bytes.fromhex(
    "47475245010101006d020000b260ee08e1f86b4c57f9c70f86bba26ed5d1436bcf52e142db3249d905eded757764991ca31a8373cdd26eab91b80f3f1f6f262f4f10b895d7b6937ddba30a27197453890e9da49373f736c679b8254e2f8e1623e91084a5fdd5374fe478ff99e010834553fddeb0bec4018d142e49df9bb236675b67e852f92a43586f7a7d4d0d7a197a1d4da32714dab4d069ad53214e2c33b3877420a12459738c4c619cbd815fa878bbd104776bb3e1ac7818d5397b04a666ac57f682763ff2df31bc2f846ddc7904f3dce1bda0c4b01f9698e9166f98c84f92640abe3f6317834a42e5c12573b46842c1a6ea8fe6ca9c006dca48a2087e1f983dfb5692771e4a0b15b337ad669b1d08b40862b176bace5331b49a767375b1a8469012aa70a67b55fe71b72478201d0b3ac7269c064c960361e92ee7ba8a42cc6b582bf9b965fb388fa9172ad44c4b073ac23c02080a6bcd106b691ffdf4c7cf71e42f2063fcf196e9bddc5e85be1fe5048eb1b31b460efbb46d76195eef9904c4cba326f2e17ff51fec17dd965aa06dadd4ab07d6966e4a7c38e8afd66dfde56c872bb87516a8f7313c797e4d80e5ad4a5f7afad95c1e0449254adae052e71a3fb98399f93ab30848e0d23252dd45e6fd41bc5fa7303dfb846a8fd713a0032a0b0ae96dfba1bbe41d20abd8099e2cb7fccc329d25bd153029139ef05d090a5093ea557693c0a8d491395b8a23ca844b3887dd5dfc29ac06f4b9be87883a793211b973465e2644c4f5de02b8ab01571401203fc2740423826858cc6da0194c195d27aac4ec4b9d23d506c1501d06440aca3fc180926d75d4a004d3dff21eb4ea1e8c86e6c9627248eff953e1d192d5c8efc006a7e512388ef2ebdb72ee3ad42d719f28e8f994e12ebf4c79f2ffe3abd7408ccd2236a7b89b2606247a732c10c4"
)

REGION_LANG = {"IND":"hi","BD":"bn","PK":"ur","ID":"id","TH":"th","VN":"vi","ME":"ar"}
REGION_GROUP = {
    "IND":"IND",
    "BR":"AMERICA","US":"AMERICA","NA":"AMERICA","SAC":"AMERICA",
    "ID":"OTHERS","TH":"OTHERS","ME":"OTHERS","EUROPE":"OTHERS",
    "VN":"OTHERS","BD":"OTHERS","PK":"OTHERS","TW":"OTHERS","RU":"OTHERS","SG":"OTHERS",
}
REGION_URLS = {
    "IND":    {"server":"https://loginbp.ppmainecoonghj.com/","client":"https://client.ind.freefiremobile.com/"},
    "AMERICA":{"server":"https://loginbp.ppmainecoonghj.com/","client":"https://client.us.freefiremobile.com/"},
    "OTHERS": {"server":"https://loginbp.ppmainecoonghj.com/","client":"https://clientbp.ggpolarbear.com/"},
}

_PLAY_VERSION = "1.132.13"
_OB_VERSION = "OB55"

REGION_PROFILES = {
    "IND": {
        "pkg_name": "com.garena.game.ffi",
        "apk_hash": "dd9d4c174e0472d34b7fd34bd5924bc9",
        "app_dir": "/data/app/~~OlJmIW-Yzl-44x2WnJP4Nw==/com.garena.game.ffi-_eDk_pQQMiFk1YUeqwJBvQ==",
        "lib_arch": "arm64", "lib_field_73": 3, "lib_field_76": 3, "cpu_arch_field_81": "64",
        "cpu_details": "ARM64 FP ASIMD AES | 2200 | 8",
        "screen_w": 2340, "screen_h": 1080, "dpi": "295", "mem_field_16": 5586,
        "gpu_renderer": "Mali-G57 MC2", "gpu_version": "OpenGL ES 3.2 v1.r38p1",
        "model": "samsung SM-A155F",
        "os_version": "Android OS 14 / API-34 (UP1A.231005.007/E156BXXS6AYD4)",
        "carrier": "airtel", "net_type": "CarrierDataNetwork",
        "net_apn": "airtel", "net_gen": "4G", "city": "Coimbatore", "state": "TN",
        "client_version_code": "2019121269",
        "memory_sig_94": "KqsHT54jON6bxITmlrRyOrXWBqKqZ4BoqPzT/mhtriAfRt2dt7gC8pnAJfj11alcEUA5sD8BshSYQhxXT9RFmU6YzcI1FKK4MwxJcF4+kvelPD1H",
        "storage_95": 111207,
        "hotfix_106": "https://dl-tata.freefireind.in/live/ABHotUpdates/|https://core-tata.freefireind.in/live/ABHotUpdates/|dff941d41e6e3a9e76f05ed71fdc8d87",
        "hotfix_hash_107": "1.6168622e0868ddbd",
        "mem_60": 108009, "mem_61": 3859, "mem_62": 5023,
        "mem_64": 3987, "mem_65": 108009, "mem_66": 3987, "mem_67": 108009,
        "field_70": 4, "region_code_26": "IND", "field_104": 11921,
        "default_client_version": "1.134.14", "play_pkg": "com.garena.game.ffi",
    },
    "DEFAULT": {
        "pkg_name": "com.dts.freefireth",
        "apk_hash": "b8e0cd5e295eee42f5860d3c86e483dd",
        "app_dir": "/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==",
        "lib_arch": "arm", "lib_field_73": 2, "lib_field_76": 1, "cpu_arch_field_81": "32",
        "cpu_details": "ARMv7 VFPv3 NEON | 2002 | 8",
        "screen_w": 1672, "screen_h": 750, "dpi": "338", "mem_field_16": 3702,
        "gpu_renderer": "Mali-G52",
        "gpu_version": "OpenGL ES 3.2 v1.r38p1-01bet0-mbs2v41_0.6d20ec041e51b2f2d25dfc265586ebe8",
        "model": "samsung SM-E135F",
        "os_version": "Android OS 14 / API-34 (UP1A.231005.007/E135FXXSEEZE2)",
        "carrier": "airtel", "net_type": "CarrierDataNetwork",
        "net_apn": "airtel", "net_gen": "Cellular",
        "city": "Khulna", "state": "D", "client_version_code": "2019121229",
        "memory_sig_94": "KqsHT3Yeqo3RLRl8efNiL3aL/1SHwlSrtK0DwNAqdkNBQz70TeVy+icaIwuR3UK4b65Uf3IG5xBFEv0uu+jQZI+rOYCmNCsXjJT4QcZaYgoaaUGG",
        "storage_95": 111107,
        "hotfix_106": "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462",
        "hotfix_hash_107": "c8e41b7a93f02d56e1a94c7b8203f5d1",
        "mem_60": 52037, "mem_61": 5355, "mem_62": 3723,
        "mem_64": 5483, "mem_65": 52037, "mem_66": 5483, "mem_67": 52037,
        "field_70": 2, "region_code_26": "ID", "field_104": 53792,
        "default_client_version": "1.132.9", "play_pkg": "com.dts.freefireth",
    },
}

def _get_region_profile(region):
    return REGION_PROFILES.get((region or "ID").upper(), REGION_PROFILES["DEFAULT"])

# ── AES / PROTOBUF ──────────────────────────────────────────────────────────
AES_KEY = bytes([89,103,38,116,99,37,68,69,117,104,54,37,90,99,94,56])
AES_IV  = bytes([54,111,121,90,68,114,50,50,69,51,121,99,104,106,77,37])
NICK_XOR_KEY = b"1e5898ccb8dfdd921f9bdea848768b64a201"

def aes_encrypt(data): return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(data, AES.block_size))

def aes_decrypt(data):
    try:
        d = AES.new(AES_KEY, AES.MODE_CBC, AES_IV).decrypt(data)
        if d and 0 < d[-1] <= 16: return d[:-d[-1]]
    except Exception: pass
    return data

def encode_varint(n):
    if n < 0: n = (1 << 64) + n
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n: break
    return bytes(out)

def _rv(data, pos):
    r = 0; s = 0
    while pos < len(data):
        b = data[pos]; r |= (b & 0x7F) << s; pos += 1
        if not (b & 0x80): return r, pos
        s += 7
        if s > 63: break
    return None, pos

def decode_message(data):
    result = {}; pos = 0; n = len(data)
    while pos < n:
        try:
            tag, pos = _rv(data, pos)
            if tag is None: break
            fn = tag >> 3; wt = tag & 7
            if fn == 0: break
            if wt == 0:
                v, pos = _rv(data, pos); result[fn] = v
            elif wt == 1:
                if pos + 8 > n: break
                result[fn] = int.from_bytes(data[pos:pos+8], 'little'); pos += 8
            elif wt == 2:
                sz, pos = _rv(data, pos)
                if sz is None or pos + sz > n: break
                raw = data[pos:pos+sz]; pos += sz
                try:
                    nested, _ = decode_message(raw)
                    if nested and all(isinstance(k, int) for k in nested.keys()):
                        result[fn] = nested
                    else: result[fn] = raw
                except Exception: result[fn] = raw
            elif wt == 5:
                if pos + 4 > n: break
                result[fn] = int.from_bytes(data[pos:pos+4], 'little'); pos += 4
            else: break
        except Exception: break
    return result, None

def decode_best(content):
    if not content: return {}
    try:
        f, _ = decode_message(content)
        if f: return f
    except Exception: pass
    try:
        d = aes_decrypt(content)
        if d and d != content:
            f, _ = decode_message(d)
            if f: return f
    except Exception: pass
    return {}

def decode_varint_sync(data, offset):
    result = 0; shift = 0
    while offset < len(data):
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80): return result, offset
        shift += 7
    return None, offset

def decode_protobuf_2(data):
    result = {}; offset = 0; data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint_sync(data, offset)
        if header is None: break
        fn = header >> 3; wt = header & 0x7
        if wt == 0:
            v, offset = decode_varint_sync(data, offset)
            if v is not None: result[fn] = v
        elif wt == 2:
            length, offset = decode_varint_sync(data, offset)
            if length is None: break
            value = data[offset:offset+length]; offset += length
            try:
                s = value.decode('utf-8')
                result[fn] = s if s else value.hex()
            except UnicodeDecodeError:
                nested = decode_protobuf_2(value)
                result[fn] = nested if nested else value.hex()
        elif wt == 1: offset += 8
        elif wt == 3: offset += 4
        else: break
    return result

def extract_raw_fields(data):
    result = {}; offset = 0; data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint_sync(data, offset)
        if header is None: break
        fn = header >> 3; wt = header & 0x7
        if wt == 0:
            v, offset = decode_varint_sync(data, offset)
            if v is not None: result[fn] = v
        elif wt == 2:
            length, offset = decode_varint_sync(data, offset)
            if length is None: break
            if offset + length > data_len: break
            result[fn] = bytes(data[offset:offset+length]); offset += length
        elif wt == 1: offset += 8
        elif wt == 3: offset += 4
        else: break
    return result

def create_proto(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(field, str): field = int(field)
        if isinstance(value, dict):
            body = create_proto(value)
            packet.extend(encode_varint((field << 3) | 2))
            packet.extend(encode_varint(len(body)))
            packet.extend(body)
        elif isinstance(value, bool):
            packet.extend(encode_varint(field << 3))
            packet.extend(encode_varint(1 if value else 0))
        elif isinstance(value, int):
            packet.extend(encode_varint(field << 3))
            packet.extend(encode_varint(value))
        elif isinstance(value, str):
            b = value.encode('utf-8')
            packet.extend(encode_varint((field << 3) | 2))
            packet.extend(encode_varint(len(b)))
            packet.extend(b)
        elif isinstance(value, (bytes, bytearray)):
            packet.extend(encode_varint((field << 3) | 2))
            packet.extend(encode_varint(len(value)))
            packet.extend(value)
    return bytes(packet)

def decode_jwt_payload(jwt):
    try:
        p = jwt.split('.')[1]
        p += '=' * ((4 - len(p) % 4) % 4)
        return json.loads(base64.urlsafe_b64decode(p))
    except Exception: return {}

def decode_nickname(b64):
    try:
        raw = base64.b64decode(b64)
        dec = bytearray()
        for i, b in enumerate(raw): dec.append(b ^ NICK_XOR_KEY[i % len(NICK_XOR_KEY)])
        return dec.decode('utf-8', errors='replace').strip('\x00')
    except Exception: return ""

def _to_bytes(v):
    if isinstance(v, bytes): return v
    if isinstance(v, str):
        try: return bytes.fromhex(v)
        except ValueError: return v.encode()
    if v is None: return b""
    return bytes(v)

def _normalize_uid(uid):
    s = str(uid).strip()
    return int(s) if s.isdigit() else s

IST_TZ = timezone(timedelta(hours=5, minutes=30))
def now_str(): return datetime.now(IST_TZ).strftime('%Y-%m-%d %H:%M:%S')
BD_TZ = IST_TZ

def _get_xga(base=1792293041):
    base_ts = int(datetime(2026, 10, 18, 9, 26, 29, tzinfo=BD_TZ).timestamp())
    return str(base + max(0, int(datetime.now(BD_TZ).timestamp()) - base_ts))

def get_session():
    s = requests.Session(); s.verify = False
    s.mount('https://', requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=20))
    return s

def build_region_cfg(region):
    region = (region or "IND").upper()
    grp = REGION_GROUP.get(region, "OTHERS")
    return {
        "latest_release_version": _OB_VERSION,
        "remote_version": _PLAY_VERSION,
        "region": region,
        "lang": REGION_LANG.get(region, "en"),
        "country_code": region,
        "server_url": REGION_URLS[grp]["server"],
        "client_url": REGION_URLS[grp]["client"],
    }

# ═══════════════════════════════════════════════════════════════════════════
#  ⭐ DATADOME + TOKEN GRANT (try.py)
# ═══════════════════════════════════════════════════════════════════════════
import threading as _threading
_gate_lock = _threading.Lock()
_dd_lock = _threading.Lock()
_last_register_time = 0.0
_dd_session_cookie = None
_dd_expires_at = 0.0

USER_AGENT_WEB = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_datadome(tag="[api]", force=False):
    global _dd_session_cookie, _dd_expires_at
    with _dd_lock:
        now = time.time()
        if not force and _dd_session_cookie and _dd_expires_at > now:
            return _dd_session_cookie
        headers = {
            "User-Agent": USER_AGENT_WEB,
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://sso.garena.com/universal/register?locale=en-SG",
            "Origin": "https://sso.garena.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        payload = {
            "jsType": "le",
            "eventCounters": '{"mousemove":1,"click":1,"keydown":11}',
            "ddk": "AE3F04AD3F0D3A462481A337485081",
            "Referer": "https://sso.garena.com/universal/register?locale=en-SG",
            "request": "/universal/register?locale=en-SG",
            "responsePage": "origin", "ddv": "5.7.0",
        }
        last = None
        for attempt in range(1, DATADOME_MAX_RETRIES + 1):
            try:
                r = requests.post(DATADOME_URL, data=payload, headers=headers, timeout=15)
                r.raise_for_status()
                result = r.json()
            except Exception as e:
                last = e; time.sleep(1.5 * attempt); continue
            if result.get("status") == 200 and result.get("cookie"):
                for part in result["cookie"].split(";"):
                    if "datadome=" in part:
                        dd = part.replace("datadome=", "").strip()
                        if dd:
                            _dd_session_cookie = dd
                            _dd_expires_at = now + 300.0
                            return dd
            last = result
            time.sleep(1.5 * attempt)
        raise RuntimeError(f"DataDome failed: {last}")

def sign_body(body): return hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()

def _wait_register_slot(tag="[api]"):
    global _last_register_time
    while True:
        with _gate_lock:
            now = time.time()
            wait = MIN_REGISTER_INTERVAL - (now - _last_register_time)
            if wait <= 0:
                _last_register_time = now
                return
        time.sleep(min(wait, 0.5))

# ═══════════════════════════════════════════════════════════════════════════
#  ⭐ 1. GRANT_GUEST — try.py guest_token (replaces old grant_guest)
# ═══════════════════════════════════════════════════════════════════════════
def grant_guest(uid, pw, s, verbose=False):
    """try.py guest_token flow — returns {open_id, access_token}"""
    tag = "[grant]"
    try:
        uid_val = _normalize_uid(uid)
    except Exception:
        return None

    payload = {
        "client_id": APP_ID, "client_secret": SECRET, "client_type": 2,
        "device_id": "02-" + str(uuid.uuid4()), "password": str(pw),
        "response_type": "token", "uid": uid_val,
    }
    body = json.dumps(payload, separators=(",", ":"))

    last_err = None
    for attempt in range(1, 5):
        try:
            datadome = get_datadome(tag, force=(attempt > 1 and attempt % 2 == 0))
        except Exception as e:
            last_err = e
            time.sleep(2.0 * attempt); continue

        headers = {
            "User-Agent": USER_AGENT_MSDK,
            "Authorization": f"Signature {sign_body(body)}",
            "Cookie": f"datadome={datadome}",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }
        try:
            r = requests.post(GRANT_URL, data=body, headers=headers, timeout=20, verify=False)
            data = r.json()
        except Exception as e:
            last_err = e; time.sleep(2.0 * attempt); continue

        code = data.get("code")
        if code == 0:
            d = data["data"]
            return {"open_id": d["open_id"], "access_token": d["access_token"],
                    "platform": int(d.get("platform", 4) or 4)}
        if code in (1006, 1005):
            wait = min(REGISTER_BACKOFF_START * (2 ** (attempt - 1)), REGISTER_BACKOFF_MAX)
            last_err = data; time.sleep(wait); continue
        last_err = data
        if attempt < 4:
            time.sleep(1.5 * attempt); continue

    if verbose: print(f"  grant_guest failed: {last_err}")
    return None

# ═══════════════════════════════════════════════════════════════════════════
#  ⭐ 2. MAJOR_LOGIN — try.py (replaces old major_login)
# ═══════════════════════════════════════════════════════════════════════════
def _extract_key_iv(res_json):
    if "__RAW_HEX__" in res_json and "__OFFSET__" in res_json:
        try:
            raw = bytes.fromhex(res_json["__RAW_HEX__"])
            off = int(res_json["__OFFSET__"])
            rf = extract_raw_fields(raw[off:])
            for kf, vf in [(22,23),(24,25),(6,7)]:
                k = rf.get(kf); v = rf.get(vf)
                if isinstance(k,(bytes,bytearray)) and len(k)==16 and \
                   isinstance(v,(bytes,bytearray)) and len(v)==16:
                    return bytes(k), bytes(v)
        except Exception: pass
    found = {}
    for k, v in res_json.items():
        if str(k).startswith("__"): continue
        if not isinstance(v, dict): continue
        data = v.get("data")
        if data is None: continue
        raw = None
        if isinstance(data, (bytes,bytearray)) and len(data)==16: raw = bytes(data)
        elif isinstance(data, str) and len(data)==32:
            try:
                c = bytes.fromhex(data)
                if len(c)==16: raw = c
            except Exception: pass
        if raw and len(raw)==16:
            try: found[int(k)] = raw
            except Exception: pass
    if len(found) < 2: return None, None
    for kf, vf in [(22,23),(24,25),(6,7)]:
        if kf in found and vf in found: return found[kf], found[vf]
    sk = sorted(found.keys())
    return found[sk[0]], found[sk[1]]

def _parse_results_sync(results):
    out = {}
    for r in results:
        fd = {"wire_type": r.wire_type}
        if r.wire_type == "varint": fd["data"] = r.data
        elif r.wire_type in ("string","bytes"): fd["data"] = r.data
        elif r.wire_type == "length_delimited":
            if hasattr(r.data, "results"): fd["data"] = _parse_results_sync(r.data.results)
            elif isinstance(r.data, list): fd["data"] = _parse_results_sync(r.data)
            else: fd["data"] = str(r.data)
        out[str(r.field)] = fd
    return out

def _decode_protobuf_dict(data):
    try:
        parsed = Parser().parse(data)
        return _parse_results_sync(parsed)
    except Exception: return {}

def _build_major_login_payload(access_token, open_id, platform, version, lang_code, region):
    prof = _get_region_profile(region)
    device_id = f"Google|{uuid.uuid4()}"
    major_login = {
        "3": str(datetime.now())[:-7], "4": "free fire", "5": 1,
        "7": f"{version}", "8": prof["os_version"], "9": "Handheld",
        "10": prof["carrier"], "11": prof["net_type"],
        "12": prof["screen_w"], "13": prof["screen_h"], "14": prof["dpi"],
        "15": prof["cpu_details"], "16": prof["mem_field_16"],
        "17": prof["gpu_renderer"], "18": prof["gpu_version"],
        "19": device_id, "20": f"{random.randint(49,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}", "21": lang_code,
        "22": f"{open_id}", "23": f"{platform}", "24": "Handheld",
        "25": prof["model"], "26": prof["region_code_26"],
        "29": f"{access_token}", "30": 1,
        "41": prof["net_apn"], "42": prof["net_gen"],
        "57": SESSION_HASH, "60": prof["mem_60"], "61": prof["mem_61"],
        "62": prof["mem_62"], "64": prof["mem_64"], "65": prof["mem_65"],
        "66": prof["mem_66"], "67": prof["mem_67"],
        "70": prof["field_70"], "73": prof["lib_field_73"],
        "74": f'{prof["app_dir"]}/lib/{prof["lib_arch"]}',
        "76": prof["lib_field_76"],
        "77": f'{prof["apk_hash"]}|{prof["app_dir"]}/base.apk',
        "78": 3, "79": 2, "81": prof["cpu_arch_field_81"],
        "83": prof["client_version_code"], "85": 3, "86": "OpenGLES2",
        "87": 8191, "88": int(platform), "90": prof["city"], "91": prof["state"],
        "92": 9570, "93": "android", "94": prof["memory_sig_94"],
        "95": prof["storage_95"],
        "96": "{\"cur_rate\":null,\"support_etc2\":false}",
        "97": 1, "98": 1, "99": f"{platform}", "100": f"{platform}",
        "102": "4503454457550c0766", "104": prof["field_104"], "105": 1,
        "106": prof["hotfix_106"], "107": prof["hotfix_hash_107"],
    }
    get_login_data = dict(major_login)
    get_login_data["99"] = "0"
    get_login_data["103"] = 1
    proto1 = create_proto(major_login).hex()
    proto2 = create_proto(get_login_data).hex()
    return (AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(bytes.fromhex(proto1), 16)),
            AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(bytes.fromhex(proto2), 16)))

def major_login(uid, region, at, oid, lang, s, verbose=False):
    """try.py MajorLogin — returns {jwt, account_id, game_url, aes_key, aes_iv, server_time}"""
    region = (region or "IND").upper()
    cfg = build_region_cfg(region)
    version = cfg.get("remote_version", _PLAY_VERSION)
    release = cfg.get("latest_release_version", _OB_VERSION)
    platform = 4  # default; caller can override

    major_payload, _ = _build_major_login_payload(at, oid, platform, version, lang, region)
    login_url = cfg["server_url"].rstrip("/") + "/MajorLogin"

    req_headers = {
        "Accept": "*/*", "Authorization": "Bearer ",
        "Content-Type": "application/x-www-form-urlencoded",
        "ReleaseVersion": f"{release}",
        "User-Agent": "UnityPlayer/2018.4.12f1",
        "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
        "X-Unity-Version": "2018.4.12f1",
    }

    try:
        r = s.post(login_url, headers=req_headers, data=major_payload, timeout=20, verify=False)
    except Exception as e:
        if verbose: print(f"  MajorLogin exc: {e}")
        return None

    if r.status_code != 200 or len(r.content or b"") < 200:
        if verbose: print(f"  MajorLogin HTTP {r.status_code} len={len(r.content or b'')}")
        return None

    resp = r.content
    best = None; best_score = -1; best_off = 0
    for offset in [64, 0, 48, 32, 80, 16, 128, 8, 96, 60, 56, 40, 24, 20, 12, 4]:
        if offset >= len(resp): continue
        cb = resp[offset:]
        cand = _decode_protobuf_dict(cb) if HAS_PARSER else None
        if not cand:
            c2 = decode_protobuf_2(cb)
            if c2: cand = {str(k): {"data": v} for k, v in c2.items()}
        if not cand: continue
        keys = set(cand.keys())
        has_jwt = ("8" in keys) or (8 in keys)
        has_url = ("10" in keys) or (10 in keys)
        score = len(cand) + (100 if has_jwt else 0) + (50 if has_url else 0)
        if score > best_score:
            best = cand; best_score = score; best_off = offset
        if has_jwt and has_url: break

    if not best:
        if verbose: print("  MajorLogin parse failed")
        return None
    if ("8" not in best) and (8 not in best):
        if verbose: print("  MajorLogin no JWT field")
        return None

    best["__RAW_HEX__"] = resp.hex()
    best["__OFFSET__"] = best_off

    def _gd(k):
        v = best.get(str(k))
        if isinstance(v, dict) and "data" in v: return v["data"]
        if k in best and not isinstance(best[k], dict): return best[k]
        if isinstance(v, dict): return v.get("data")
        return None

    acc_id = _gd(1)
    jwt_token = _gd(8)
    server_url = _gd(10) or login_url
    server_time = _gd(21)
    aes_ak, iv_i = _extract_key_iv(best)
    if not jwt_token or not aes_ak or not iv_i:
        if verbose: print(f"  MajorLogin missing fields jwt={bool(jwt_token)} key={bool(aes_ak)} iv={bool(iv_i)}")
        return None

    pl = decode_jwt_payload(jwt_token)
    nick = decode_nickname(pl.get("nickname","")) if pl.get("nickname") else ""

    return {
        "jwt": jwt_token,
        "account_id": acc_id or pl.get("account_id"),
        "game_url": server_url,
        "region": region,
        "aes_key": aes_ok_safe(aes_ak),
        "aes_iv":  aes_ok_safe(iv_i),
        "server_time": server_time,
        "nickname": nick,
    }

def aes_ok_safe(v):
    if isinstance(v, bytes): return v
    try: return bytes.fromhex(v) if isinstance(v, str) else bytes(v)
    except Exception: return b""

# ═══════════════════════════════════════════════════════════════════════════
#  ⭐ 3. GET_LOGIN_DATA — try.py flow (needed for game_server/chat_server)
# ═══════════════════════════════════════════════════════════════════════════
def get_login_data_try(jwt, at, oid, region, s, verbose=False):
    """try.py GetLoginData — returns decoded dict (has game_server/chat_server)"""
    cfg = build_region_cfg(region)
    version = cfg.get("remote_version", _PLAY_VERSION)
    release = cfg.get("latest_release_version", _OB_VERSION)
    lang = cfg.get("lang", "en")
    client_url = cfg["client_url"]
    platform = 4

    _, login_payload = _build_major_login_payload(at, oid, platform, version, lang, region)
    url = f"{client_url.rstrip('/')}/GetLoginData"
    hdrs = {
        "Accept": "*/*", "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/x-www-form-urlencoded",
        "ReleaseVersion": f"{release}",
        "User-Agent": "UnityPlayer/2018.4.12f1",
        "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
        "X-Unity-Version": "2018.4.12f1",
    }

    # client hosts fallback
    for host in [client_url.rstrip('/').replace("https://","")] + CLIENT_HOSTS:
        try_url = f"https://{host}/GetLoginData" if not host.startswith("http") else f"{host}/GetLoginData"
        try:
            r = s.post(try_url, headers={**hdrs, "Host": host if not host.startswith("http") else host.split("//")[1].split("/")[0]},
                       data=login_payload, timeout=10, verify=False)
            if r.status_code != 200: continue
            content = r.content or b""
            for off in [0, 64, 48, 32, 80, 16, 128, 8, 96]:
                if off >= len(content): continue
                if HAS_PARSER:
                    c = _decode_protobuf_dict(content[off:])
                    if c and len(c) >= 3: return c
                c2 = decode_protobuf_2(content[off:])
                if c2 and len(c2) >= 3:
                    return {str(k): {"data": v} for k, v in c2.items()}
        except Exception:
            continue
    return {}

def _ld_get(ld, field, default=None):
    if not ld: return default
    v = ld.get(str(field), {})
    if isinstance(v, dict): return v.get("data", default)
    return v if v is not None else default

# ═══════════════════════════════════════════════════════════════════════════
#  PRESET LOADOUT (unchanged)
# ═══════════════════════════════════════════════════════════════════════════
PRESET_ID = 102000037

PRESET_STEPS = [
    ("128b", "E6 B8 3B 7E 00 B0 9B CA 30 CE 37 FE 10 F8 ED 0E "
             "58 A4 3E 98 FA 7E 29 53 58 8D 2C 21 A2 5B CB 4F "
             "71 21 9C 42 26 E3 C2 B7 0D 92 7C CF 6A BE 5E 6E "
             "57 DD 9E CD 02 9F BA 53 FC CA 94 3C 82 C2 E0 8C "
             "EF 55 02 A0 5F C6 05 DB 8F 62 E7 F0 CF 14 07 0B "
             "57 CB B5 4F 85 5E 50 6D 00 3B 9D 45 4F CA 2A 24 "
             "76 95 E3 77 68 EE A4 30 D2 8C E1 7D BD ED 18 B7 "
             "41 79 E2 CC 8D DC F8 B9 16 23 CE FD F4 D9 0C DB"),
    ("80b",  "C7 7B 8C 6E 5A FB 9F 08 55 F7 79 B7 59 9B B7 D2 "
             "69 43 95 B4 D1 06 94 02 D6 EC 9E B4 58 A5 23 53 "
             "89 35 52 C8 B8 9C 1F A7 3E 70 A5 C7 C7 D1 7D 09 "
             "37 5D 47 DB F3 3B 25 F0 31 1D 79 97 44 F6 71 AA "
             "73 53 B5 27 3D 35 F9 5A AF 4F 22 53 61 BA 0A BB"),
    ("96b",  "70 77 28 E1 02 50 3C B6 04 CE 4B 8B CA A4 E0 AD "
             "83 DC 83 46 2F 09 CA A4 0F D2 28 4A 76 B7 7F C5 "
             "DB F9 A0 C7 1E 2A 1C E3 D0 33 39 13 37 A8 C6 48 "
             "28 4B 74 E6 83 CE 25 64 2D 68 1C CA 5E 47 75 42 "
             "9C D6 35 7D 6C 8E 4A 37 7E 89 D6 AD 77 0A 1E 39 "
             "2D 5B F4 CB 86 7A B5 8F BB 58 E7 D5 56 96 6B DD"),
    ("64b",  "14 DD 1B 72 2A B6 1D A9 DD D0 F4 F8 A8 04 57 3D "
             "60 04 4B D1 13 7B BF 96 5B 10 E9 4D FD 60 4F D7 "
             "F1 0D 95 32 98 DA 6C BD E7 EE FB DA D7 4E 1E 53 "
             "41 8C 37 B9 20 6E E5 03 A9 63 EE 7E 56 A9 56 51"),
]

def give_newbie_roles(jwt, s, verbose=False):
    body = bytes.fromhex("EC91183DEF30AA26FAEF2BBBEB313789")
    r = _client_post(s, "GiveAccountNewbieRoles", jwt, "1792282124", body)
    return "ok" if r else "failed"

def _client_post(s, path, jwt, xga, body, timeout=10, verbose=False):
    for host in CLIENT_HOSTS:
        url = f"https://{host}/{path}"
        headers = {"Accept":"*/*","Accept-Encoding":"deflate, gzip",
                   "Authorization":f"Bearer {jwt}","Content-Length":str(len(body)),
                   "Content-Type":"application/x-www-form-urlencoded","Host":host,
                   "ReleaseVersion":_OB_VERSION,"User-Agent":"UnityPlayer/2018.4.12f1",
                   "X-GA":"v1 1","X-GA-SV":xga,"X-Unity-Version":"2018.4.12f1"}
        try:
            r = s.post(url, headers=headers, data=body, timeout=timeout, verify=False)
            if r.status_code == 200: return r
        except Exception: continue
    return None

def get_profiles(jwt, s, verbose=False):
    body = bytes.fromhex("1A725B2C56EC52BA7D09623454C0A003")
    r = _client_post(s, "GetProfiles", jwt, "1792282176", body)
    if not r: return []
    try:
        fields, _ = decode_message(r.content or b"")
        out = []
        for k, v in fields.items():
            if not isinstance(v, dict): continue
            pid = v.get(1)
            if not pid: continue
            items = []
            for fld, val in v.items():
                if fld in (1,3,6,8,11): continue
                if isinstance(val, dict):
                    for sk, sv in val.items():
                        if isinstance(sv, int) and 1_000_000 <= sv <= 999_999_999:
                            items.append((fld, sk, sv))
                elif isinstance(val, int) and 1_000_000 <= val <= 999_999_999:
                    items.append((fld, val))
            out.append({"id": pid, "active": bool(v.get(6)),
                        "unlocked": bool(v.get(8)), "items": items})
        return out
    except Exception: return []

def select_preset_loadout(jwt, s, body_hex, verbose=False):
    body = bytes.fromhex(re.sub(r'[^0-9a-fA-F]', '', body_hex))
    r = _client_post(s, "SelectPresetLoadout", jwt, _get_xga(1792293041), body, timeout=12)
    if r and r.status_code == 200:
        try:
            fields, _ = decode_message(r.content or b"")
            return "ok", fields
        except Exception: return "ok", {}
    return "failed", {}

# ── 7. INFO QUERIES (unchanged) ────────────────────────────────────────────
def _build_request_simple(uid):
    return encode_varint((1 << 3) | 0) + encode_varint(int(uid))

def _build_personal_show_req(uid):
    p = bytearray([0x08]); p.extend(encode_varint(int(uid)))
    p.append(0x10); p.extend(encode_varint(7))
    p.extend([0x18,0x01,0x20,0x01,0x28,0x01,0x30,0x01])
    return bytes(p)

def _build_stats_req(uid):
    p = bytearray([0x08]); p.extend(encode_varint(int(uid)))
    p.extend([0x10,0x00]); return bytes(p)

def _build_heroic_req(uid):
    p = bytearray([0x08]); p.extend(encode_varint(int(uid)))
    p.append(0x10); p.append(0x01); return bytes(p)

def _query_endpoint(jwt, path, plain_body, s, verbose=False):
    payload = aes_encrypt(plain_body)
    for host in CLIENT_HOSTS:
        url = f"https://{host}/{path}"
        for xga in (_get_xga(1792293041), str(int(time.time()))):
            headers = {"Accept":"*/*","Accept-Encoding":"deflate, gzip",
                       "Authorization":f"Bearer {jwt}","Content-Length":str(len(payload)),
                       "Content-Type":"application/x-www-form-urlencoded","Host":host,
                       "ReleaseVersion":_OB_VERSION,"User-Agent":"UnityPlayer/2018.4.12f1",
                       "X-GA":"v1 1","X-GA-SV":xga,"X-Unity-Version":"2018.4.12f1"}
            try:
                r = s.post(url, headers=headers, data=payload, timeout=10, verify=False)
                if r.status_code == 200: return decode_best(r.content or b"")
            except Exception: continue
    return None

def query_occupation(jwt, uid, s, verbose=False):
    return _query_endpoint(jwt, "QueryOccupationDetail", _build_request_simple(uid), s)

def query_personal_show(jwt, uid, s, verbose=False):
    return _query_endpoint(jwt, "GetPlayerPersonalShow", _build_personal_show_req(uid), s)

def query_player_stats(jwt, uid, s, verbose=False):
    return _query_endpoint(jwt, "GetPlayerStats", _build_stats_req(uid), s)

def query_heroic(jwt, uid, s, verbose=False):
    return _query_endpoint(jwt, "GetHeroicInfo", _build_heroic_req(uid), s)

def query_wishlist(jwt, uid, s, verbose=False):
    return _query_endpoint(jwt, "GetWishListItems", _build_request_simple(uid), s)

def query_outfit(jwt, uid, s, verbose=False):
    return _query_endpoint(jwt, "GetAccountOutfit", _build_request_simple(uid), s)

# ═══════════════════════════════════════════════════════════════════════════
#  8. SETUP — ⭐ login section replaced with try.py flow
# ═══════════════════════════════════════════════════════════════════════════
def setup_account(uid, password, region="IND", verbose=False):
    s = get_session(); region = (region or "IND").upper()
    lang = REGION_LANG.get(region, "en")

    result = {
        "uid": uid, "region": region, "status": "FAIL",
        "account_id": None, "nickname": "",
        "jwt": "", "open_id": "", "access_token": "",
        "region_bound": False, "newbie": False, "sealed": False,
        "roles_given": False,
        "preset_before": None, "preset_after": None,
        "preset_unlocked": False, "preset_items": [],
        "occupation": None, "personal_show": None,
        "stats": None, "heroic": None, "outfit": None, "wishlist": None,
        "game_server": None, "chat_server": None,
        "aes_key": None, "aes_iv": None,
        "date_run": now_str(),
    }

    # ⭐ STEP 1: token grant (try.py)
    g = grant_guest(uid, password, s, verbose=verbose)
    if not g:
        if verbose: print("  ✗ grant_guest failed")
        return result
    result["open_id"] = g["open_id"]; result["access_token"] = g["access_token"]
    platform = g.get("platform", 4)

    # ⭐ STEP 2: major_login (try.py)
    lr = major_login(uid, region, g["access_token"], g["open_id"], lang, s, verbose=verbose)
    if not lr:
        if verbose: print("  ✗ major_login failed")
        return result
    result["jwt"] = lr["jwt"]
    result["account_id"] = lr.get("account_id")
    result["nickname"] = lr.get("nickname", "")
    result["aes_key"] = lr.get("aes_key").hex() if isinstance(lr.get("aes_key"), bytes) else lr.get("aes_key")
    result["aes_iv"]  = lr.get("aes_iv").hex()  if isinstance(lr.get("aes_iv"),  bytes) else lr.get("aes_iv")
    jwt = lr["jwt"]

    # ⭐ STEP 3: GetLoginData for game_server/chat_server (try.py)
    ld = get_login_data_try(jwt, g["access_token"], g["open_id"], region, s, verbose=verbose)
    if ld:
        result["game_server"] = _ld_get(ld, 14)
        result["chat_server"] = _ld_get(ld, 32)

    # ── region lock check (from try.py)
    try:
        pl = decode_jwt_payload(jwt)
        lock_reg = (pl.get("lock_region") or region).upper()
        if lock_reg != region:
            region = lock_reg
            result["region"] = region
            lang = REGION_LANG.get(region, "en")
            lr = major_login(uid, region, g["access_token"], g["open_id"], lang, s, verbose=verbose)
            if lr:
                result["jwt"] = lr["jwt"]
                result["account_id"] = lr.get("account_id")
                result["aes_key"] = lr.get("aes_key").hex() if isinstance(lr.get("aes_key"), bytes) else lr.get("aes_key")
                result["aes_iv"]  = lr.get("aes_iv").hex()  if isinstance(lr.get("aes_iv"),  bytes) else lr.get("aes_iv")
                jwt = lr["jwt"]
                ld = get_login_data_try(jwt, g["access_token"], g["open_id"], region, s, verbose=verbose)
                if ld:
                    result["game_server"] = _ld_get(ld, 14)
                    result["chat_server"] = _ld_get(ld, 32)
    except Exception:
        pass

    # ── legacy region_bind / newbie (optional, best-effort) ────────────────
    try: result["region_bound"] = choose_region(jwt, region, s, verbose=verbose)
    except Exception: pass
    try: result["newbie"] = choose_newbie(jwt, s, verbose=verbose)
    except Exception: pass
    # 'sealed' was the old GetLoginData — now redundant, keep True
    result["sealed"] = bool(result.get("game_server"))

    # ── newbie roles ───────────────────────────────────────────────────────
    try:
        r = give_newbie_roles(jwt, s)
        result["roles_given"] = (r == "ok")
    except Exception: pass

    # ── presets ────────────────────────────────────────────────────────────
    try:
        profs = get_profiles(jwt, s)
        result["preset_before"] = next((p["id"] for p in profs if p["active"]), None)

        for label, body_hex in PRESET_STEPS:
            select_preset_loadout(jwt, s, body_hex)

        profs_after = get_profiles(jwt, s)
        result["preset_after"] = next((p["id"] for p in profs_after if p["active"]), None)
        for p in profs_after:
            if p["id"] == PRESET_ID:
                result["preset_items"] = p["items"]
                result["preset_unlocked"] = True
    except Exception: pass

    # ── info queries ───────────────────────────────────────────────────────
    try: result["occupation"]    = query_occupation(jwt, int(uid), s)
    except Exception: pass
    try: result["personal_show"] = query_personal_show(jwt, int(uid), s)
    except Exception: pass
    try: result["stats"]         = query_player_stats(jwt, int(uid), s)
    except Exception: pass
    try: result["heroic"]        = query_heroic(jwt, int(uid), s)
    except Exception: pass
    try: result["outfit"]        = query_outfit(jwt, int(uid), s)
    except Exception: pass
    try: result["wishlist"]      = query_wishlist(jwt, int(uid), s)
    except Exception: pass

    if result["account_id"] and result["jwt"]:
        result["status"] = "SUCCESS"
    return result

# ── legacy choose_region/choose_newbie (unchanged, best-effort) ────────────
def choose_region(jwt, region, s, verbose=False):
    body = aes_encrypt(encode_varint((1 << 3) | 2) + encode_varint(len(region.upper())) + region.upper().encode())
    for host in LOGIN_HOSTS:
        url = f"https://{host}/ChooseRegion"
        h = {"User-Agent":"UnityPlayer/2018.4.12f1","Connection":"Keep-Alive","Accept-Encoding":"gzip",
             "Content-Type":"application/x-www-form-urlencoded","Expect":"100-continue",
             "Authorization":f"Bearer {jwt}","X-Unity-Version":"2018.4.12f1",
             "X-GA":"v1 1","X-GA-SV":str(int(time.time())),
             "ReleaseVersion":_OB_VERSION,"Host":host}
        try:
            if s.post(url, data=body, headers=h, timeout=8, verify=False).status_code == 200:
                return True
        except Exception: continue
    return False

def choose_newbie(jwt, s, verbose=False):
    body = bytes.fromhex("3CE3A025334E4E014643A74B16ADB058")
    for host in LOGIN_HOSTS:
        url = f"https://{host}/ChooseNewbieChoice"
        h = {"Accept":"*/*","Accept-Encoding":"deflate, gzip","Authorization":f"Bearer {jwt}",
             "Content-Length":str(len(body)),"Content-Type":"application/x-www-form-urlencoded",
             "Host":host,"ReleaseVersion":_OB_VERSION,"User-Agent":"UnityPlayer/2018.4.12f1",
             "X-GA":"v1 1","X-GA-SV":"1791524202","X-Unity-Version":"2018.4.12f1"}
        try:
            if s.post(url, headers=h, data=body, timeout=8, verify=False).status_code == 200:
                return True
        except Exception: continue
    return False

# ── 9. FLASK APP (unchanged) ───────────────────────────────────────────────
from flask import Flask, request, jsonify

app = Flask(__name__)

def _serialize(obj):
    if isinstance(obj, dict):
        return {str(k): _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]
    if isinstance(obj, bytes):
        try: return obj.decode('utf-8', errors='replace')
        except Exception: return obj.hex()
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    return str(obj)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "api": BRAND,
        "dev": DEV_HANDLE,
        "usage": "/jxe/act?uid=UID&password=PASS&region=IND",
    })

@app.route("/jxe/act", methods=["GET"])
def act():
    uid = request.args.get("uid")
    password = request.args.get("password")
    region = (request.args.get("region") or "IND").upper()

    if not uid or not password:
        return jsonify({"status": "FAIL", "error": "missing uid or password"}), 400

    t0 = time.time()
    try:
        result = setup_account(uid, password, region=region, verbose=False)
    except Exception as e:
        return jsonify({"status": "ERROR", "uid": uid,
                        "error": f"{type(e).__name__}: {e}"}), 500

    out = _serialize(result)
    out["elapsed_s"] = round(time.time() - t0, 3)
    return jsonify(out)

handler = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)