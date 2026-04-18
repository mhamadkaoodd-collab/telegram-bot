import json
import os
import shutil
import threading
import re
import time
import datetime
import requests
import uuid
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAHfIbUkEOeS1s_K4dGx6tEJiWPowXoTOwo"
ADMIN_ID = 8015961726
SUPPORT = "@Star_IDOO796256363"

API_TOKEN = "dxupxt7yced8110nyh1buuos1"
BASE_URL = "https://mega-game.net/api/fast"

headers = {
    "api-token": API_TOKEN,
    "Content-Type": "application/json"
}

lock = threading.Lock()
last_click = {}
processed = set()

# تحميل البيانات
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

# إنشاء نسخة احتياطية
if not os.path.exists("data_backup.json") and os.path.exists("data.json"):
    shutil.copy("data.json", "data_backup.json")

data = load_data()

balances = data.get("balances", {})
orders = data.get("orders", {})
order_id = data.get("counter", 1)
spent = data.get("spent", {})
joined = data.get("joined", {})

# حفظ
def save():
    global order_id
    with lock:
        temp = "data_temp.json"
        with open(temp, "w") as f:
            json.dump({
                "balances": balances,
                "orders": orders,
                "counter": order_id,
                "spent": spent,
                "joined": joined
            }, f, indent=2)

        os.replace(temp, "data.json")
        shutil.copy("data.json", "data_backup.json")

# API إرسال طلب
def create_order_api(product_id, phone):
    order_uuid = str(uuid.uuid4())

    payload = {
        "uuid": order_uuid,
        "userdata": [
            {"key": "phone", "value": phone}
        ]
    }

    try:
        res = requests.post(
            f"{BASE_URL}/orders/{product_id}",
            json=payload,
            headers=headers,
            timeout=10
        )

        data = res.json()

        if data.get("err"):
            return False, data.get("msg")

        return True, data.get("data")

    except Exception as e:
        return False, str(e)

# المنتجات (مربوطة بالـ API)
products = {
    "PUBG": {
        "60 UC": {"price": 0.95, "id": 34},
        "325 UC": {"price": 4.75, "id": 39},
    },
    "Syriatel": {
        "40 ليرة - 0.38$": {"price": 0.38, "id": 0},
        "50 ليرة - 0.46$": {"price": 0.46, "id": 0},
    },
    "MTN": {
        "40 ليرة - 0.38$": {"price": 0.38, "id": 0},
        "50 ليرة - 0.46$": {"price": 0.46, "id": 0},
    }
}

def main_menu():
    return ReplyKeyboardMarkup([
        ["🛍 المنتجات"],
        ["💰 إيداع رصيد", "📦 طلباتي"],
        ["👤 حسابي", "📞 الدعم الفني"]
    ], resize_keyboard=True)

async def start(update, context):
    uid = str(update.message.from_user.id)

    if uid not in joined:
        joined[uid] = str(datetime.datetime.now())
        save()

    await update.message.reply_text("⚡ مرحبا بك في متجر الشيخ", reply_markup=main_menu())

async def text(update, context):
    global order_id

    uid = str(update.message.from_user.id)
    msg = update.message.text

    now = time.time()
    if uid in last_click and now - last_click[uid] < 1:
        return
    last_click[uid] = now

    if msg == "رجوع":
        context.user_data.clear()
        await update.message.reply_text("🔙 رجعت", reply_markup=main_menu())
        return

    if msg == "🛍 المنتجات":
        keyboard = ReplyKeyboardMarkup([
            ["🎮 الألعاب"],
            ["📡 سيرياتيل", "📶 MTN"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر القسم:", reply_markup=keyboard)

    elif msg == "🎮 الألعاب":
        context.user_data["game"] = "PUBG"
        keyboard = ReplyKeyboardMarkup([[p] for p in products["PUBG"]] + [["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)

    elif msg in ["📡 سيرياتيل", "📶 MTN"]:
        context.user_data["game"] = "Syriatel" if "سيرياتيل" in msg else "MTN"
        keyboard = ReplyKeyboardMarkup([[p] for p in products[context.user_data["game"]]] + [["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)

    elif "game" in context.user_data and "pack" not in context.user_data:
        if msg in products[context.user_data["game"]]:
            context.user_data["pack"] = msg
            await update.message.reply_text("📱 أرسل رقم الهاتف أو ID")

    elif "pack" in context.user_data and "id" not in context.user_data:
        if not re.fullmatch(r"09\d{8}|\d+", msg):
            await update.message.reply_text("❌ إدخال غير صحيح")
            return

        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]["price"]
        bal = balances.get(uid, 0)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ])

        await update.message.reply_text(
            f"📦 تأكيد الطلب\n🎮 {game}\n💎 {pack}\n📩 {msg}\n💰 {price}$\n💳 {bal}$",
            reply_markup=keyboard
        )

    elif msg == "📦 طلباتي":
        text_msg = ""

        for oid, v in orders.items():
            if v["user"] != uid:
                continue

            status = v.get("status", "pending")

            if status == "done":
                s = "✅ مكتمل"
            elif status == "rejected":
                s = "❌ مرفوض"
            else:
                s = "⏳ بالانتظار"

            text_msg += f"""
━━━━━━━━━━━━━━━
{s}
🎮 {v['pack']}
💰 {v['price']}
🆔 ID_{oid}
📩 {v['id']}
📅 {v['date']}
━━━━━━━━━━━━━━━
"""

        await update.message.reply_text(text_msg if text_msg else "❌ لا يوجد طلبات")

async def button(update, context):
    global order_id

    query = update.callback_query
    await query.answer()

    if query.id in processed:
        return
    processed.add(query.id)

    if query.data == "confirm":
        uid = str(query.from_user.id)
        game = context.user_data["game"]
        pack = context.user_data["pack"]

        product = products[game][pack]
        price = product["price"]
        product_id = product["id"]
        phone = context.user_data["id"]

        if balances.get(uid, 0) < price:
            await query.edit_message_text("❌ رصيدك غير كافي")
            return

        await query.edit_message_text("⏳ جاري تنفيذ الطلب...")

        success, response = create_order_api(product_id, phone)

        if not success:
            await query.edit_message_text(f"❌ فشل الطلب\n{response}")
            return

        with lock:
            balances[uid] -= price
            spent[uid] = spent.get(uid, 0) + price

            oid = str(order_id)
            order_id += 1

            orders[oid] = {
                "user": uid,
                "game": game,
                "pack": pack,
                "id": phone,
                "status": "pending",
                "price": price,
                "date": datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
            }

            save()

        await query.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

    elif query.data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ تم الإلغاء")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))

print("🔥 BOT WORKING")
app.run_polling()
