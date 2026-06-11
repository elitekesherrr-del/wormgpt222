# =============================================
#   WORMGPT 2.0 MADE BY SIR KANHA
#   Separate Think Mode Buttons: ON / OFF
#   Render Webhook Deployment Optimized
#   pip install pyTelegramBotAPI requests flask gunicorn
# =============================================

import json
import re
import threading
import time
import requests
import telebot
import os
import random
import string
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Update
from flask import Flask, request

# =============================================
#  ⚙️  CONFIGURATION
# =============================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8839096412:AAFF_QRxRJOp2WxzCr-XSNKxDVI8SavMRko")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 6885858256))
ADMIN_ACCESS_KEY = os.environ.get("ADMIN_ACCESS_KEY", "LHSGFLHADA")
YOUR_CHANNEL_LINK = "https://t.me/K4NHA_EMPIRE"

BASE_URL = "https://uncensored.chat"
DEFAULT_CHAR_ID = 87
FREE_CREDITS = 2
RESET_HOURS = 24
COOLDOWN_SECONDS = 40
CREDIT_CLAIM_AMOUNT = 50

CHANNELS = {
    "@K4NHA_EMPIRE": "https://t.me/K4NHA_EMPIRE",
    "@K3NHA_EMPIRE": "https://t.me/K3NHA_EMPIRE"
}

DATA_FILE = "user_data.json"
ADMIN_LOG_FILE = "admin_logs.json"
KEYS_FILE = "generated_keys.json"

WATERMARK = "✨ Worm Gpt 😈 2.0 Made By Sir Kanha ✨"

# =============================================
#  🤖  BOT & FLASK INIT
# =============================================
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
_lock = threading.Lock()
_users = {}
_admin_session = {}

app = Flask(__name__)

# =============================================
#  WEBHOOK ROUTING FOR RENDER
# =============================================
@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def webhook_init():
    # Render app primary URL fetch karega automatically
    render_url = f"https://{request.host}"
    bot.remove_webhook()
    time.sleep(0.1)
    status = bot.set_webhook(url=f"{render_url}/{TELEGRAM_BOT_TOKEN}")
    if status:
        return f"😈 WormGPT 2.0 Webhook Successfully Set on {render_url}!", 200
    else:
        return "❌ Webhook Setup Failed.", 500

# =============================================
#  KEY GENERATOR SYSTEM
# =============================================
def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_batch_codes(batch_size=10):
    codes_set = set()
    while len(codes_set) < batch_size:
        codes_set.add(generate_random_code())
    return list(codes_set)

def save_generated_codes(batch_id, codes_list):
    data = load_data(KEYS_FILE)
    if "batches" not in data:
        data["batches"] = {}
    data["batches"][batch_id] = {
        "codes": codes_list,
        "created_at": datetime.now().isoformat(),
        "redeemed": {}
    }
    save_data(KEYS_FILE, data)
    return batch_id

def get_all_code_batches():
    return load_data(KEYS_FILE)

def claim_code_from_batch(code, user_id):
    data = load_data(KEYS_FILE)
    if "batches" not in data:
        return False
    for batch_id, batch in data["batches"].items():
        if code in batch["codes"]:
            if code in batch["redeemed"]:
                return False  
            batch["redeemed"][code] = {
                "user_id": user_id,
                "claimed_at": datetime.now().isoformat()
            }
            save_data(KEYS_FILE, data)
            return True
    return False

def is_code_valid(code):
    data = load_data(KEYS_FILE)
    if "batches" not in data:
        return False
    for batch_id, batch in data["batches"].items():
        if code in batch["codes"]:
            if code not in batch["redeemed"]:
                return True
    return False

def get_batch_stats(batch_id):
    data = load_data(KEYS_FILE)
    if "batches" not in data or batch_id not in data["batches"]:
        return None
    batch = data["batches"][batch_id]
    total = len(batch["codes"])
    claimed = len(batch["redeemed"])
    return {
        "total": total,
        "claimed": claimed,
        "remaining": total - claimed,
        "created_at": batch["created_at"]
    }

# =============================================
#  DATA MANAGEMENT
# =============================================
def init_data_files():
    files = [DATA_FILE, ADMIN_LOG_FILE, KEYS_FILE]
    for f in files:
        if not os.path.exists(f):
            with open(f, 'w') as fp:
                json.dump({}, fp)

def load_data(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_data(filename, data):
    try:
        with _lock:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def log_admin_action(uid, action, details=""):
    logs = load_data(ADMIN_LOG_FILE)
    if "logs" not in logs:
        logs["logs"] = []
    logs["logs"].append({
        "timestamp": datetime.now().isoformat(),
        "admin_id": uid,
        "action": action,
        "details": details
    })
    save_data(ADMIN_LOG_FILE, logs)

# =============================================
#  USER DATA
# =============================================
def get_user(uid):
    with _lock:
        if uid not in _users:
            all_data = load_data(DATA_FILE)
            if str(uid) in all_data:
                _users[uid] = all_data[str(uid)]
            else:
                _users[uid] = {
                    "user_id": uid,
                    "username": None,
                    "credits": FREE_CREDITS,
                    "total_messages": 0,
                    "version": "1",
                    "think_mode": False,
                    "reset_time": time.time() + RESET_HOURS * 3600,
                    "cooldown": 0,
                    "claimed_code": None,
                    "joined_date": datetime.now().isoformat()
                }
        return _users[uid]

def update_user(uid, data):
    with _lock:
        _users[uid] = data
    all_data = load_data(DATA_FILE)
    all_data[str(uid)] = data
    save_data(DATA_FILE, all_data)

def get_all_users():
    return load_data(DATA_FILE)

def reset_user(uid):
    d = get_user(uid)
    d["credits"] = FREE_CREDITS
    d["total_messages"] = 0
    d["reset_time"] = time.time() + RESET_HOURS * 3600
    d["cooldown"] = 0
    update_user(uid, d)

# =============================================
#  ADMIN AUTH
# =============================================
def is_admin(uid):
    return uid == ADMIN_USER_ID

def verify_admin_key(uid, key):
    if key == ADMIN_ACCESS_KEY:
        _admin_session[uid] = {"authenticated": True, "timestamp": time.time()}
        return True
    return False

def is_admin_authenticated(uid):
    if uid not in _admin_session:
        return False
    session = _admin_session[uid]
    if time.time() - session["timestamp"] > 3600:
        del _admin_session[uid]
        return False
    return session.get("authenticated", False)

# =============================================
#  CHANNEL HELPERS
# =============================================
def not_joined_channels(user_id):
    result = []
    for username, link in CHANNELS.items():
        try:
            m = bot.get_chat_member(username, user_id)
            if m.status not in ("member", "administrator", "creator"):
                result.append((username, link))
        except:
            result.append((username, link))
    return result

def is_joined(user_id):
    return len(not_joined_channels(user_id)) == 0

def send_force_join(chat_id, user_id):
    nj = not_joined_channels(user_id)
    markup = InlineKeyboardMarkup()
    for username, link in nj:
        markup.row(InlineKeyboardButton(f"📢 Join {username}", url=link))
    markup.row(InlineKeyboardButton("✅ I Joined", callback_data="check_join"))
    names = "\n".join(f"• {x[0]}" for x in nj)
    bot.send_message(
        chat_id,
        f"😈 *WORMGPT - JOIN TO START*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥 JOIN THESE CHANNELS:\n\n"
        f"{names}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Then tap ✅\n\n"
        f"{WATERMARK}",
        reply_markup=markup, parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def cb_check_join(call):
    uid = call.from_user.id
    if is_joined(uid):
        bot.answer_callback_query(call.id, "✅ Let's Go!", show_alert=True)
        bot.edit_message_text(
            welcome_text(), call.message.chat.id,
            call.message.message_id, parse_mode="Markdown"
        )
    else:
        nj = not_joined_channels(uid)
        names = "\n".join(x[0] for x in nj)
        bot.answer_callback_query(call.id, f"❌ Join All:\n{names}", show_alert=True)

# =============================================
#  TIME & CREDIT HELPERS
# =============================================
def refresh_credits(d):
    now = time.time()
    if now >= d["reset_time"]:
        d["credits"] = FREE_CREDITS
        d["reset_time"] = now + RESET_HOURS * 3600

def fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m}m"

def welcome_text():
    return (
        "😈 *WELCOME TO WORMGPT 2.0*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔥 CHAT WITH AI NOW\n\n"
        "🎁 Credits Today: *2*\n"
        "⏳ Wait: *40 seconds*\n"
        "💪 2 Versions Available\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📖 *COMMANDS:*\n\n"
        "/menu - Open Menu\n"
        "/v1 - Use Version 1\n"
        "/v2 - Use Version 2\n"
        "/stats - Check Credits\n"
        "/clear - New Chat\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{WATERMARK}"
    )

# =============================================
#  MENU BUILDERS
# =============================================
def build_user_menu(uid):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("💎 BUY CREDITS", callback_data="buy_credits"))
    markup.row(InlineKeyboardButton("💰 MY CREDITS", callback_data="my_credits"))
    markup.row(InlineKeyboardButton("ℹ️ HELP", callback_data="help_menu"))
    markup.row(InlineKeyboardButton("📞 CONTACT US", url=YOUR_CHANNEL_LINK))
    return markup

def build_admin_menu():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📊 USERS", callback_data="admin_stats"))
    markup.row(InlineKeyboardButton("👤 USER LIST", callback_data="admin_user_list"))
    markup.row(InlineKeyboardButton("📢 SEND MESSAGE", callback_data="admin_broadcast"))
    markup.row(InlineKeyboardButton("🔑 CREATE CODES", callback_data="admin_gen_codes"))
    markup.row(InlineKeyboardButton("📈 CODE STATS", callback_data="admin_code_stats"))
    markup.row(InlineKeyboardButton("❌ CLOSE", callback_data="admin_close"))
    return markup

def build_chat_menu_v1(uid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🧠 Think ON", callback_data="think_on"),
        InlineKeyboardButton("⚡ Think OFF", callback_data="think_off")
    )
    markup.row(InlineKeyboardButton("📊 Stats", callback_data="my_credits"))
    markup.row(InlineKeyboardButton("🔙 Back", callback_data="user_menu"))
    return markup

def build_chat_menu_v2(uid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🧠 Think ON", callback_data="think_on"),
        InlineKeyboardButton("⚡ Think OFF", callback_data="think_off")
    )
    markup.row(InlineKeyboardButton("📊 Stats", callback_data="my_credits"))
    markup.row(InlineKeyboardButton("🔙 Back", callback_data="user_menu"))
    return markup

# =============================================
#  THINK MODE HANDLERS
# =============================================
@bot.callback_query_handler(func=lambda c: c.data == "think_on")
def cb_think_on(call):
    uid = call.from_user.id
    d = get_user(uid)
    if not d["think_mode"]:
        d["think_mode"] = True
        update_user(uid, d)
        bot.answer_callback_query(call.id, "✅ Think Mode ENABLED", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "ℹ️ Already ON", show_alert=True)
    try:
        markup = build_chat_menu_v1(uid) if d["version"] == "1" else build_chat_menu_v2(uid)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    except:
        pass

@bot.callback_query_handler(func=lambda c: c.data == "think_off")
def cb_think_off(call):
    uid = call.from_user.id
    d = get_user(uid)
    if d["think_mode"]:
        d["think_mode"] = False
        update_user(uid, d)
        bot.answer_callback_query(call.id, "⚡ Think Mode DISABLED", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "ℹ️ Already OFF", show_alert=True)
    try:
        markup = build_chat_menu_v1(uid) if d["version"] == "1" else build_chat_menu_v2(uid)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    except:
        pass

# =============================================
#  CALLBACK HANDLERS - USER & ADMIN
# =============================================
@bot.callback_query_handler(func=lambda c: c.data == "buy_credits")
def cb_buy_credits(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📞 CONTACT ADMIN", url=YOUR_CHANNEL_LINK))
    markup.row(InlineKeyboardButton("🔙 BACK", callback_data="user_menu"))
    bot.edit_message_text(f"💎 *BUY CREDITS*\n\n━━━━━━━━━━━━━━━━\n\nNeed more credits?\n\nMessage us on the channel.\nWe'll add them fast.\n\n━━━━━━━━━━━━━━━━\n\n{WATERMARK}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "my_credits")
def cb_my_credits(call):
    bot.answer_callback_query(call.id)
    d = get_user(call.from_user.id)
    refresh_credits(d)
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔙 BACK", callback_data="user_menu"))
    credit_bar = "🟩" * d['credits'] + "⬜" * (FREE_CREDITS - d['credits'])
    bot.edit_message_text(f"💰 *YOUR CREDITS*\n\n━━━━━━━━━━━━━━━\n\n{credit_bar}\n\nBalance: *{d['credits']}/{FREE_CREDITS}*\n\nMessages Today: {d['total_messages']}\nReset In: {fmt_time(max(0, d['reset_time'] - time.time()))}\n\n━━━━━━━━━━━━━━━\n\nGot a code? Use:\n/claim CODE\n\nEach code = {CREDIT_CLAIM_AMOUNT} credits\n\n{WATERMARK}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "help_menu")
def cb_help(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔙 BACK", callback_data="user_menu"))
    bot.edit_message_text(f"ℹ️ *HOW TO USE*\n\n━━━━━━━━━━━━━━━━━━\n\n*TALK TO AI:*\n/v1 - Version 1\n/v2 - Version 2\n\n*IN CHAT:*\nUse Think ON / Think OFF buttons\nSee your stats\nGo back anytime\n\n*CREDITS:*\nEach message = 1 credit\nDaily: {FREE_CREDITS} free credits\nGot code? /claim CODE\n\n*COMMANDS:*\n/stats - See balance\n/clear - New chat\n/menu - Main menu\n\n━━━━━━━━━━━━━━━━━━\n\n{WATERMARK}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data == "user_menu")
def cb_user_menu(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(welcome_text(), call.message.chat.id, call.message.message_id, reply_markup=build_user_menu(call.from_user.id), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_"))
def handle_admin_callbacks(call):
    uid = call.from_user.id
    if not (is_admin(uid) and is_admin_authenticated(uid)):
        bot.answer_callback_query(call.id, "❌ ADMIN ONLY", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    action = call.data
    
    if action == "admin_stats":
        all_users = get_all_users()
        bot.edit_message_text(f"📊 *STATISTICS*\n\n━━━━━━━━━━━━━━━━━\n\nUsers: {len(all_users)}\n\n━━━━━━━━━━━━━━━━━\n\n{WATERMARK}", call.message.chat.id, call.message.message_id, reply_markup=build_admin_menu(), parse_mode="Markdown")
    elif action == "admin_user_list":
        all_users = get_all_users()
        user_list = "👤 *USERS*\n\n━━━━━━━━━━━━━━\n\n"
        for uid_str, data in list(all_users.items())[:15]:
            username = data.get("username", f"ID:{uid_str}")
            user_list += f"{username} → {data.get('credits', 0)} 💎\n"
        bot.edit_message_text(user_list + f"\n━━━━━━━━━━━━━━\n\n{WATERMARK}", call.message.chat.id, call.message.message_id, reply_markup=build_admin_menu(), parse_mode="Markdown")
    elif action == "admin_broadcast":
        msg = bot.send_message(call.message.chat.id, f"📢 Type message to send everyone:\n\n(or /cancel)\n\n{WATERMARK}")
        bot.register_next_step_handler(msg, process_broadcast, uid)
    elif action == "admin_gen_codes":
        batch_id = f"BATCH_{int(time.time())}"
        codes = generate_batch_codes(10)
        save_generated_codes(batch_id, codes)
        bot.edit_message_text(f"🔑 *10 CODES CREATED*\n\n━━━━━━━━━━━━━━━━━━\n\n`{'\n'.join(codes)}`\n\n━━━━━━━━━━━━━━━━━━\n\n💎 Each code = {CREDIT_CLAIM_AMOUNT} credits\n\n{WATERMARK}", call.message.chat.id, call.message.message_id, reply_markup=build_admin_menu(), parse_mode="Markdown")
    elif action == "admin_close":
        bot.edit_message_text(f"✅ *CLOSED*\n\n{WATERMARK}", call.message.chat.id, call.message.message_id)

def process_broadcast(message, admin_uid):
    if message.text == "/cancel":
        bot.reply_to(message, f"❌ Cancelled\n\n{WATERMARK}")
        return
    all_users = get_all_users()
    sent, failed = 0, 0
    for uid_str in all_users.keys():
        try:
            bot.send_message(int(uid_str), f"📢 *MESSAGE*\n\n━━━━━━━━━━━━\n\n{message.text}\n\n━━━━━━━━━━━━\n\n{WATERMARK}", parse_mode="Markdown")
            sent += 1
        except:
            failed += 1
    bot.send_message(message.chat.id, f"✅ *DONE*\n\nSent: {sent} ✓\nFailed: {failed} ✗\n\n{WATERMARK}", reply_markup=build_admin_menu(), parse_mode="Markdown")

# =============================================
#  CORE ENGINE - WORMGPT
# =============================================
def create_guest_and_stream(user_message, version="1", think_mode=False, char_id=DEFAULT_CHAR_ID):
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept-Language": "en-US,en;q=0.9"})
    try:
        r0 = s.get(BASE_URL, timeout=30)
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', r0.text).group(1)
        r1 = s.post(f"{BASE_URL}/chats/start", headers={"X-CSRF-TOKEN": csrf, "X-Requested-With": "XMLHttpRequest"}, json={"message": user_message, "character_id": char_id}, timeout=30)
        chat_uuid = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", r1.text).group(0)
        r2 = s.get(f"{BASE_URL}/chat/{chat_uuid}", timeout=30)
        csrf2 = re.search(r'name="csrf-token" content="([^"]+)"', r2.text).group(1)
        
        body = {"messages": [{"role": "user", "content": user_message, "type": "text", "action": None, "image_prompt": None}], "version": version}
        if think_mode: body["think_mode"] = True

        thinking, answer = "", ""
        with s.post(f"{BASE_URL}/chats/{chat_uuid}/stream", json=body, headers={"X-CSRF-TOKEN": csrf2, "Accept": "text/event-stream", "X-Requested-With": "XMLHttpRequest"}, stream=True, timeout=90) as r3:
            for chunk in r3.iter_content(chunk_size=None):
                if not chunk: continue
                for line in chunk.decode("utf-8", errors="replace").split("\n"):
                    if line.startswith("data:"):
                        d = line[5:].strip()
                        if not d or d == "[DONE]": continue
                        try:
                            obj = json.loads(d)
                            if "content" in obj:
                                if obj.get("type") == "thinking": thinking += obj["content"]
                                else: answer += obj["content"]
                        except: pass
        return thinking.strip(), re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()
    except Exception as e: raise e

def get_response_retry(user_message, version, think_mode, retries=2):
    for attempt in range(retries + 1):
        try: return create_guest_and_stream(user_message, version, think_mode)
        except:
            if attempt < retries: time.sleep(2); continue
            raise

def send_long(cid, text, **kw):
    for i in range(0, len(text), 4096): bot.send_message(cid, text[i:i + 4096], **kw)

# =============================================
#  COMMANDS HANDLERS
# =============================================
@bot.message_handler(commands=["start", "menu"])
def cmd_start(m):
    uid = m.from_user.id
    d = get_user(uid)
    d["username"] = f"@{m.from_user.username}" if m.from_user.username else f"ID:{uid}"
    update_user(uid, d)
    if not is_joined(uid): send_force_join(m.chat.id, uid); return
    bot.reply_to(m, welcome_text(), reply_markup=build_user_menu(uid), parse_mode="Markdown")

@bot.message_handler(commands=["admin"])
def cmd_admin(m):
    uid = m.from_user.id
    if not is_admin(uid): bot.reply_to(m, f"❌ Not Allowed\n\n{WATERMARK}"); return
    args = m.text.split()
    if len(args) < 2: bot.reply_to(m, f"🔒 Need Key\n\n/admin [KEY]\n\n{WATERMARK}"); return
    if verify_admin_key(uid, args[1]):
        bot.reply_to(m, f"✅ *ADMIN UNLOCKED*\n\n━━━━━━━━━━━━━━━━\n\nWelcome Sir Kanha\n\n{WATERMARK}", reply_markup=build_admin_menu(), parse_mode="Markdown")
    else: bot.reply_to(m, f"❌ Wrong Key\n\n{WATERMARK}")

@bot.message_handler(commands=["claim"])
def cmd_claim(m):
    uid = m.from_user.id
    args = m.text.split()
    if len(args) < 2: bot.reply_to(m, f"🔑 *Use:* /claim CODE\n\n{WATERMARK}", parse_mode="Markdown"); return
    code = args[1].upper()
    if not is_code_valid(code): bot.reply_to(m, f"❌ *CODE INVALID*\n\n{WATERMARK}", parse_mode="Markdown"); return
    d = get_user(uid)
    if d.get("claimed_code"): bot.reply_to(m, f"❌ *ALREADY CLAIMED*\n\n{WATERMARK}", parse_mode="Markdown"); return
    if claim_code_from_batch(code, uid):
        d["credits"] += CREDIT_CLAIM_AMOUNT; d["claimed_code"] = code; update_user(uid, d)
        bot.reply_to(m, f"✅ *CODE WORKED!*\n\n+{CREDIT_CLAIM_AMOUNT} Credits Added\n\n{WATERMARK}", parse_mode="Markdown")

@bot.message_handler(commands=["clear"])
def cmd_clear(m):
    reset_user(m.from_user.id)
    bot.reply_to(m, f"🗑 *CLEARED*\n\nFresh start ready!\n\n{WATERMARK}", parse_mode="Markdown")

@bot.message_handler(commands=["v1", "v2"])
def cmd_version(m):
    uid = m.from_user.id
    if not is_joined(uid): send_force_join(m.chat.id, uid); return
    d = get_user(uid)
    d["version"] = "1" if m.text.startswith("/v1") else "2"
    update_user(uid, d)
    markup = build_chat_menu_v1(uid) if d["version"] == "1" else build_chat_menu_v2(uid)
    bot.reply_to(m, f"📡 *VERSION {d['version']} READY*\n\nThink Mode: {'ON ✅' if d['think_mode'] else 'OFF ⚡'}\n\n{WATERMARK}", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=["stats"])
def cmd_stats(m):
    d = get_user(m.from_user.id); refresh_credits(d)
    credit_bar = "🟩" * d['credits'] + "⬜" * (FREE_CREDITS - d['credits'])
    bot.reply_to(m, f"📊 *YOUR STATS*\n\n{credit_bar}\n\nBalance: {d['credits']}/{FREE_CREDITS}\nReset: {fmt_time(max(0, int(d['reset_time'] - time.time())))}\n\n{WATERMARK}", parse_mode="Markdown")

# =============================================
#  MAIN MESSAGE HANDLER
# =============================================
@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    uid = m.from_user.id
    if not m.text or not is_joined(uid): send_force_join(m.chat.id, uid); return
    d = get_user(uid); refresh_credits(d); now = time.time()
    if now < d["cooldown"]: bot.reply_to(m, f"⏳ *WAIT {int(d['cooldown'] - now)}s*\n\n{WATERMARK}", parse_mode="Markdown"); return
    if d["credits"] <= 0: bot.reply_to(m, f"🚫 *NO CREDITS*\n\n{WATERMARK}", reply_markup=build_user_menu(uid), parse_mode="Markdown"); return

    d["credits"] -= 1; d["cooldown"] = now + COOLDOWN_SECONDS; d["total_messages"] += 1; update_user(uid, d)
    wait_msg = bot.reply_to(m, f"🔥 *PROCESSING VERSION {d['version']}...*\n\n{WATERMARK}", parse_mode="Markdown")
    
    try:
        thinking, answer = get_response_retry(m.text, d["version"], d["think_mode"])
        try: bot.delete_message(m.chat.id, wait_msg.message_id)
        except: pass
        if d["think_mode"] and thinking:
            bot.send_message(m.chat.id, f"💭 *THINKING*\n\n{thinking[:500]}...\n\n{WATERMARK}", parse_mode="Markdown")
        send_long(m.chat.id, f"😈 *WORMGPT ANSWER*\n\n━━━━━━━━━━━━━━━━━━━\n\n{answer or thinking}\n\n━━━━━━━━━━━━━━━━━━━\n\nCredits: {d['credits']}/{FREE_CREDITS}\n\n{WATERMARK}", parse_mode="Markdown")
    except:
        d["credits"] += 1; update_user(uid, d)
        try: bot.delete_message(m.chat.id, wait_msg.message_id)
        except: pass
        bot.reply_to(m, f"❌ *ERROR* Try again later.\n\n{WATERMARK}", parse_mode="Markdown")

init_data_files()
