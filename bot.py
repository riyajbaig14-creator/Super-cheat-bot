import os
import sys
import time
import json
import random
import string
import asyncio
import unicodedata
import re
import shutil
import logging
import traceback
from datetime import datetime
from pyrogram import Client, filters, idle
from pyrogram.types import (
    ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton,
    Message, CallbackQuery
)
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid, FloodWait

# ====================================================================
# LOGGING CONFIGURATION
# ====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_errors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ====================================================================
# CONFIGURATION
# ====================================================================
API_ID = 31103613
API_HASH = "3e836a34d6c0ff25ab2c99ed00a754df"
BOT_TOKEN = "8583790049:AAG8VY-1WumJhfHn52fLwFS9sl7b3KSQcR8"
OWNER_ID = 5674825926,6774356389
DATABASE_FILE = "database.json"
BACKUP_DIR = "Backups"
SESSION_NAME = "ULTRA_FINAL_BOT_V59_HYBRID"

# ====================================================================
# SMART ALERT SYSTEM
# ====================================================================
class SmartAlerter:
    def __init__(self):
        self.schedule = [0, 4*3600, 8*3600, 16*3600, 5*3600]
        self.stage = 0
        self.last_alert = 0

    def check(self):
        now = time.time()
        wait_time = self.schedule[min(self.stage, len(self.schedule)-1)]
        if now - self.last_alert >= wait_time:
            self.last_alert = now
            if self.stage < len(self.schedule) - 1:
                self.stage += 1
            return True
        return False

ALERTER = SmartAlerter()

# ====================================================================
# DATABASE MANAGER (enhanced with error handling)
# ====================================================================
DATA = {}

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def save_data_to_disk():
    for i in range(10):
        try:
            ensure_backup_dir()
            temp_file = DATABASE_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(DATA, f, indent=4, ensure_ascii=False)
            os.replace(temp_file, DATABASE_FILE)

            # Auto backup (10% chance)
            if random.randint(1, 10) == 5:
                ts = int(time.time())
                backup_path = os.path.join(BACKUP_DIR, f"auto_{ts}.json")
                shutil.copy(DATABASE_FILE, backup_path)
                files = sorted(os.listdir(BACKUP_DIR))
                if len(files) > 15:
                    os.remove(os.path.join(BACKUP_DIR, files[0]))
            return
        except Exception as e:
            logger.error(f"Error saving database (attempt {i+1}): {e}")
            time.sleep(0.5)
    logger.critical("Failed to save database after multiple attempts.")

def load_data():
    global DATA
    if not os.path.exists(DATABASE_FILE):
        ensure_backup_dir()
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.json')], key=lambda f: os.path.getctime(os.path.join(BACKUP_DIR, f)))
        if backups:
            logger.info(f"Restoring from backup: {backups[-1]}")
            shutil.copy(os.path.join(BACKUP_DIR, backups[-1]), DATABASE_FILE)

    loaded = False
    for i in range(5):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                DATA = json.load(f)
            loaded = True
            break
        except Exception as e:
            logger.error(f"Error loading database (attempt {i+1}): {e}")
            time.sleep(0.1)

    if not loaded:
        logger.warning("Creating new database.")
        # Fresh database with all required fields
        DATA = {
            "bot_on": True,
            "force_join": False,
            "post_join": True,
            "verify_on": False,
            "refer_on": False,
            "refer_limit": 10,
            "key_format": 1,
            "ui_style": 1,
            "custom_style_symbol": "🔥",
            "gate_link": "https://google.com",
            "start_text": "Welcome {name}! CLICK HERE to continue.",
            "start_photo": None,
            "refer_text": "Refer friends to unlock the key!",
            "refer_photo": None,
            "verify_text": "Join these channels to verify yourself:",
            "verify_photo": None,
            "key_broadcast_msg": "Success! Here is your key: `{key}`",
            "key_file": None,
            "slots": [],               # main force-join slots
            "verify_slots": [],         # additional verify slots
            "admins": {str(OWNER_ID): {"name": "Owner", "username": "Owner"}},
            "users": {},                # user_id -> {"refs":0, "passed_slots":[], "passed_verify":[], "reached_key":False, "join_date":str}
            "used_keys": [],
            "join_log": [],             # last 50 joins {id, name, username, date}
            "slot_stats": {},            # per slot index -> count of unique users who passed
            "verify_stats": {},          # per verify slot index -> count
            "sys_stats": {"errors": 0, "fixes": 0, "restarts": 0},
            "last_boot": 0,
            # Custom button texts
            "gen_button_text": "💀 GENERATE YOUR KEY 💀",
            "verify_button_text": "✅ VERIFY JOINED",
            # Support username (default to owner)
            "support_username": DATA.get("admins", {}).get(str(OWNER_ID), {}).get("username", "Owner")
        }
        try:
            with open(DATABASE_FILE, "w", encoding="utf-8") as f:
                json.dump(DATA, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not create new database: {e}")

load_data()
STATE = {}  # user_id -> {"mode":..., "ctx":...}
app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ====================================================================
# STYLES ENGINE
# ====================================================================
STYLES = {
    1: "Normal", 2: "Bold", 3: "Italic", 4: "Monospace",
    5: "Strike", 6: "Underline", 7: "Bold + Italic",
    8: "Bold + Underline", 9: "Bold + Strike", 10: "Italic + Underline",
    11: "Mono + Bold", 12: "Bold + Emoji ⚡", 13: "Italic + Emoji 💎",
    14: "Quote", 15: "Spoiler", 99: "Custom UI"
}

def normalize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def apply_style(text, user=None, link_url=None):
    style = DATA.get("ui_style", 1)
    if user:
        first = user.first_name or ""
        last = user.last_name or ""
        fullname = f"{first} {last}".strip()
        username = f"@{user.username}" if user.username else "No Username"
        uid = str(user.id)
        text = text.replace("{name}", fullname).replace("{username}", username).replace("{id}", uid)

    # Link handling
    marker = "||LNK||"
    processed_text = text
    has_link = False
    if link_url:
        clean_text = normalize_text(text)
        if re.search(r"(click[\s\W]*here|{link})", clean_text, re.IGNORECASE):
            processed_text = re.sub(r"(click[\s\W]*here|{link}|𝐂𝐋𝐈𝐂𝐊[\s\W]*𝐇𝐄𝐑𝐄|𝗖𝗟𝗜𝗖𝗞[\s\W]*𝗛𝗘𝗥𝗘|𝘾𝙇𝙄𝘾𝙆[\s\W]*𝙃𝙀𝙍𝙀)", marker, text, flags=re.IGNORECASE)
            has_link = True

    # Apply style
    if style == 1: final = processed_text
    elif style == 2: final = f"**{processed_text}**"
    elif style == 3: final = f"__{processed_text}__"
    elif style == 4: final = f"`{processed_text}`"
    elif style == 5: final = f"~~{processed_text}~~"
    elif style == 6: final = f"--{processed_text}--"
    elif style == 7: final = f"**__{processed_text}__**"
    elif style == 8: final = f"**--{processed_text}--**"
    elif style == 9: final = f"**~~{processed_text}~~**"
    elif style == 10: final = f"__--{processed_text}--__"
    elif style == 11: final = f"**`{processed_text}`**"
    elif style == 12: final = f"⚡ **{processed_text}** ⚡"
    elif style == 13: final = f"💎 __{processed_text}__ 💎"
    elif style == 14: final = f"> {processed_text}"
    elif style == 15: final = f"||{processed_text}||"
    elif style == 99:
        sym = DATA.get("custom_style_symbol", "✨")
        final = f"{sym} {processed_text} {sym}"
    else:
        final = processed_text

    if link_url and has_link:
        link_md = f"[CLICK HERE]({link_url})"
        final = final.replace(f"`{marker}`", link_md) \
                     .replace(f"**{marker}**", link_md) \
                     .replace(f"__{marker}__", link_md) \
                     .replace(marker, link_md)

    return final

def make_bar(curr, total):
    if total == 0:
        total = 1
    perc = min(curr / total, 1.0)
    filled = int(10 * perc)
    return f"[{'■'*filled}{'□'*(10-filled)}] {int(perc*100)}%"

# ====================================================================
# KEYBOARDS (improved layout: 2 buttons per row)
# ====================================================================
PAGE1_KB = ReplyKeyboardMarkup([
    ["🟢 Bot ON", "🔴 Bot OFF"],
    ["🔐 Force Join ON", "🔓 Force Join OFF"],
    ["📤 Post Join ON", "📥 Post Join OFF"],
    ["✅ Verify ON", "❌ Verify OFF"],
    ["➕ Add Slot", "➖ Remove Slot"],
    ["🔗 Set Channel", "❌ Remove Gate Link"],
    ["✏️ Edit Slot Name", "🌐 Set Gate Link"],
    ["📦 Slot Status", "📡 Channel Status"],
    ["📝 Set Start Text", "🖼 Set Start Photo"],
    ["📣 Broadcast", "🛠 Error Report"],
    ["👥 Bot Members", "📊 Bot Analytics"],
    ["♻️ Restart Bot", "➡️ Page 2"]
], resize_keyboard=True)

PAGE2_KB = ReplyKeyboardMarkup([
    ["➕ Add Admin", "➖ Remove Admin"],
    ["👑 Admin Status"],
    ["✅ Verify Channel Add", "❌ Verify Channel Remove"],
    ["✏️ Edit Verify Channel Name", "🔗 Set Verify Channel Link"],
    ["📝 Set Verify Text", "🖼 Set Verify Photo"],
    ["✏️ Set Gen Button Text", "✏️ Set Verify Button Text"],
    ["🔁 Refer ON", "⛔ Refer OFF"],
    ["✍️ Refer Set Text", "🖼 Refer Set Photo"],
    ["🔢 Set Refer Limit", "🔐 Set Key Format"],
    ["📊 Slot Stats", "📊 Join Log"],
    ["📊 System Stats", "📊 Stats Overview"],
    ["📋 Join Info", "🎨 Set UI Style"],
    ["🔧 Set Support Username", "🗑 Delete Key File"],
    ["⬅️ Back"]
], resize_keyboard=True)

# Referral keyboard (as per user's specification)
REFER_KB = ReplyKeyboardMarkup([
    ["💰 My Balance"],
    ["👥 Referral", "🔐 Get Key"],
    ["💬 Support"]
], resize_keyboard=True)

def get_slot_buttons(user_id, mode="slots"):
    buttons = []
    source = DATA["verify_slots"] if mode == "verify" else DATA["slots"]
    row = []
    for i, slot in enumerate(source):
        emo = "💎" if mode == "verify" else "🚀"
        btn_txt = f"{slot['name']} {emo}"
        row.append(InlineKeyboardButton(btn_txt, url=slot['url']))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    if mode == "verify":
        button_text = DATA.get("verify_button_text", "✅ VERIFY JOINED")
        buttons.append([InlineKeyboardButton(button_text, callback_data="check_verify")])
    else:
        button_text = DATA.get("gen_button_text", "💀 GENERATE YOUR KEY 💀")
        buttons.append([InlineKeyboardButton(button_text, callback_data="check_slots")])
    return InlineKeyboardMarkup(buttons)

def generate_key():
    fmt = DATA["key_format"]
    if fmt == 1:
        key = str(random.randint(100000000, 999999999))
    elif fmt == 2:
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    else:
        key = f"USER-{''.join(random.choices(string.ascii_uppercase, k=5))} PASS-{''.join(random.choices(string.digits, k=5))}"
    if key not in DATA["used_keys"]:
        DATA["used_keys"].append(key)
        return key
    return generate_key()

# ====================================================================
# HELPER FUNCTIONS (membership checks with counters)
# ====================================================================
async def check_membership_and_count(c, user_id, slot_list, slot_type):
    """
    Returns (not_joined_names, newly_passed_indices)
    slot_type: 'slots' or 'verify'
    Updates counters for slots where user just passed.
    """
    not_joined = []
    newly_passed = []
    user_str = str(user_id)
    user_data = DATA["users"].get(user_str, {})
    passed_key = f"passed_{slot_type}"  # e.g. "passed_slots"
    if passed_key not in user_data:
        user_data[passed_key] = []

    for idx, slot in enumerate(slot_list):
        # Skip if already counted for this slot
        if idx in user_data[passed_key]:
            continue

        # Try to check membership
        member = False
        if slot.get("id"):
            try:
                await c.get_chat_member(slot["id"], user_id)
                member = True
            except UserNotParticipant:
                member = False
            except (ChatAdminRequired, PeerIdInvalid, FloodWait) as e:
                # Bot not in channel or other error -> treat as not joined
                member = False
                logger.warning(f"Membership check failed for slot {idx}: {e}")
        else:
            # No chat ID stored, maybe it's a public link only - we cannot verify
            # For safety, treat as not joined
            member = False

        if not member:
            not_joined.append(slot['name'])
        else:
            # User is member, count if not already counted
            newly_passed.append(idx)
            user_data[passed_key].append(idx)
            # Increment slot stat
            stat_key = f"{slot_type}_stats"
            if stat_key not in DATA:
                DATA[stat_key] = {}
            str_idx = str(idx)
            DATA[stat_key][str_idx] = DATA[stat_key].get(str_idx, 0) + 1

    # Save updated user data
    DATA["users"][user_str] = user_data
    save_data_to_disk()
    return not_joined, newly_passed

# ====================================================================
# PAGE RENDERING FUNCTIONS
# ====================================================================
async def send_force_join_page(c, m):
    txt = apply_style(DATA["start_text"], m.from_user, DATA["gate_link"])
    kb = get_slot_buttons(m.from_user.id, "slots")

    if DATA["start_photo"]:
        try:
            await m.reply_photo(DATA["start_photo"], caption=txt, reply_markup=kb)
        except Exception as e:
            logger.error(f"Error sending start photo: {e}")
            DATA["start_photo"] = None
            save_data_to_disk()
            await m.reply(txt, reply_markup=kb, disable_web_page_preview=True)
    else:
        await m.reply(txt, reply_markup=kb, disable_web_page_preview=True)

async def send_verify_page(c, m_or_q):
    is_cb = isinstance(m_or_q, CallbackQuery)
    target = m_or_q.message if is_cb else m_or_q
    txt = apply_style(DATA["verify_text"], m_or_q.from_user)
    kb = get_slot_buttons(m_or_q.from_user.id, "verify")

    if DATA["verify_photo"]:
        try:
            if is_cb:
                await target.delete()
                await target.reply_photo(DATA["verify_photo"], caption=txt, reply_markup=kb)
            else:
                await target.reply_photo(DATA["verify_photo"], caption=txt, reply_markup=kb)
        except Exception as e:
            logger.error(f"Error sending verify photo: {e}")
            if is_cb:
                await target.edit_text(txt, reply_markup=kb, disable_web_page_preview=True)
            else:
                await target.reply(txt, reply_markup=kb)
    else:
        if is_cb:
            await target.edit_text(txt, reply_markup=kb, disable_web_page_preview=True)
        else:
            await target.reply(txt, reply_markup=kb)

async def send_refer_interface(c, m_or_q):
    is_cb = isinstance(m_or_q, CallbackQuery)
    target = m_or_q.message if is_cb else m_or_q

    raw = DATA.get("refer_text", "Refer friends to unlock!")
    txt = apply_style(raw, m_or_q.from_user)

    # Generate referral link
    bot_username = (await c.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={m_or_q.from_user.id}"
    txt += f"\n\n🔗 **Your referral link:**\n`{ref_link}`"

    if is_cb:
        await target.delete()
        if DATA["refer_photo"]:
            try:
                await target.reply_photo(DATA["refer_photo"], caption=txt, reply_markup=REFER_KB)
            except Exception as e:
                logger.error(f"Error sending refer photo: {e}")
                await target.reply(txt, reply_markup=REFER_KB)
        else:
            await target.reply(txt, reply_markup=REFER_KB)
    else:
        if DATA["refer_photo"]:
            try:
                await target.reply_photo(DATA["refer_photo"], caption=txt, reply_markup=REFER_KB)
            except Exception as e:
                logger.error(f"Error sending refer photo: {e}")
                await target.reply(txt, reply_markup=REFER_KB)
        else:
            await target.reply(txt, reply_markup=REFER_KB)

async def send_final_key(c, m_or_q):
    is_cb = isinstance(m_or_q, CallbackQuery)
    target = m_or_q.message if is_cb else m_or_q

    # Check if key is configured
    if not DATA.get("key_broadcast_msg") and not DATA.get("key_file"):
        await target.reply("❌ **Key not configured.** Please contact admin.")
        return

    key = generate_key()
    template = DATA.get("key_broadcast_msg", "Key: {key}")
    msg = template.replace("{key}", key)
    msg = apply_style(msg, m_or_q.from_user)

    file_id = DATA.get("key_file")
    success_prefix = "✅ **Success!**\n\n" if DATA["post_join"] else ""

    if file_id:
        try:
            await target.reply_document(file_id, caption=f"{success_prefix}{msg}")
        except Exception as e:
            logger.error(f"Error sending key file: {e}")
            await target.reply(f"{success_prefix}{msg}")
    else:
        await target.reply(f"{success_prefix}{msg}")

    # Mark user as reached key
    uid = str(m_or_q.from_user.id)
    if uid in DATA["users"]:
        DATA["users"][uid]["reached_key"] = True
        save_data_to_disk()

# ====================================================================
# ERROR HANDLER DECORATOR (for all handlers)
# ====================================================================
def error_handler(func):
    async def wrapper(client, update, *args, **kwargs):
        try:
            return await func(client, update, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Unhandled exception in {func.__name__}: {e}")
            # Optionally notify owner (if smart alerter allows)
            if ALERTER.check():
                try:
                    await client.send_message(OWNER_ID, f"⚠️ **Error in {func.__name__}:**\n`{str(e)[:200]}`")
                except:
                    pass
            # Continue execution (don't crash)
    return wrapper

# ====================================================================
# CALLBACK HANDLERS
# ====================================================================
@app.on_callback_query()
@error_handler
async def cb_handler(c, q):
    uid = str(q.from_user.id)
    data = q.data

    if data == "check_slots":
        if DATA["force_join"]:
            not_joined, newly_passed = await check_membership_and_count(c, q.from_user.id, DATA["slots"], "slots")
            if not_joined:
                return await q.answer(f"⚠️ Please join: {', '.join(not_joined)}", show_alert=True)

        # Proceed to next step
        if DATA["verify_on"]:
            await send_verify_page(c, q)
        elif DATA["refer_on"]:
            await send_refer_interface(c, q)
        else:
            await send_final_key(c, q)

    elif data == "check_verify":
        if DATA["verify_on"]:
            not_joined, newly_passed = await check_membership_and_count(c, q.from_user.id, DATA["verify_slots"], "verify")
            if not_joined:
                return await q.answer(f"❌ Join {', '.join(not_joined)} first!", show_alert=True)

        if DATA["refer_on"]:
            await send_refer_interface(c, q)
        else:
            await send_final_key(c, q)

    # Broadcast callbacks
    elif data == "bc_key_msg":
        STATE[uid] = {"mode": "set_key_broadcast"}
        await q.message.reply("✍️ **Set Key Message:**\nUse `{key}` placeholder.")
        await q.answer()
    elif data == "bc_key_file":
        STATE[uid] = {"mode": "set_key_file"}
        await q.message.reply("📂 **Send the file (APK, video, photo, etc.):**")
        await q.answer()
    elif data == "bc_univ":
        STATE[uid] = {"mode": "bc_univ"}
        await q.message.reply("📢 **Send the message to broadcast to ALL users:**")
        await q.answer()
    elif data == "bc_admin":
        STATE[uid] = {"mode": "bc_admin"}
        await q.message.reply("👮 **Send the message to broadcast to ADMINS:**")
        await q.answer()

    # Style selection
    elif data == "custom_style_input":
        STATE[uid] = {"mode": "set_custom_style"}
        await q.message.reply("🎨 **Send the symbol you want to use:**")
        await q.answer()
    elif data.startswith("style_"):
        sid = int(data.split("_")[1])
        DATA["ui_style"] = sid
        save_data_to_disk()
        await q.answer(f"Style: {STYLES.get(sid)}")
        await q.message.edit_text(f"✅ **Style Set:** {STYLES.get(sid)}")

    # Slot removal
    elif data.startswith("rm_slot_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(DATA["slots"]):
            removed = DATA["slots"].pop(idx)
            save_data_to_disk()
            await q.answer(f"🗑 Removed slot: {removed['name']}")
            await show_status(c, q.message, "slots")
        else:
            await q.answer("❌ Invalid slot")
    elif data.startswith("rm_v_slot_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(DATA["verify_slots"]):
            removed = DATA["verify_slots"].pop(idx)
            save_data_to_disk()
            await q.answer(f"🗑 Removed verify slot: {removed['name']}")
            await show_status(c, q.message, "verify")
        else:
            await q.answer("❌ Invalid slot")

    # Admin removal
    elif data.startswith("rm_admin_"):
        aid = data.split("_")[2]
        if aid in DATA["admins"] and aid != str(OWNER_ID):
            del DATA["admins"][aid]
            save_data_to_disk()
            await q.message.delete()
            await q.message.reply("✅ Admin removed")
        else:
            await q.answer("❌ Cannot remove owner or not found")

    # Edit verify channel name (step1)
    elif data.startswith("edit_v_name_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(DATA["verify_slots"]):
            STATE[uid] = {"mode": "edit_verify_name", "ctx": idx}
            await q.message.reply(f"✏️ Current name: {DATA['verify_slots'][idx]['name']}\nSend new name:")
            await q.answer()
        else:
            await q.answer("❌ Invalid slot")

    # Set verify channel link (step1)
    elif data.startswith("set_v_link_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(DATA["verify_slots"]):
            STATE[uid] = {"mode": "set_verify_link", "ctx": idx}
            await q.message.reply(f"🔗 Current link: {DATA['verify_slots'][idx]['url']}\nSend new link:")
            await q.answer()
        else:
            await q.answer("❌ Invalid slot")

# ====================================================================
# ADMIN & MESSAGE HANDLER
# ====================================================================
ALL_CMDS = [
    "🟢 Bot ON", "🔴 Bot OFF",
    "🔐 Force Join ON", "🔓 Force Join OFF",
    "📤 Post Join ON", "📥 Post Join OFF",
    "✅ Verify ON", "❌ Verify OFF",
    "➕ Add Slot", "➖ Remove Slot",
    "🔗 Set Channel", "❌ Remove Gate Link",
    "✏️ Edit Slot Name", "🌐 Set Gate Link",
    "📦 Slot Status", "📡 Channel Status",
    "📝 Set Start Text", "🖼 Set Start Photo",
    "📣 Broadcast", "🛠 Error Report",
    "👥 Bot Members", "📊 Bot Analytics",
    "♻️ Restart Bot", "➡️ Page 2",
    "➕ Add Admin", "➖ Remove Admin",
    "👑 Admin Status",
    "✅ Verify Channel Add", "❌ Verify Channel Remove",
    "✏️ Edit Verify Channel Name", "🔗 Set Verify Channel Link",
    "📝 Set Verify Text", "🖼 Set Verify Photo",
    "✏️ Set Gen Button Text", "✏️ Set Verify Button Text",
    "🔁 Refer ON", "⛔ Refer OFF",
    "✍️ Refer Set Text", "🖼 Refer Set Photo",
    "🔢 Set Refer Limit", "🔐 Set Key Format",
    "📊 Slot Stats", "📊 Join Log",
    "📊 System Stats", "📊 Stats Overview",
    "📋 Join Info", "🎨 Set UI Style",
    "🔧 Set Support Username", "🗑 Delete Key File",
    "⬅️ Back"
]

@app.on_message(filters.command("start") & filters.private)
@error_handler
async def start_handler(c, m):
    uid = str(m.from_user.id)
    STATE.pop(uid, None)

    # Referral logic
    if len(m.command) > 1:
        ref_id = m.command[1]
        if ref_id != uid and ref_id in DATA["users"] and uid not in DATA["users"]:
            DATA["users"][ref_id]["refs"] += 1
            save_data_to_disk()
            try:
                await c.send_message(ref_id, f"➕ **New Referral!**\nUser: {m.from_user.first_name}")
            except Exception as e:
                logger.error(f"Failed to send referral notification: {e}")

    # Register new user with join log
    if uid not in DATA["users"]:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        DATA["users"][uid] = {
            "refs": 0,
            "passed_slots": [],
            "passed_verify": [],
            "reached_key": False,
            "join_date": now
        }
        # Add to join log
        log_entry = {
            "id": uid,
            "name": m.from_user.first_name,
            "username": m.from_user.username,
            "date": now
        }
        DATA["join_log"].insert(0, log_entry)
        DATA["join_log"] = DATA["join_log"][:50]
        save_data_to_disk()

    # Maintenance check
    if not DATA["bot_on"] and uid not in DATA["admins"] and int(uid) != OWNER_ID:
        return await m.reply("❌ **Bot is under maintenance.**")

    await send_force_join_page(c, m)

@app.on_message(filters.command("admin") & filters.private)
@error_handler
async def admin_start(c, m):
    if str(m.from_user.id) in DATA["admins"] or m.from_user.id == OWNER_ID:
        STATE.pop(str(m.from_user.id), None)
        await m.reply("👑 **Admin Panel**", reply_markup=PAGE1_KB)
    else:
        await m.reply("⛔ Unauthorized")

@app.on_message(filters.private & (filters.text | filters.photo | filters.document | filters.video))
@error_handler
async def main_handler(c, m):
    uid = str(m.from_user.id)
    txt = m.text or ""

    # Navigation
    if txt == "⬅️ Back":
        await m.reply("🔙 Main Menu", reply_markup=PAGE1_KB)
        return
    elif txt == "➡️ Page 2":
        await m.reply("⚙️ Advanced Settings", reply_markup=PAGE2_KB)
        return

    # Admin commands
    if txt in ALL_CMDS:
        if uid in DATA["admins"] or uid == str(OWNER_ID):
            STATE.pop(uid, None)
            await handle_commands(c, m, uid, txt)
        else:
            await m.reply("⛔ Unauthorized")
        return

    # User commands (referral keyboard)
    if txt in ["💰 My Balance", "👥 Referral", "🔐 Get Key", "💬 Support"]:
        await handle_user_commands(c, m, uid, txt)
        return

    # State-based input
    if uid in STATE:
        mode = STATE[uid]["mode"]
        try:
            if mode == "set_custom_style":
                DATA["custom_style_symbol"] = txt.strip()
                DATA["ui_style"] = 99
                save_data_to_disk()
                await m.reply(f"✅ **Set!** Preview: {txt} Text {txt}")
                STATE.pop(uid)

            elif mode in ["set_start_photo", "set_refer_photo", "set_verify_photo"] and m.photo:
                fid = m.photo.file_id
                if mode == "set_start_photo":
                    DATA["start_photo"] = fid
                elif mode == "set_refer_photo":
                    DATA["refer_photo"] = fid
                elif mode == "set_verify_photo":
                    DATA["verify_photo"] = fid
                save_data_to_disk()
                await m.reply("✅ Photo saved!")
                STATE.pop(uid)

            elif mode == "set_key_file":
                if m.document or m.video or m.photo:
                    DATA["key_file"] = (m.document or m.video or m.photo).file_id
                    save_data_to_disk()
                    await m.reply("✅ File saved as key attachment!")
                    STATE.pop(uid)
                else:
                    await m.reply("❌ Please send a document, video, or photo.")

            elif mode == "set_start_text":
                DATA["start_text"] = txt
                save_data_to_disk()
                await m.reply("✅ Start text updated!")
                STATE.pop(uid)
            elif mode == "set_refer_text":
                DATA["refer_text"] = txt
                save_data_to_disk()
                await m.reply("✅ Refer text updated!")
                STATE.pop(uid)
            elif mode == "set_verify_text":
                DATA["verify_text"] = txt
                save_data_to_disk()
                await m.reply("✅ Verify text updated!")
                STATE.pop(uid)
            elif mode == "set_gate_link":
                clean = txt.strip()
                if not clean.startswith("http"):
                    clean = "https://" + clean
                DATA["gate_link"] = clean
                save_data_to_disk()
                await m.reply(f"✅ Gate link set to: {clean}")
                STATE.pop(uid)
            elif mode == "set_gen_button":
                DATA["gen_button_text"] = txt
                save_data_to_disk()
                await m.reply("✅ Generate button text updated!")
                STATE.pop(uid)
            elif mode == "set_verify_button":
                DATA["verify_button_text"] = txt
                save_data_to_disk()
                await m.reply("✅ Verify button text updated!")
                STATE.pop(uid)
            elif mode == "set_support_username":
                clean = txt.strip().replace("@", "")
                DATA["support_username"] = clean
                save_data_to_disk()
                await m.reply(f"✅ Support username set to: @{clean}")
                STATE.pop(uid)
            elif mode == "set_channel_step1":
                if not txt.isdigit():
                    return await m.reply("❌ Please send a valid slot number.")
                idx = int(txt) - 1
                if 0 <= idx < len(DATA["slots"]):
                    STATE[uid] = {"mode": "set_channel_step2", "ctx": idx}
                    await m.reply(f"🔗 Updating slot {txt}. Send the new link:")
                else:
                    await m.reply("❌ Slot number out of range.")
            elif mode == "set_channel_step2":
                idx = STATE[uid]["ctx"]
                new_url = txt.strip()
                DATA["slots"][idx]["url"] = new_url
                # Try to fetch chat info
                try:
                    if "t.me/" in new_url:
                        chat = await c.get_chat(new_url)
                        DATA["slots"][idx]["id"] = chat.id
                        DATA["slots"][idx]["name"] = chat.title
                except Exception as e:
                    logger.warning(f"Could not fetch chat info for {new_url}: {e}")
                save_data_to_disk()
                await m.reply("✅ Channel link updated!")
                STATE.pop(uid)
            elif mode == "edit_slot_name":
                if "ctx" not in STATE[uid]:
                    if not txt.isdigit():
                        return await m.reply("❌ Send slot number.")
                    idx = int(txt) - 1
                    if 0 <= idx < len(DATA["slots"]):
                        STATE[uid]["ctx"] = idx
                        await m.reply(f"✏️ Current name: {DATA['slots'][idx]['name']}\nSend new name:")
                    else:
                        await m.reply("❌ Invalid slot.")
                else:
                    idx = STATE[uid]["ctx"]
                    DATA["slots"][idx]["name"] = txt
                    save_data_to_disk()
                    await m.reply(f"✅ Slot name updated to: {txt}")
                    STATE.pop(uid)
            elif mode == "edit_verify_name":
                idx = STATE[uid]["ctx"]
                DATA["verify_slots"][idx]["name"] = txt
                save_data_to_disk()
                await m.reply(f"✅ Verify channel name updated to: {txt}")
                STATE.pop(uid)
            elif mode == "set_verify_link":
                idx = STATE[uid]["ctx"]
                new_url = txt.strip()
                DATA["verify_slots"][idx]["url"] = new_url
                try:
                    if "t.me/" in new_url:
                        chat = await c.get_chat(new_url)
                        DATA["verify_slots"][idx]["id"] = chat.id
                        DATA["verify_slots"][idx]["name"] = chat.title
                except Exception as e:
                    logger.warning(f"Could not fetch verify chat info: {e}")
                save_data_to_disk()
                await m.reply("✅ Verify channel link updated!")
                STATE.pop(uid)
            elif mode == "add_verify_channel":
                new_slot = {"name": f"Verify {len(DATA['verify_slots'])+1}", "url": txt, "id": 0}
                try:
                    if "t.me/" in txt:
                        chat = await c.get_chat(txt)
                        new_slot["id"] = chat.id
                        new_slot["name"] = chat.title
                except Exception as e:
                    logger.warning(f"Could not fetch verify chat info: {e}")
                DATA["verify_slots"].append(new_slot)
                save_data_to_disk()
                await m.reply("✅ Verify channel added!")
                STATE.pop(uid)
            elif mode == "add_admin":
                try:
                    user = await c.get_users(txt)
                    DATA["admins"][str(user.id)] = {"name": user.first_name, "username": user.username}
                    save_data_to_disk()
                    await m.reply("✅ Admin added!")
                except Exception as e:
                    await m.reply("❌ User not found.")
                STATE.pop(uid)
            elif mode == "remove_admin":
                try:
                    user = await c.get_users(txt)
                    aid = str(user.id)
                    if aid in DATA["admins"] and aid != str(OWNER_ID):
                        del DATA["admins"][aid]
                        save_data_to_disk()
                        await m.reply("✅ Admin removed.")
                    else:
                        await m.reply("❌ Cannot remove owner or admin not found.")
                except Exception as e:
                    await m.reply("❌ User not found.")
                STATE.pop(uid)
            elif mode == "set_refer_limit":
                try:
                    limit = int(txt)
                    if limit > 0:
                        DATA["refer_limit"] = limit
                        save_data_to_disk()
                        await m.reply(f"✅ Refer limit set to {limit}")
                    else:
                        await m.reply("❌ Limit must be positive.")
                except ValueError:
                    await m.reply("❌ Send a number.")
                STATE.pop(uid)
            elif mode == "set_key_broadcast":
                DATA["key_broadcast_msg"] = txt
                save_data_to_disk()
                await m.reply("✅ Key message updated!")
                STATE.pop(uid)
            elif mode == "bc_univ":
                asyncio.create_task(broadcast_msg(c, txt, "users", m.from_user.id))
                await m.reply("📢 Broadcasting to all users started.")
                STATE.pop(uid)
            elif mode == "bc_admin":
                asyncio.create_task(broadcast_msg(c, txt, "admins", m.from_user.id))
                await m.reply("👮 Broadcasting to admins started.")
                STATE.pop(uid)
        except Exception as e:
            logger.exception(f"Error in state mode {mode}: {e}")
            await m.reply("❌ An internal error occurred. Please try again.")
            STATE.pop(uid, None)

async def broadcast_msg(app, text, target_type, admin_id):
    count = 0
    failed = 0
    if target_type == "users":
        targets = list(DATA["users"].keys())
    else:
        targets = list(DATA["admins"].keys())
    for uid in targets:
        try:
            await app.send_message(int(uid), text)
            count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed for {uid}: {e}")
    try:
        await app.send_message(admin_id, f"✅ Broadcast finished.\nSent: {count}\nFailed: {failed}")
    except Exception as e:
        logger.error(f"Could not send broadcast report: {e}")

async def handle_commands(c, m, uid, cmd):
    try:
        # Toggles
        if cmd == "🟢 Bot ON":
            DATA["bot_on"] = True
            await m.reply("✅ Bot turned ON")
        elif cmd == "🔴 Bot OFF":
            DATA["bot_on"] = False
            await m.reply("❌ Bot turned OFF")
        elif cmd == "🔐 Force Join ON":
            DATA["force_join"] = True
            await m.reply("✅ Force Join enabled")
        elif cmd == "🔓 Force Join OFF":
            DATA["force_join"] = False
            await m.reply("❌ Force Join disabled")
        elif cmd == "📤 Post Join ON":
            DATA["post_join"] = True
            await m.reply("✅ Post‑join message enabled")
        elif cmd == "📥 Post Join OFF":
            DATA["post_join"] = False
            await m.reply("❌ Post‑join message disabled")
        elif cmd == "✅ Verify ON":
            DATA["verify_on"] = True
            await m.reply("✅ Verification enabled")
        elif cmd == "❌ Verify OFF":
            DATA["verify_on"] = False
            await m.reply("❌ Verification disabled")
        elif cmd == "🔁 Refer ON":
            DATA["refer_on"] = True
            await m.reply("✅ Referral system enabled")
        elif cmd == "⛔ Refer OFF":
            DATA["refer_on"] = False
            await m.reply("❌ Referral system disabled")

        # Slot management
        elif cmd == "➕ Add Slot":
            new_idx = len(DATA["slots"]) + 1
            DATA["slots"].append({"name": f"Channel {new_idx}", "url": "https://google.com", "id": 0})
            save_data_to_disk()
            await m.reply(f"✅ Slot added. Total slots: {new_idx}\nUse '🔗 Set Channel' to configure.")
        elif cmd == "➖ Remove Slot":
            if not DATA["slots"]:
                await m.reply("📭 No slots to remove.")
            else:
                btns = [[InlineKeyboardButton(f"Remove {i+1}: {s['name']}", callback_data=f"rm_slot_{i}")] for i, s in enumerate(DATA["slots"])]
                await m.reply("🗑 Select slot to remove:", reply_markup=InlineKeyboardMarkup(btns))
        elif cmd == "🔗 Set Channel":
            if not DATA["slots"]:
                await m.reply("⚠️ No slots exist. Use '➕ Add Slot' first.")
            else:
                STATE[uid] = {"mode": "set_channel_step1"}
                slot_list = "\n".join([f"{i+1}. {s['name']}" for i, s in enumerate(DATA["slots"])])
                await m.reply(f"📋 Existing slots:\n{slot_list}\n\nSend the slot number you want to update:")
        elif cmd == "❌ Remove Gate Link":
            DATA["gate_link"] = ""
            save_data_to_disk()
            await m.reply("❌ Gate link removed.")
        elif cmd == "✏️ Edit Slot Name":
            if not DATA["slots"]:
                await m.reply("⚠️ No slots to rename.")
            else:
                STATE[uid] = {"mode": "edit_slot_name"}
                slot_list = "\n".join([f"{i+1}. {s['name']}" for i, s in enumerate(DATA["slots"])])
                await m.reply(f"📋 Slots:\n{slot_list}\n\nSend the slot number to rename:")
        elif cmd == "🌐 Set Gate Link":
            STATE[uid] = {"mode": "set_gate_link"}
            await m.reply("🔗 Send the new gate link (e.g., https://example.com):")
        elif cmd == "📦 Slot Status" or cmd == "📡 Channel Status":
            await show_status(c, m, "slots")

        # Text/Photo settings
        elif cmd == "📝 Set Start Text":
            STATE[uid] = {"mode": "set_start_text"}
            await m.reply("✍️ Send the new start text. Use `{name}`, `{username}`, `{id}` as placeholders.")
        elif cmd == "🖼 Set Start Photo":
            STATE[uid] = {"mode": "set_start_photo"}
            await m.reply("📸 Send the new start photo.")
        elif cmd == "📝 Set Verify Text":
            STATE[uid] = {"mode": "set_verify_text"}
            await m.reply("✍️ Send the new verify text.")
        elif cmd == "🖼 Set Verify Photo":
            STATE[uid] = {"mode": "set_verify_photo"}
            await m.reply("📸 Send the new verify photo.")
        elif cmd == "✍️ Refer Set Text":
            STATE[uid] = {"mode": "set_refer_text"}
            await m.reply("✍️ Send the new referral text.")
        elif cmd == "🖼 Refer Set Photo":
            STATE[uid] = {"mode": "set_refer_photo"}
            await m.reply("📸 Send the new referral photo.")

        # Button text customization
        elif cmd == "✏️ Set Gen Button Text":
            STATE[uid] = {"mode": "set_gen_button"}
            await m.reply("✍️ Send the new text for the GENERATE YOUR KEY button.")
        elif cmd == "✏️ Set Verify Button Text":
            STATE[uid] = {"mode": "set_verify_button"}
            await m.reply("✍️ Send the new text for the VERIFY JOINED button.")

        # Support username
        elif cmd == "🔧 Set Support Username":
            STATE[uid] = {"mode": "set_support_username"}
            await m.reply("👤 Send the support username (without @).")

        # Verify channels
        elif cmd == "✅ Verify Channel Add":
            STATE[uid] = {"mode": "add_verify_channel"}
            await m.reply("🔗 Send the link of the verify channel (public or private).")
        elif cmd == "❌ Verify Channel Remove":
            if not DATA["verify_slots"]:
                await m.reply("📭 No verify channels to remove.")
            else:
                btns = [[InlineKeyboardButton(f"Remove {i+1}: {s['name']}", callback_data=f"rm_v_slot_{i}")] for i, s in enumerate(DATA["verify_slots"])]
                await m.reply("🗑 Select verify channel to remove:", reply_markup=InlineKeyboardMarkup(btns))
        elif cmd == "✏️ Edit Verify Channel Name":
            if not DATA["verify_slots"]:
                await m.reply("📭 No verify channels to edit.")
            else:
                btns = [[InlineKeyboardButton(f"Edit {i+1}: {s['name']}", callback_data=f"edit_v_name_{i}")] for i, s in enumerate(DATA["verify_slots"])]
                await m.reply("✏️ Select verify channel to rename:", reply_markup=InlineKeyboardMarkup(btns))
        elif cmd == "🔗 Set Verify Channel Link":
            if not DATA["verify_slots"]:
                await m.reply("📭 No verify channels to edit.")
            else:
                btns = [[InlineKeyboardButton(f"Set Link {i+1}: {s['name']}", callback_data=f"set_v_link_{i}")] for i, s in enumerate(DATA["verify_slots"])]
                await m.reply("🔗 Select verify channel to update its link:", reply_markup=InlineKeyboardMarkup(btns))

        # Referral settings
        elif cmd == "🔢 Set Refer Limit":
            STATE[uid] = {"mode": "set_refer_limit"}
            await m.reply("🔢 Send the number of referrals required to get the key (e.g., 5).")
        elif cmd == "🔐 Set Key Format":
            DATA["key_format"] = (DATA["key_format"] % 3) + 1
            fmts = {1: "🔢 Numeric (9 digits)", 2: "🔤 Alphanumeric (8 chars)", 3: "👤 User + Pass"}
            save_data_to_disk()
            await m.reply(f"✅ Key format changed to: {fmts[DATA['key_format']]}")

        # Admin management
        elif cmd == "➕ Add Admin":
            STATE[uid] = {"mode": "add_admin"}
            await m.reply("👤 Send the user ID or username of the new admin.")
        elif cmd == "➖ Remove Admin":
            STATE[uid] = {"mode": "remove_admin"}
            await m.reply("👤 Send the user ID or username of the admin to remove (cannot remove owner).")
        elif cmd == "👑 Admin Status":
            msg = "👑 **Admins:**\n"
            for aid, info in DATA["admins"].items():
                msg += f"- {info['name']} (`{aid}`)\n"
            await m.reply(msg)

        # Broadcast menu
        elif cmd == "📣 Broadcast":
            btns = [
                [InlineKeyboardButton("🔑 Set Key Message", callback_data="bc_key_msg")],
                [InlineKeyboardButton("📂 Set Key File", callback_data="bc_key_file")],
                [InlineKeyboardButton("🌍 Broadcast to All Users", callback_data="bc_univ")],
                [InlineKeyboardButton("👮 Broadcast to Admins", callback_data="bc_admin")]
            ]
            await m.reply("📣 **Broadcast Menu**", reply_markup=InlineKeyboardMarkup(btns))

        # Stats
        elif cmd == "🛠 Error Report":
            s = DATA["sys_stats"]
            await m.reply(f"🔴 Errors: {s['errors']}\n🚑 Fixes: {s['fixes']}\n♻️ Restarts: {s['restarts']}")
        elif cmd == "👥 Bot Members":
            total = len(DATA["users"])
            active = sum(1 for u in DATA["users"] if DATA["users"][u].get("reached_key", False))
            await m.reply(f"👥 **Total users:** {total}\n🔑 **Have key:** {active}")
        elif cmd == "📊 Bot Analytics":
            keys = len(DATA["used_keys"])
            await m.reply(f"📊 **Keys generated:** {keys}")
        elif cmd == "📊 Slot Stats":
            if not DATA["slots"]:
                await m.reply("📭 No slots configured.")
            else:
                msg = " **Slot Member Counts (unique users who passed):**\n"
                for i, s in enumerate(DATA["slots"]):
                    count = DATA.get("slot_stats", {}).get(str(i), 0)
                    msg += f"{i+1}. {s['name']} : {count} users\n"
                await m.reply(msg)
        elif cmd == "📊 Join Log":
            if not DATA["join_log"]:
                await m.reply("📭 No join records yet.")
            else:
                msg = "🆕 **Recent joins:**\n"
                for entry in DATA["join_log"][:10]:
                    name = entry['name']
                    username = f"@{entry['username']}" if entry['username'] else "No username"
                    msg += f"• {name} ({username}) - {entry['date']}\n"
                await m.reply(msg)
        elif cmd == "📊 System Stats":
            total_users = len(DATA["users"])
            keys = len(DATA["used_keys"])
            slots = len(DATA["slots"])
            v_slots = len(DATA["verify_slots"])
            await m.reply(f"📊 **System Statistics**\n"
                          f"👥 Users: {total_users}\n"
                          f"🔑 Keys: {keys}\n"
                          f"🚀 Force slots: {slots}\n"
                          f"💎 Verify slots: {v_slots}\n"
                          f"📅 Last boot: {datetime.fromtimestamp(DATA['last_boot']).strftime('%Y-%m-%d %H:%M') if DATA['last_boot'] else 'Never'}")
        elif cmd == "📊 Stats Overview":
            keys = len(DATA["used_keys"])
            last_join = DATA["join_log"][0] if DATA["join_log"] else None
            msg = f"📊 **Overview**\n🔑 Keys Generated: {keys}\n"
            if last_join:
                msg += f"🆕 Last Join: {last_join['name']} (ID: {last_join['id']}) at {last_join['date']}\n"
            else:
                msg += "🆕 No joins yet.\n"
            msg += f"📦 Total Slots: {len(DATA['slots'])}\n💎 Verify Slots: {len(DATA['verify_slots'])}"
            await m.reply(msg)
        elif cmd == "📋 Join Info":
            if not DATA["join_log"]:
                await m.reply("📭 No join records.")
            else:
                entry = DATA["join_log"][0]  # latest
                msg = (f"🎁 **New User Joined!**\n\n"
                       f"ID User ID: {entry['id']}\n"
                       f"Username: {entry['username'] or 'None'}\n"
                       f"Join Number: {len(DATA['users'])}")  # total users as join number
                await m.reply(msg)

        # UI Style
        elif cmd == "🎨 Set UI Style":
            btns = []
            row = []
            for k, v in STYLES.items():
                if k == 99:
                    continue
                row.append(InlineKeyboardButton(v, callback_data=f"style_{k}"))
                if len(row) == 2:
                    btns.append(row)
                    row = []
            if row:
                btns.append(row)
            btns.append([InlineKeyboardButton("🎨 Custom UI", callback_data="custom_style_input")])
            await m.reply("🎨 Select a style:", reply_markup=InlineKeyboardMarkup(btns))

        # Delete key file
        elif cmd == "🗑 Delete Key File":
            DATA["key_file"] = None
            save_data_to_disk()
            await m.reply("🗑 Key file removed.")

        # Restart
        elif cmd == "♻️ Restart Bot":
            await m.reply("♻️ Restarting...")
            DATA["sys_stats"]["restarts"] += 1
            save_data_to_disk()
            os.execl(sys.executable, sys.executable, *sys.argv)

        # Back handled above
    except Exception as e:
        logger.exception(f"Error handling command {cmd}: {e}")
        await m.reply("❌ An error occurred while processing that command.")

async def show_status(c, m, type_):
    source = DATA["verify_slots"] if type_ == "verify" else DATA["slots"]
    if not source:
        await m.reply(f"📭 No {type_} slots.")
        return
    kb = []
    for i, s in enumerate(source):
        cb_prefix = "rm_v_slot_" if type_ == "verify" else "rm_slot_"
        kb.append([
            InlineKeyboardButton(f"{i+1} | {s['name']}", url=s['url']),
            InlineKeyboardButton("🗑 Remove", callback_data=f"{cb_prefix}{i}")
        ])
    await m.reply(f"📦 **{type_.title()} Slots** (click to visit, remove if needed):", reply_markup=InlineKeyboardMarkup(kb))

async def handle_user_commands(c, m, uid, cmd):
    try:
        user_data = DATA["users"].get(uid, {"refs": 0})
        if cmd == "💰 My Balance":
            refs = user_data.get("refs", 0)
            await m.reply(f"💰 Your balance: {refs} / {DATA['refer_limit']}")
        elif cmd == "👥 Referral":
            await send_refer_interface(c, m)
        elif cmd == "🔐 Get Key":
            if user_data.get("refs", 0) >= DATA["refer_limit"]:
                await send_final_key(c, m)
            else:
                need = DATA["refer_limit"] - user_data.get("refs", 0)
                await m.reply(f"❌ You need {need} more referral(s) to unlock the key.")
        elif cmd == "💬 Support":
            support = DATA.get("support_username", "Owner")
            await m.reply(f"📞 Contact: @{support}")
    except Exception as e:
        logger.exception(f"Error in user command {cmd}: {e}")
        await m.reply("❌ An error occurred. Please try again later.")

# ====================================================================
# BACKGROUND TASKS (wrapped in try-except)
# ====================================================================
async def scheduled_saver():
    while True:
        try:
            await asyncio.sleep(30)
            save_data_to_disk()
        except Exception as e:
            logger.exception(f"Error in scheduled_saver: {e}")

async def backup_loop():
    ensure_backup_dir()
    while True:
        try:
            await asyncio.sleep(600)  # every 10 minutes
            if os.path.exists(DATABASE_FILE):
                ts = int(time.time())
                shutil.copy(DATABASE_FILE, f"{BACKUP_DIR}/db_{ts}.json")
                files = sorted(os.listdir(BACKUP_DIR))
                if len(files) > 20:
                    os.remove(os.path.join(BACKUP_DIR, files[0]))
        except Exception as e:
            logger.exception(f"Error in backup_loop: {e}")

# ====================================================================
# MAIN
# ====================================================================
async def run_bot():
    print("🚀 Bot starting...")
    try:
        await app.start()
        # Anti‑spam / boot notification
        if time.time() - DATA["last_boot"] > 30:
            try:
                await app.send_message(OWNER_ID, "✅ **Bot Online**\nAll systems secured.")
            except Exception as e:
                logger.error(f"Could not send startup message: {e}")
        DATA["last_boot"] = time.time()
        save_data_to_disk()

        # Start background tasks
        asyncio.create_task(scheduled_saver())
        asyncio.create_task(backup_loop())

        await idle()
    except Exception as e:
        logger.exception(f"🔥 CRITICAL ERROR in main loop: {e}")
        error_msg = str(e).lower()
        if "locked" in error_msg or "busy" in error_msg:
            logger.warning("Database locked. Waiting 5s...")
            time.sleep(5)
        else:
            DATA["sys_stats"]["errors"] += 1
            if ALERTER.check():
                try:
                    async with Client("Alert", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) as tmp:
                        await tmp.send_message(OWNER_ID, f"⚠️ **Bot crashed:**\n`{e}`")
                except:
                    pass
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        print("👋 Bot stopped by user.")
    except Exception as e:
        logger.exception(f"Unhandled exception at top level: {e}")
        time.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)