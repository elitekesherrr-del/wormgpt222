# =============================================
#   WORMGPT 2.0 MADE BY SIR KANHA
#   Separate Think Mode Buttons: ON / OFF
#   Render Deployment Optimized (With Flask Ping Webserver)
#   pip install pyTelegramBotAPI requests flask
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
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# =============================================
#  ⚙️  CONFIGURATION (UPDATED FOR RENDER)
# =============================================
# Render ke environment variables se token uthayega, backup me purana token rakha hai
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8839096412:AAFF_QRxRJOp2WxzCr-XSNKxDVI8SavMRko")
ADMIN_USER_ID = int(os.environ.get("ADMIN_USER_ID", 6885858256))  # SIR KANHA
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

# Data files (Render par ephemeral disk hoti hai, par json files temporary kaam karengi)
DATA_FILE = "user_data.json"
ADMIN_LOG_FILE = "admin_logs.json"
KEYS_FILE = "generated_keys.json"

# Watermark - SIR KANHA
WATERMARK = "✨ Worm Gpt 😈 2.0 Made By Sir Kanha ✨"

# =============================================
#  🤖  BOT INIT
# =============================================
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
_lock = threading.Lock()
_users = {}
_admin_session = {}

# FLASK APP FOR RENDER PORT BINDING
app = Flask(__name__)

@app.route('/')
def home():
    return "😈 WormGPT 2.0 Bot Is Alive on Render!"

@app.route('/health')
def health():
    return {"status": "healthy"}, 200


# =============================================
#  KEY GENERATOR SYSTEM - SIMPLIFIED
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
    data = load_data(KEYS_FILE)
    return data.get("batches", {})


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
    remaining = total - claimed
    
    return {
        "total": total,
        "claimed": claimed,
        "remaining": remaining,
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
        if d["version"] == "1":
            markup = build_chat_menu_v1(uid)
        else:
            markup = build_chat_menu_v2(uid)
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
        if d["version"] == "1":
            markup = build_chat_menu_v1(uid)
        else:
            markup = build_chat_menu_v2(uid)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    except:
        pass


# =============================================
#  CALLBACK HANDLERS - USER
# =============================================
@bot.callback_query_handler(func=lambda c: c.data == "buy_credits")
def cb_buy_credits(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📞 CONTACT ADMIN", url=YOUR_CHANNEL_LINK))
    markup.row(InlineKeyboardButton("🔙 BACK", callback_data="user_menu"))
    bot.edit_message_text(
        f"💎 *BUY CREDITS*\n\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"Need more credits?\n\n"
        f"Message us on the channel.\n"
        f"We'll add them fast.\n\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{WATERMARK}",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda c: c.data == "my_credits")
def cb_my_credits(call):
    bot.answer_callback_query(call.id)
    d = get_user(call.from_user.id)
    refresh_credits(d)
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔙 BACK", callback_data="user_menu"))
    
    credit_bar = "🟩" * d['credits'] + "⬜" * (FREE_CREDITS - d['credits'])
    
    bot.edit_message_text(
        f"💰 *YOUR CREDITS*\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{credit_bar}\n\n"
        f"Balance: *{d['credits']}/{FREE_CREDITS}*\n\n"
        f"Messages Today: {d['total_messages']}\n"
        f"Reset In: {fmt_time(max(0, d['reset_time'] - time.time()))}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"Got a code? Use:\n"
        f"/claim CODE\n\n"
        f"Each code = {CREDIT_CLAIM_AMOUNT} credits\n\n"
        f"{WATERMARK}",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda c: c.data == "help_menu")
def cb_help(call):
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔙 BACK", callback_data="user_menu"))
    bot.edit_message_text(
        f"ℹ️ *HOW TO USE*\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"*TALK TO AI:*\n"
        f"/v1 - Version 1\n"
        f"/v2 - Version 2\n\n"
        f"*IN CHAT:*\n"
        f"Use Think ON / Think OFF buttons\n"
        f"See your stats\n"
        f"Go back anytime\n\n"
        f"*CREDITS:*\n"
        f"Each message = 1 credit\n"
        f"Daily: {FREE_CREDITS} free credits\n"
        f"Got code? /claim CODE\n\n"
        f"*COMMANDS:*\n"
        f"/stats - See balance\n"
        f"/clear - New chat\n"
        f"/menu - Main menu\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"{WATERMARK}",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda c: c.data == "user_menu")
def cb_user_menu(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        welcome_text(),
        call.message.chat.id, call.message.message_id,
        reply_markup=build_user_menu(call.from_user.id),
        parse_mode="Markdown"
    )


# =============================================
#  CALLBACK HANDLERS - ADMIN
# =============================================
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
        bot.edit_message_text(
            f"📊 *STATISTICS*\n\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"Users: {len(all_users)}\n\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
            f"{WATERMARK}",
            call.message.chat.id, call.message.message_id,
            reply_markup=build_admin_menu(), parse_mode="Markdown"
        )
    
    elif action == "admin_user_list":
        all_users = get_all_users()
        user_list = "👤 *USERS*\n\n━━━━━━━━━━━━━━\n\n"
        for uid_str, data in list(all_users.items())[:15]:
            username = data.get("username", f"ID:{uid_str}")
            credits = data.get("credits", 0)
            user_list += f"{username} → {credits} 💎\n"
        
        if len(all_users) > 15:
            user_list += f"\n+{len(all_users) - 15} more users\n"
        
        bot.edit_message_text(
            user_list + f"\n━━━━━━━━━━━━━━\n\n{WATERMARK}",
            call.message.chat.id, call.message.message_id,
            reply_markup=build_admin_menu(), parse_mode="Markdown"
        )
    
    elif action == "admin_broadcast":
        msg = bot.send_message(call.message.chat.id, 
            f"📢 Type message to send everyone:\n\n"
            f"(or /cancel)\n\n"
            f"{WATERMARK}")
        bot.register_next_step_handler(msg, process_broadcast, uid)
    
    elif action == "admin_gen_codes":
        batch_id = f"BATCH_{int(time.time())}"
        codes = generate_batch_codes(10)
        save_generated_codes(batch_id, codes)
        
        codes_display = "\n".join(codes)
        log_admin_action(uid, "GEN_CODES", f"Generated batch {batch_id}")
        
        bot.edit_message_text(
            f"🔑 *10 CODES CREATED*\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"`{codes_display}`\n\n"
            f"━━━━━━━━━━━━━━━━━━\n\n"
            f"💎 Each code = {CREDIT_CLAIM_AMOUNT} credits\n"
            f"👥 One per user\n\n"
            f"Send codes to users\n"
            f"They use: /claim CODE\n\n"
            f"{WATERMARK}",
            call.message.chat.id, call.message.message_id,
            reply_markup=build_admin_menu(), parse_mode="Markdown"
        )
    
    elif action == "admin_code_stats":
        batches = get_all_code_batches()
        if not batches:
            stats_text = "🔑 *NO CODES YET*\n"
        else:
            stats_text = "🔑 *CODE STATISTICS*\n\n━━━━━━━━━━━━━━━\n\n"
            total_generated = 0
            total_claimed = 0
            
            for batch_id, batch_data in list(batches.items())[-5:]:
                stats = get_batch_stats(batch_id)
                if stats:
                    total_generated += stats["total"]
                    total_claimed += stats["claimed"]
                    stats_text += f"📦 {batch_id}\n"
                    stats_text += f"  ✅ Used: {stats['claimed']}/{stats['total']}\n"
                    stats_text += f"  📅 {stats['created_at'][:10]}\n\n"
            
            stats_text += f"━━━━━━━━━━━━━━━\n\n"
            stats_text += f"Total Created: {total_generated}\n"
            stats_text += f"Total Used: {total_claimed}\n"
            stats_text += f"Available: {total_generated - total_claimed}\n"
        
        bot.edit_message_text(
            stats_text + f"\n━━━━━━━━━━━━━━━\n\n{WATERMARK}",
            call.message.chat.id, call.message.message_id,
            reply_markup=build_admin_menu(), parse_mode="Markdown"
        )
    
    elif action == "admin_close":
        bot.edit_message_text(
            f"✅ *CLOSED*\n\n"
            f"{WATERMARK}",
            call.message.chat.id, call.message.message_id
        )


def process_broadcast(message, admin_uid):
    if message.text == "/cancel":
        bot.reply_to(message, f"❌ Cancelled\n\n{WATERMARK}")
        return
    
    broadcast_msg = message.text
    all_users = get_all_users()
    sent = 0
    failed = 0
    
    progress = bot.send_message(message.chat.id, f"📢 Sending...\n\n{WATERMARK}")
    
    for uid_str in all_users.keys():
        try:
            bot.send_message(
                int(uid_str),
                f"📢 *MESSAGE*\n\n"
                f"━━━━━━━━━━━━\n\n"
                f"{broadcast_msg}\n\n"
                f"━━━━━━━━━━━━\n\n"
                f"{WATERMARK}",
                parse_mode="Markdown"
            )
            sent += 1
        except:
            failed += 1
        time.sleep(0.05)
    
    log_admin_action(admin_uid, "BROADCAST", f"Sent: {sent}, Failed: {failed}")
    
    bot.edit_message_text(
        f"✅ *DONE*\n\n"
        f"Sent: {sent} ✓\n"
        f"Failed: {failed} ✗\n\n"
        f"{WATERMARK}",
        message.chat.id, progress.message_id,
        reply_markup=build_admin_menu(), parse_mode="Markdown"
    )


# =============================================
#  CORE ENGINE - VERSION BASED
# =============================================
def create_guest_and_stream(user_message, version="1",
                             think_mode=False, char_id=DEFAULT_CHAR_ID):
    s = requests.Session()
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    })

    try:
        r0 = s.get(BASE_URL, timeout=30)
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', r0.text)
        if not csrf:
            raise Exception("ERROR")
        csrf = csrf.group(1)

        h1 = {
            "Content-Type": "application/json",
            "Accept": "application/json, */*",
            "X-CSRF-TOKEN": csrf,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": BASE_URL,
            "Origin": BASE_URL,
        }
        r1 = s.post(
            f"{BASE_URL}/chats/start", headers=h1,
            json={"message": user_message, "character_id": char_id},
            timeout=30
        )
        uuid_m = re.search(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            r1.text
        )
        if not uuid_m:
            raise Exception("ERROR")
        chat_uuid = uuid_m.group(0)

        r2 = s.get(f"{BASE_URL}/chat/{chat_uuid}", timeout=30)
        csrf2m = re.search(r'name="csrf-token" content="([^"]+)"', r2.text)
        csrf2 = csrf2m.group(1) if csrf2m else csrf

        body = {
            "messages": [{
                "role": "user", "content": user_message,
                "type": "text", "action": None, "image_prompt": None
            }],
            "version": version
        }
        if think_mode:
            body["think_mode"] = True

        h2 = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "X-CSRF-TOKEN": csrf2,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{BASE_URL}/chat/{chat_uuid}",
            "Origin": BASE_URL,
        }

        thinking = ""
        answer = ""

        with s.post(
            f"{BASE_URL}/chats/{chat_uuid}/stream",
            json=body, headers=h2, stream=True, timeout=90
        ) as r3:
            buf = b""
            for chunk in r3.iter_content(chunk_size=None):
                if not chunk:
                    continue
                buf += chunk
                lines = buf.split(b"\n")
                buf = lines[-1]
                for raw in lines[:-1]:
                    line = raw.decode("utf-8", errors="replace").strip()
                    if not line.startswith("data:"):
                        continue
                    d = line[5:].strip()
                    if not d or d == "[DONE]":
                        continue
                    try:
                        obj = json.loads(d)
                        if "error" in obj:
                            raise Exception("ERROR")
                        if "content" in obj:
                            if obj.get("type") == "thinking":
                                thinking += obj["content"]
                            else:
                                answer += obj["content"]
                        for choice in obj.get("choices", []):
                            answer += choice.get("delta", {}).get("content", "")
                    except json.JSONDecodeError:
                        pass

        answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL)
        answer = re.sub(r"^think>.*", "", answer, flags=re.MULTILINE)
        answer = answer.strip()

        return thinking.strip(), answer.strip()
    
    except Exception as e:
        raise e


def get_response_retry(user_message, version, think_mode, retries=2):
    for attempt in range(retries + 1):
        try:
            return create_guest_and_stream(user_message, version, think_mode)
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            raise


def send_long(cid, text, **kw):
    for i in range(0, len(text), 4096):
        bot.send_message(cid, text[i:i + 4096], **kw)


# =============================================
#  COMMANDS
# =============================================
@bot.message_handler(commands=["start"])
def cmd_start(m):
    uid = m.from_user.id
    
    d = get_user(uid)
    if m.from_user.username:
        d["username"] = f"@{m.from_user.username}"
    else:
        d["username"] = f"ID:{uid}"
    update_user(uid, d)
    
    if not is_joined(uid):
        send_force_join(m.chat.id, uid)
        return
    
    bot.reply_to(m, welcome_text(), reply_markup=build_user_menu(uid), parse_mode="Markdown")


@bot.message_handler(commands=["menu"])
def cmd_menu(m):
    uid = m.from_user.id
    if not is_joined(uid):
        send_force_join(m.chat.id, uid)
        return
    bot.reply_to(m, welcome_text(), reply_markup=build_user_menu(uid), parse_mode="Markdown")


@bot.message_handler(commands=["admin"])
def cmd_admin(m):
    uid = m.from_user.id
    
    if not is_admin(uid):
        bot.reply_to(m, f"❌ Not Allowed\n\n{WATERMARK}")
        return
    
    args = m.text.split()
    if len(args) < 2:
        bot.reply_to(m, f"🔒 Need Key\n\n/admin [KEY]\n\n{WATERMARK}")
        return
    
    key = args[1]
    if verify_admin_key(uid, key):
        bot.reply_to(
            m,
            f"✅ *ADMIN UNLOCKED*\n\n"
            f"━━━━━━━━━━━━━━━━\n\n"
            f"Welcome Sir Kanha\n\n"
            f"All Options Ready\n\n"
            f"{WATERMARK}",
            reply_markup=build_admin_menu(),
            parse_mode="Markdown"
        )
        log_admin_action(uid, "LOGIN", "Admin accessed")
    else:
        bot.reply_to(m, f"❌ Wrong Key\n\n{WATERMARK}")


@bot.message_handler(commands=["claim"])
def cmd_claim(m):
    uid = m.from_user.id
    args = m.text.split()
    
    if len(args) < 2:
        bot.reply_to(m, 
            f"🔑 *GOT A CODE?*\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"Use: /claim CODE\n\n"
            f"Example:\n"
            f"/claim ABC12345\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"Get {CREDIT_CLAIM_AMOUNT} credits!\n\n"
            f"{WATERMARK}",
            parse_mode="Markdown")
        return
    
    code = args[1].upper()
    
    if not is_code_valid(code):
        bot.reply_to(m, 
            f"❌ *CODE INVALID*\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"Already used or wrong.\n\n"
            f"Ask admin for new one.\n\n"
            f"{WATERMARK}",
            parse_mode="Markdown")
        return
    
    d = get_user(uid)
    if d.get("claimed_code"):
        bot.reply_to(m, 
            f"❌ *ALREADY CLAIMED*\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"One code per person only.\n\n"
            f"{WATERMARK}",
            parse_mode="Markdown")
        return
    
    if claim_code_from_batch(code, uid):
        d["credits"] += CREDIT_CLAIM_AMOUNT
        d["claimed_code"] = code
        update_user(uid, d)
        
        bot.reply_to(
            m,
            f"✅ *CODE WORKED!*\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"+{CREDIT_CLAIM_AMOUNT} Credits Added\n\n"
            f"New Balance: {d['credits']}\n\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"Ready to chat!\n\n"
            f"{WATERMARK}", 
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(m, 
            f"❌ *FAILED*\n\n"
            f"Try again or ask admin\n\n"
            f"{WATERMARK}",
            parse_mode="Markdown")


@bot.message_handler(commands=["clear"])
def cmd_clear(m):
    reset_user(m.from_user.id)
    bot.reply_to(m, 
        f"🗑 *CLEARED*\n\n"
        f"Fresh start ready!\n\n"
        f"{WATERMARK}",
        parse_mode="Markdown")


@bot.message_handler(commands=["v1"])
def cmd_v1(m):
    uid = m.from_user.id
    if not is_joined(uid):
        send_force_join(m.chat.id, uid)
        return
    
    d = get_user(uid)
    d["version"] = "1"
    update_user(uid, d)
    
    think_status = "ON ✅" if d["think_mode"] else "OFF ⚡"
    
    bot.reply_to(m, 
        f"📡 *VERSION 1 READY*\n\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"Think Mode: {think_status}\n\n"
        f"Start chatting!\n\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{WATERMARK}",
        reply_markup=build_chat_menu_v1(uid),
        parse_mode="Markdown")


@bot.message_handler(commands=["v2"])
def cmd_v2(m):
    uid = m.from_user.id
    if not is_joined(uid):
        send_force_join(m.chat.id, uid)
        return
    
    d = get_user(uid)
    d["version"] = "2"
    update_user(uid, d)
    
    think_status = "ON ✅" if d["think_mode"] else "OFF ⚡"
    
    bot.reply_to(m, 
        f"📡 *VERSION 2 READY*\n\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"Think Mode: {think_status}\n\n"
        f"Start chatting!\n\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"{WATERMARK}",
        reply_markup=build_chat_menu_v2(uid),
        parse_mode="Markdown")


@bot.message_handler(commands=["stats"])
def cmd_stats(m):
    d = get_user(m.from_user.id)
    refresh_credits(d)
    left = max(0, int(d["reset_time"] - time.time()))
    
    credit_bar = "🟩" * d['credits'] + "⬜" * (FREE_CREDITS - d['credits'])
    
    bot.reply_to(
        m,
        f"📊 *YOUR STATS*\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{credit_bar}\n\n"
        f"Balance: {d['credits']}/{FREE_CREDITS}\n"
        f"Messages: {d['total_messages']}\n"
        f"Version: {d['version']}\n"
        f"Reset: {fmt_time(left)}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"{WATERMARK}",
        parse_mode="Markdown"
    )


# =============================================
#  MAIN MESSAGE HANDLER
# =============================================
@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    uid = m.from_user.id
    cid = m.chat.id

    if not m.text:
        return

    if not is_joined(uid):
        send_force_join(cid, uid)
        return

    d = get_user(uid)
    refresh_credits(d)
    now = time.time()

    if now < d["cooldown"]:
        left = int(d["cooldown"] - now)
        bot.reply_to(
            m,
            f"⏳ *WAIT {left}s*\n\n"
            f"━━━━━━━━━━━━\n\n"
            f"Still thinking...\n\n"
            f"{WATERMARK}",
            parse_mode="Markdown"
        )
        return

    if d["credits"] <= 0:
        left = max(0, int(d["reset_time"] - now))
        bot.reply_to(
            m,
            f"🚫 *NO CREDITS*\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"Reset: {fmt_time(left)}\n\n"
            f"Got code? /claim\n"
            f"Need code? Contact us\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"{WATERMARK}",
            reply_markup=build_user_menu(uid),
            parse_mode="Markdown"
        )
        return

    version = d["version"]
    think_mode = d["think_mode"]
    d["credits"] -= 1
    d["cooldown"] = now + COOLDOWN_SECONDS
    d["total_messages"] += 1
    update_user(uid, d)

    think_label = "🧠 THINKING" if think_mode else "⚡ QUICK"
    wait_msg = bot.reply_to(
        m,
        f"🔥 *LOADING...*\n\n"
        f"━━━━━━━━━━━━\n\n"
        f"Version {version}\n"
        f"{think_label}\n\n"
        f"⏳ Processing...\n\n"
        f"{WATERMARK}",
        parse_mode="Markdown"
    )
    bot.send_chat_action(cid, "typing")

    try:
        thinking, answer = get_response_retry(m.text, version, think_mode)

        if not answer and not thinking:
            d["credits"] += 1
            update_user(uid, d)
            bot.edit_message_text(
                f"❌ *NO REPLY*\n\n"
                f"Try again\n\n"
                f"{WATERMARK}",
                cid, wait_msg.message_id
            )
            return

        try:
            bot.delete_message(cid, wait_msg.message_id)
        except:
            pass

        if think_mode and thinking:
            preview = thinking[:500] + ("..." if len(thinking) > 500 else "")
            bot.send_message(
                cid,
                f"💭 *THINKING*\n\n{preview}\n\n{WATERMARK}",
                parse_mode="Markdown"
            )

        final = (
            f"😈 *WORMGPT ANSWER*\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"{answer or thinking}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"Version {version} | {think_label}\n"
            f"Credits: {d['credits']}/{FREE_CREDITS}\n\n"
            f"{WATERMARK}"
        )
        send_long(cid, final, parse_mode="Markdown")

    except Exception as e:
        d["credits"] += 1
        update_user(uid, d)
        try:
            bot.delete_message(cid, wait_msg.message_id)
        except:
            pass
        print(f"ERROR: {e}")
        bot.reply_to(
            m,
            f"❌ *ERROR*\n\n"
            f"Try again later\n\n"
            f"{WATERMARK}",
            parse_mode="Markdown"
        )


# =============================================
#  TELEGRAM POLLING THREAD
# =============================================
def run_bot():
    print("😈 WORMGPT 2.0 - TELEGRAM POLLING STARTED")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=20)
        except Exception as e:
            print(f"Polling error: {e}. Re-starting in 5 seconds...")
            time.sleep(5)


# =============================================
#  RUN SERVER (MAIN ENTRY POINT FOR RENDER)
# =============================================
if __name__ == "__main__":
    init_data_files()
    print("😈 WORMGPT 2.0 - MADE BY SIR KANHA")
    print(f"👤 ADMIN ID: {ADMIN_USER_ID}")
    
    # 1. Bot ko background thread me start karein
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # 2. Flask webserver ko main thread me run karein jo Render ke PORT ko bind karega
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

