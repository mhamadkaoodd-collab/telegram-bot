import json
import os
import shutil
import threading
import re
import time
import datetime
import logging
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAHfIbUkEOeS1s_K4dGx6tEJiWPowXoTOwo"
ADMIN_ID = 8015961726
SUPPORT = "@Star_IDOO796256363"

logging.basicConfig(level=logging.ERROR)

lock = threading.Lock()
last_click = {}
processed = set()

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

def save():
    global order_id
    with lock:
        temp_file = "data_temp.json"

        with open(temp_file, "w") as f:
            json.dump({
                "balances": balances,
                "orders": orders,
                "counter": order_id,
                "spent": spent,
                "joined": joined
            }, f, indent=2)

        os.replace(temp_file, "data.json")
        shutil.copy("data.json", "data_backup.json")

products = {
    "PUBG": {
        "60 UC": 0.95,
        "325 UC": 4.75,
        "660 UC": 9.5,
        "1800 UC": 23.62,
        "3850 UC": 47.5,
        "8100 UC": 95,
    },
    "TikTok": {
        "1000 Coins": 1,
        "5000 Coins": 5,
    },
    "Google Play": {
        "5$": 5,
        "10$": 10,
    },
    "Syriatel": {
        "40 ليرة - 0.38$": 0.38,
        "50 ليرة - 0.46$": 0.46,
    },
    "MTN": {
        "40 ليرة - 0.38$": 0.38,
        "50 ليرة - 0.46$": 0.46,
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

    # 📞 الدعم الفني (يفتح الحساب)
    if msg == "📞 الدعم الفني":
        await update.message.reply_text(f"https://t.me/{SUPPORT.replace('@','')}")
        return

    # 💰 إيداع رصيد
    elif msg == "💰 إيداع رصيد":
        keyboard = ReplyKeyboardMarkup([
            ["سيرياتيل كاش", "شام كاش"],
            ["رجوع"]
        ], resize_keyboard=True)

        await update.message.reply_text("اختر طريقة الدفع:", reply_markup=keyboard)
        return

    elif msg == "سيرياتيل كاش":
        await update.message.reply_text("📲 أرسل صورة التحويل أو تواصل مع الدعم")
        return

    elif msg == "شام كاش":
        await update.message.reply_text("📲 أرسل صورة التحويل أو تواصل مع الدعم")
        return

    # 🎮 الألعاب
    elif msg == "🎮 الألعاب":
        context.user_data["game"] = "PUBG"
        keyboard = ReplyKeyboardMarkup([[p] for p in products["PUBG"]] + [["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)
        return

    # 📱 التطبيقات
    elif msg == "📱 التطبيقات":
        keyboard = ReplyKeyboardMarkup([
            ["TikTok", "Google Play"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر التطبيق:", reply_markup=keyboard)
        return

    elif msg in ["TikTok", "Google Play"]:
        context.user_data["game"] = msg
        keyboard = ReplyKeyboardMarkup([[p] for p in products[msg]] + [["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)
        return

    # 🛍 المنتجات
    if msg == "🛍 المنتجات":
        keyboard = ReplyKeyboardMarkup([
            ["🎮 الألعاب", "📱 التطبيقات"],
            ["📡 سيرياتيل", "📶 MTN"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر القسم:", reply_markup=keyboard)

    elif msg in ["📡 سيرياتيل", "📶 MTN"]:
        context.user_data["game"] = "Syriatel" if "سيرياتيل" in msg else "MTN"
        keyboard = ReplyKeyboardMarkup([[p] for p in products[context.user_data["game"]]] + [["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)

    elif "game" in context.user_data and "pack" not in context.user_data:
        if msg in products[context.user_data["game"]]:
            context.user_data["pack"] = msg
            await update.message.reply_text("📱 أرسل رقم الهاتف")

    elif "pack" in context.user_data and "id" not in context.user_data:

        msg = msg.strip()

        if not msg.isdigit():
            await update.message.reply_text("❌ الرقم يجب أن يحتوي على أرقام فقط")
            return

        if len(msg) != 10 or not msg.startswith("09"):
            await update.message.reply_text("❌ رقم غير صحيح")
            return

        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]
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
                s = "✅ الحالة: مكتمل"
            elif status == "rejected":
                s = "❌ الحالة: مرفوض"
            else:
                s = "⏳ الحالة: بالانتظار"

            text_msg += f"""
━━━━━━━━━━━━━━━
{s}
🎮 المنتج: {v['pack']}
💰 السعر: {v.get('price')}
🆔 رقم الطلب: ID_{oid}
📩 player_id: {v['id']}
📅 التاريخ: {v.get('date')}
━━━━━━━━━━━━━━━
"""

        await update.message.reply_text(text_msg if text_msg else "❌ لا يوجد طلبات")

    elif msg == "👤 حسابي":
        bal = balances.get(uid, 0)
        total_spent = spent.get(uid, 0)
        total_orders = len([o for o in orders.values() if o["user"] == uid])

        await update.message.reply_text(f"""
👤 معلومات حسابك

💰 رصيدك: {bal}$
💸 إجمالي ما صرفت: {total_spent}$

📦 عدد الطلبات: {total_orders}

🆔 ID: {uid}
""")

async def button(update, context):
    global order_id

    query = update.callback_query
    await query.answer()

    if query.id in processed:
        return
    processed.add(query.id)

    if query.data == "confirm":
        uid = str(query.from_user.id)

        if context.user_data.get("confirmed"):
            return

        context.user_data["confirmed"] = True

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        if balances.get(uid, 0) < price:
            await query.edit_message_text("❌ رصيدك غير كافي")
            context.user_data.clear()
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
            "status": "pending",
            "price": price,
            "date": datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        }

        save()

        # إشعار الأدمن
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"طلب جديد\nID_{oid}\n{game} - {pack}\n{context.user_data['id']}"
        )

        await query.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))

print("🔥 BOT WORKING")
app.run_polling()
