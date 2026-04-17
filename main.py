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

# ===== تحميل البيانات بأمان =====
def load_data():
    default = {"balances": {}, "orders": {}, "counter": 1, "spent": {}, "joined": {}}

    if not os.path.exists("data.json"):
        return default

    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        print("⚠️ data.json خربان - استرجاع نسخة احتياطية")

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

# ===== المنتجات =====
products = {

    # ===== الألعاب =====
    "PUBG": {
        "60 UC": 0.95,
        "325 UC": 4.75,
        "660 UC": 9.5
    },
    "Free Fire": {"100 Diamonds": 1, "500 Diamonds": 5},
    "Call of Duty Mobile": {"80 CP": 1, "400 CP": 5},
    "eFootball": {"100 Coins": 1},
    "Mobile Legends": {"86 Diamonds": 2},
    "Clash of Clans": {"80 Gems": 1},
    "Clash Royale": {"80 Gems": 1},
    "Roblox": {"400 Robux": 5},

    # ===== تطبيقات اللايف =====
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

    # ===== رصيد =====
    "Syriatel": {"40 ليرة - 0.38$": 0.38},
    "MTN": {"40 ليرة - 0.38$": 0.38}
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

    if msg == "🛍 المنتجات":
        keyboard = ReplyKeyboardMarkup([
            ["🎮 الألعاب", "📱 التطبيقات"],
            ["📡 سيرياتيل", "📶 MTN"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر القسم:", reply_markup=keyboard)

    elif msg == "🎮 الألعاب":
        keyboard = ReplyKeyboardMarkup([
            ["PUBG", "Free Fire"],
            ["Call of Duty Mobile", "eFootball"],
            ["Mobile Legends", "Clash of Clans"],
            ["Clash Royale", "Roblox"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر اللعبة:", reply_markup=keyboard)

    elif msg == "📱 التطبيقات":
        keyboard = ReplyKeyboardMarkup([
            ["Bigo Live", "Party Star"],
            ["Exina Live", "Ahla Chat"],
            ["SoulChill", "Saba Chat"],
            ["IMO", "Q Chat"],
            ["Ho Chat", "Ya Ahla Chat"],
            ["Bella Chat", "Mego Live"],
            ["Yalla Live", "YoHo"],
            ["Yoyo Chat", "Haki Chat"],
            ["Up Live", "Solfa Chat"],
            ["Happy Chat", "Super Live"],
            ["Ayomi Chat", "Talk Talk"],
            ["Popo Live", "4Fun Chat"],
            ["Ohla Chat", "Koko Live"],
            ["Hiya Chat", "Taka Chat"],
            ["Likee", "Kwai"],
            ["Lego Live", "Lam Chat"],
            ["Hala"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر التطبيق:", reply_markup=keyboard)

    elif msg in products:

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
            f"""📦 تأكيد الطلب

🎮 {game}
💎 {pack}
🆔 {msg}

💰 السعر: {price}$
💳 رصيدك: {bal}$""",
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
        spent[uid] = spent.get(uid, 0) + price

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

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ تم الشحن", callback_data=f"done_{oid}_{uid}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{oid}_{uid}")
        ]])

        await context.bot.send_message(
            ADMIN_ID,
            f"📦 طلب جديد #{oid}\n👤 {uid}\n🎮 {game}\n💎 {pack}\n🆔 {context.user_data['id']}\n💰 {price}$",
            reply_markup=keyboard
        )

        await query.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))

print("🔥 BOT WORKING")
app.run_polling()
