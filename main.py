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
        return default

data = load_data()
balances = data.get("balances", {})
orders = data.get("orders", {})
order_id = data.get("counter", 1)
spent = data.get("spent", {})
joined = data.get("joined", {})

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

# 🔥 جلب المنتجات من الشركة
def fetch_products():
    try:
        r = requests.get(f"{BASE_URL}/products", headers=headers)
        data = r.json()
        if not data["err"]:
            return data["data"]["products"]
        return []
    except:
        return []

# 🔥 تنفيذ الطلب
def create_order_api(product_id, phone):
    payload = {
        "uuid": str(uuid.uuid4()),
        "userdata": [{"key": "phone", "value": phone}]
    }
    try:
        r = requests.post(f"{BASE_URL}/orders/{product_id}", json=payload, headers=headers)
        data = r.json()
        if data.get("err"):
            return False, data.get("msg")
        return True, data.get("data")
    except Exception as e:
        return False, str(e)

# 🧠 تحميل المنتجات تلقائي
products = {}

def load_products():
    global products
    prods = fetch_products()
    for p in prods:
        name = p.get("name")
        pid = p.get("id")
        price = float(p.get("price", 0))
        products[name] = {"price": price, "id": pid}

load_products()

# الواجهة
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

    if msg == "رجوع":
        context.user_data.clear()
        await update.message.reply_text("🔙 رجعت", reply_markup=main_menu())
        return

    if msg == "🛍 المنتجات":
        keyboard = ReplyKeyboardMarkup(
            [[name] for name in list(products.keys())[:20]] + [["رجوع"]],
            resize_keyboard=True
        )
        await update.message.reply_text("اختر المنتج:", reply_markup=keyboard)

    elif msg in products:
        context.user_data["product"] = msg
        await update.message.reply_text("📱 أرسل رقم الهاتف")

    elif "product" in context.user_data and "id" not in context.user_data:
        if not re.fullmatch(r"09\d{8}", msg):
            await update.message.reply_text("❌ رقم غير صحيح")
            return

        context.user_data["id"] = msg

        product = products[context.user_data["product"]]
        price = product["price"]
        bal = balances.get(uid, 0)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ])

        await update.message.reply_text(
            f"📦 تأكيد الطلب\n💎 {context.user_data['product']}\n📩 {msg}\n💰 {price}$\n💳 {bal}$",
            reply_markup=keyboard
        )

    elif msg == "📦 طلباتي":
        text_msg = ""
        for oid, v in orders.items():
            if v["user"] != uid:
                continue

            text_msg += f"""
━━━━━━━━━━━━━━━
🎮 {v['product']}
💰 {v['price']}
🆔 {oid}
📩 {v['id']}
━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(text_msg if text_msg else "❌ لا يوجد طلبات")

    elif msg == "👤 حسابي":
        await update.message.reply_text(f"💰 {balances.get(uid,0)}$\n🆔 {uid}")

    elif msg == "📞 الدعم الفني":
        await update.message.reply_text(SUPPORT)

    elif msg == "💰 إيداع رصيد":
        await update.message.reply_text("📸 أرسل صورة التحويل")

async def button(update, context):
    global order_id
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        uid = str(query.from_user.id)
        product_name = context.user_data["product"]
        product = products[product_name]

        if balances.get(uid, 0) < product["price"]:
            await query.edit_message_text("❌ رصيدك غير كافي")
            return

        await query.edit_message_text("⏳ جاري التنفيذ...")

        success, response = create_order_api(product["id"], context.user_data["id"])

        if not success:
            await query.edit_message_text("❌ فشل الطلب")
            return

        balances[uid] -= product["price"]

        oid = str(order_id)
        order_id += 1

        orders[oid] = {
            "user": uid,
            "product": product_name,
            "id": context.user_data["id"],
            "price": product["price"]
        }

        save()

        await query.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))

print("🔥 BOT WORKING")
app.run_polling()
