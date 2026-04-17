import json
import threading
import os
import shutil
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726
SUPPORT = "@Star_IDOO796256363"

lock = threading.Lock()

# ===== تحميل البيانات =====
def load_data():
    default = {"balances": {}, "orders": {}, "counter": 1, "spent": {}, "joined": {}}

    if not os.path.exists("data.json"):
        return default

    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        if os.path.exists("data_backup.json"):
            with open("data_backup.json", "r") as f:
                return json.load(f)
        return default

data = load_data()

balances = data.get("balances", {})
orders = data.get("orders", {})
order_id = data.get("counter", 1)
spent = data.get("spent", {})
joined = data.get("joined", {})

# ===== حفظ آمن =====
def save():
    global order_id
    with lock:
        with open("data.json", "w") as f:
            json.dump({
                "balances": balances,
                "orders": orders,
                "counter": order_id,
                "spent": spent,
                "joined": joined
            }, f, indent=2)

        shutil.copy("data.json", "data_backup.json")


# ===== تقسيم النظام بدون تعارض =====
SYSTEM_BUTTONS = {
    "🛍 المنتجات",
    "💰 إيداع رصيد",
    "📦 طلباتي",
    "👤 حسابي",
    "📞 الدعم الفني",
    "رجوع",
    "🎮 الألعاب",
    "📱 التطبيقات",
    "📡 سيرياتيل",
    "📶 MTN"
}

GAME_LIST = {
    "PUBG", "Free Fire", "Call of Duty Mobile", "eFootball",
    "Mobile Legends", "Clash of Clans", "Clash Royale", "Roblox"
}

APP_LIST = {
    "Bigo Live", "Party Star", "Exina Live", "Ahla Chat", "SoulChill",
    "Saba Chat", "IMO", "Q Chat", "Ho Chat", "Ya Ahla Chat",
    "Bella Chat", "Mego Live", "Yalla Live", "YoHo", "Yoyo Chat",
    "Haki Chat", "Up Live", "Solfa Chat", "Happy Chat", "Super Live",
    "Ayomi Chat", "Talk Talk", "Popo Live", "4Fun Chat", "Ohla Chat",
    "Koko Live", "Hiya Chat", "Taka Chat", "Likee", "Kwai",
    "Lego Live", "Lam Chat", "Hala"
}

# ===== المنتجات (باقات صحيحة 100%) =====
products = {
    "PUBG": {
        "60 UC": 0.95,
        "325 UC": 4.75,
        "660 UC": 9.5,
        "1800 UC": 23.62,
        "3850 UC": 47.5,
        "8100 UC": 95
    },

    "Free Fire": {"100 Diamonds": 1, "500 Diamonds": 5},
    "Call of Duty Mobile": {"80 CP": 1, "400 CP": 5},
    "eFootball": {"100 Coins": 1},
    "Mobile Legends": {"86 Diamonds": 2},
    "Clash of Clans": {"80 Gems": 1},
    "Clash Royale": {"80 Gems": 1},
    "Roblox": {"400 Robux": 5},

    "Bigo Live": {"1000 Coins": 5},
    "Party Star": {"1000 Coins": 5},
    "Exina Live": {"1000 Coins": 5},
    "Ahla Chat": {"1000 Coins": 5},
    "SoulChill": {"1000 Coins": 5},
    "Saba Chat": {"1000 Coins": 5},
    "IMO": {"1000 Coins": 5},
    "Q Chat": {"1000 Coins": 5},
    "Ho Chat": {"1000 Coins": 5},
    "Ya Ahla Chat": {"1000 Coins": 5},
    "Bella Chat": {"1000 Coins": 5},
    "Mego Live": {"1000 Coins": 5},
    "Yalla Live": {"1000 Coins": 5},
    "YoHo": {"1000 Coins": 5},
    "Yoyo Chat": {"1000 Coins": 5},
    "Haki Chat": {"1000 Coins": 5},
    "Up Live": {"1000 Coins": 5},
    "Solfa Chat": {"1000 Coins": 5},
    "Happy Chat": {"1000 Coins": 5},
    "Super Live": {"1000 Coins": 5},
    "Ayomi Chat": {"1000 Coins": 5},
    "Talk Talk": {"1000 Coins": 5},
    "Popo Live": {"1000 Coins": 5},
    "4Fun Chat": {"1000 Coins": 5},
    "Ohla Chat": {"1000 Coins": 5},
    "Koko Live": {"1000 Coins": 5},
    "Hiya Chat": {"1000 Coins": 5},
    "Taka Chat": {"1000 Coins": 5},
    "Likee": {"1000 Diamonds": 5},
    "Kwai": {"1000 Coins": 5},
    "Lego Live": {"1000 Coins": 5},
    "Lam Chat": {"1000 Coins": 5},
    "Hala": {"1000 Coins": 5},

    "Syriatel": {
        "40": 0.38,
        "50": 0.46,
        "80": 0.77,
        "100": 0.96,
        "200": 1.9
    },

    "MTN": {
        "40": 0.38,
        "50": 0.46,
        "85": 0.8,
        "100": 0.96,
        "200": 1.9
    }
}

# ===== القائمة =====
def main_menu():
    return ReplyKeyboardMarkup([
        ["🛍 المنتجات"],
        ["💰 إيداع رصيد", "📦 طلباتي"],
        ["👤 حسابي", "📞 الدعم الفني"]
    ], resize_keyboard=True)


# ===== START =====
async def start(update, context):
    uid = str(update.message.from_user.id)

    if uid not in joined:
        import datetime
        joined[uid] = str(datetime.datetime.now())
        save()

    await update.message.reply_text("⚡ مرحبا بك في متجر الشيخ", reply_markup=main_menu())


# ===== TEXT =====
async def text(update, context):
    global order_id
    msg = update.message.text
    uid = str(update.message.from_user.id)

    if msg == "رجوع":
        context.user_data.clear()
        await update.message.reply_text("🔙 رجعت", reply_markup=main_menu())
        return

    # ===== حماية الأزرار =====
    if msg in SYSTEM_BUTTONS:

        if msg == "🛍 المنتجات":
            keyboard = ReplyKeyboardMarkup([
                ["🎮 الألعاب", "📱 التطبيقات"],
                ["📡 سيرياتيل", "📶 MTN"],
                ["رجوع"]
            ], resize_keyboard=True)
            await update.message.reply_text("اختر القسم:", reply_markup=keyboard)

        elif msg == "🎮 الألعاب":
            keyboard = ReplyKeyboardMarkup([[g] for g in GAME_LIST] + [["رجوع"]], resize_keyboard=True)
            await update.message.reply_text("اختر اللعبة:", reply_markup=keyboard)

        elif msg == "📱 التطبيقات":
            keyboard = ReplyKeyboardMarkup([[a] for a in APP_LIST] + [["رجوع"]], resize_keyboard=True)
            await update.message.reply_text("اختر التطبيق:", reply_markup=keyboard)

        elif msg in ["📡 سيرياتيل", "📶 MTN"]:
            context.user_data["game"] = "Syriatel" if "سيرياتيل" in msg else "MTN"
            keyboard = ReplyKeyboardMarkup([[p] for p in products[context.user_data["game"]]] + [["رجوع"]], resize_keyboard=True)
            await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)

        elif msg == "👤 حسابي":
            await update.message.reply_text(
                f"""👤 حسابي

🆔 {uid}
💰 {balances.get(uid,0)}$
💸 {spent.get(uid,0)}$
📦 {len([o for o in orders.values() if o["user"]==uid])}
📅 {joined.get(uid)}"""
            )

        elif msg == "📦 طلباتي":
            user_orders = []
            for k, v in orders.items():
                if v["user"] == uid:
                    user_orders.append(f"#{k} - {v['pack']} - {v['status']}")
            await update.message.reply_text("\n".join(user_orders) if user_orders else "لا يوجد طلبات")

        elif msg == "📞 الدعم الفني":
            await update.message.reply_text(SUPPORT)

        return

    # ===== اختيار منتج =====
    if msg in products:
        context.user_data["game"] = msg
        keyboard = ReplyKeyboardMarkup([[p] for p in products[msg]] + [["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)

    elif "game" in context.user_data and "pack" not in context.user_data:
        context.user_data["pack"] = msg
        await update.message.reply_text("📩 أرسل ID الحساب")

    elif "pack" in context.user_data and "id" not in context.user_data:
        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]
        bal = balances.get(uid, 0)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")]
        ])

        await update.message.reply_text(
            f"📦 تأكيد\n🎮 {game}\n💎 {pack}\n🆔 {msg}\n💰 {price}$\n💳 {bal}$",
            reply_markup=keyboard
        )


# ===== BUTTON =====
async def button(update, context):
    global order_id
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        uid = str(query.from_user.id)
        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        if balances.get(uid, 0) < price:
            await query.edit_message_text("❌ رصيدك غير كافي")
            return

        balances[uid] -= price

        oid = str(order_id)
        order_id += 1

        orders[oid] = {
            "user": uid,
            "game": game,
            "pack": pack,
            "id": context.user_data["id"],
            "status": "pending"
        }

        save()

        await context.bot.send_message(
            ADMIN_ID,
            f"📦 طلب #{oid}\n👤 {uid}\n🎮 {game}\n💎 {pack}\n🆔 {context.user_data['id']}"
        )

        await query.edit_message_text(f"تم الطلب #{oid}")
        context.user_data.clear()


# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))

print("BOT RUNNING")
app.run_polling()
