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

        game = context.user_data["game"]

        msg = msg.strip()

        if not msg.isdigit():
            await update.message.reply_text("❌ الرقم يجب أن يحتوي على أرقام فقط")
            return

        if len(msg) < 10:
            await update.message.reply_text("❌ الرقم ناقص (يجب أن يكون 10 أرقام)")
            return

        if len(msg) > 10:
            await update.message.reply_text("❌ الرقم أطول من اللازم (يجب 10 أرقام فقط)")
            return

        if not msg.startswith("09"):
            await update.message.reply_text("❌ يجب أن يبدأ الرقم بـ 09")
            return

        context.user_data["id"] = msg

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
        join_date = joined.get(uid, "غير معروف")

        await update.message.reply_text(f"""
👤 معلومات حسابك

💰 رصيدك: {bal}$
💸 إجمالي ما صرفت: {total_spent}$

📦 عدد الطلبات: {total_orders}

📅 تاريخ الانضمام:
{join_date}

🆔 ID: {uid}
""")

async def button(update, context):
    global order_id

    query = update.callback_query
    await query.answer()

    if query.id in processed:
        return
    processed.add(query.id)

    # أوامر الأدمن
    if query.data.startswith("done_") or query.data.startswith("reject_"):
        if str(query.from_user.id) != str(ADMIN_ID):
            return

        oid = query.data.split("_")[1]

        if oid not in orders:
            return

        if query.data.startswith("done_"):
            orders[oid]["status"] = "done"
            status_text = "✅ تم شحن طلبك بنجاح"
        else:
            orders[oid]["status"] = "rejected"
            status_text = "❌ تم رفض طلبك"

        save()

        user_id = int(orders[oid]["user"])

        await context.bot.send_message(
            chat_id=user_id,
            text=f"{status_text}\n🆔 ID_{oid}"
        )

        await query.edit_message_text(f"تم تحديث الطلب {oid}")
        return

    if query.data == "confirm":
        uid = str(query.from_user.id)

        if context.user_data.get("confirmed"):
            return

        context.user_data["confirmed"] = True

        if "game" not in context.user_data or "pack" not in context.user_data or "id" not in context.user_data:
            return

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        with lock:
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
        admin_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تم الشحن", callback_data=f"done_{oid}")],
            [InlineKeyboardButton("❌ رفض", callback_data=f"reject_{oid}")]
        ])

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""
📥 طلب جديد

🆔 ID_{oid}
👤 المستخدم: {uid}
🎮 {game}
💎 {pack}
📩 {context.user_data["id"]}
💰 {price}$
""",
            reply_markup=admin_keyboard
        )

        await query.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))

print("🔥 BOT WORKING")
app.run_polling()
