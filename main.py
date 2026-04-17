import json
import threading
import os
import shutil
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726
SUPPORT = "@Star_IDOO796256363"

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

balances = data["balances"]
orders = data["orders"]
order_id = data["counter"]
spent = data.get("spent", {})
joined = data.get("joined", {})

# ===== حفظ بدون تعليق + باكاب =====
def save():
    def _save():
        with open("data.json", "w") as f:
            json.dump({
                "balances": balances,
                "orders": orders,
                "counter": order_id,
                "spent": spent,
                "joined": joined
            }, f, indent=2)

        shutil.copy("data.json", "data_backup.json")

    threading.Thread(target=_save).start()

# ===== المنتجات =====
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
        "80 ليرة - 0.77$": 0.77,
        "100 ليرة - 0.96$": 0.96,
        "200 ليرة - 1.9$": 1.9,
    },
    "MTN": {
        "40 ليرة - 0.38$": 0.38,
        "50 ليرة - 0.46$": 0.46,
        "85 ليرة - 0.8$": 0.8,
        "100 ليرة - 0.96$": 0.96,
        "200 ليرة - 1.9$": 1.9,
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
        keyboard = ReplyKeyboardMarkup([["PUBG"], ["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر اللعبة:", reply_markup=keyboard)

    elif msg in ["PUBG", "TikTok", "Google Play"]:
        context.user_data["game"] = msg
        keyboard = ReplyKeyboardMarkup([[p] for p in products[msg]] + [["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)

    elif msg == "📱 التطبيقات":
        keyboard = ReplyKeyboardMarkup([["TikTok", "Google Play"], ["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر التطبيق:", reply_markup=keyboard)

    elif msg in ["📡 سيرياتيل", "📶 MTN"]:
        context.user_data["game"] = "Syriatel" if "سيرياتيل" in msg else "MTN"
        keyboard = ReplyKeyboardMarkup([[p] for p in products[context.user_data["game"]]] + [["رجوع"]], resize_keyboard=True)
        await update.message.reply_text("اختر الباقة:", reply_markup=keyboard)

    elif "game" in context.user_data and "pack" not in context.user_data:
        for p in products[context.user_data["game"]]:
            if msg.startswith(p):
                context.user_data["pack"] = p

                if context.user_data["game"] in ["Syriatel", "MTN"]:
                    await update.message.reply_text("📱 أرسل رقم الهاتف")
                else:
                    await update.message.reply_text("📩 أرسل ID الحساب")
                return

    elif "pack" in context.user_data and "id" not in context.user_data:
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
            f"""📦 تأكيد الطلب

🎮 {game}
💎 {pack}
🆔 {msg}

💰 السعر: {price}$
💳 رصيدك: {bal}$""",
            reply_markup=keyboard
        )

    elif msg == "💰 إيداع رصيد":
        keyboard = ReplyKeyboardMarkup([
            ["💳 شام كاش", "📱 سيرياتيل كاش"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر طريقة الدفع:", reply_markup=keyboard)

    elif msg == "💳 شام كاش":
        context.user_data["deposit"] = "sham"
        await update.message.reply_text("💳 رقم شام كاش:\n`417504d810333979a7affca09578fa75`\n\n✍️ اكتب المبلغ", parse_mode="Markdown")

    elif msg == "📱 سيرياتيل كاش":
        context.user_data["deposit"] = "syriatel"
        await update.message.reply_text("📱 رقم سيرياتيل:\n`00820198`\n\n✍️ اكتب المبلغ", parse_mode="Markdown")

    elif "deposit" in context.user_data and "amount" not in context.user_data:
        try:
            context.user_data["amount"] = float(msg)
            await update.message.reply_text("📸 أرسل صورة الإيصال")
        except:
            await update.message.reply_text("❌ اكتب رقم فقط")

    elif msg == "📦 طلباتي":
        user_orders = []
        for k, v in orders.items():
            if v["user"] == uid:
                status = v.get("status", "pending")

                if status == "done":
                    s = "✅ تم الشحن"
                elif status == "rejected":
                    s = "❌ تم الرفض"
                else:
                    s = "⏳ قيد الانتظار"

                user_orders.append(f"#{k} - {v['pack']} - {s}")

        await update.message.reply_text("\n".join(user_orders) if user_orders else "❌ لا يوجد طلبات")

    elif msg == "👤 حسابي":
        await update.message.reply_text(f"""👤 معلومات حسابي

🆔 {uid}
💰 الرصيد: {balances.get(uid,0)}$
💸 المصروف: {spent.get(uid,0)}$
📦 الطلبات: {len([o for o in orders.values() if o["user"]==uid])}
📅 الانضمام: {joined.get(uid)}""")

    elif msg == "📞 الدعم الفني":
        await update.message.reply_text(f"راسل الدعم: {SUPPORT}")

# ===== PHOTO =====
async def photo(update, context):
    if "deposit" not in context.user_data:
        return

    uid = str(update.message.from_user.id)
    amount = context.user_data["amount"]

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ قبول", callback_data=f"ok_{uid}_{amount}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}")
    ]])

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"📥 طلب شحن\n👤 {uid}\n💰 {amount}$",
        reply_markup=keyboard
    )

    await update.message.reply_text("⏳ تم إرسال طلبك")
    context.user_data.clear()

# ===== BUTTON =====
async def button(update, context):
    global order_id

    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "confirm":
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

        orders[oid] = {"user": uid, "game": game, "pack": pack, "id": context.user_data["id"], "status": "pending"}
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

    elif data.startswith("done_"):
        _, oid, uid = data.split("_")
        orders[oid]["status"] = "done"
        save()
        await context.bot.send_message(uid, f"✅ تم تنفيذ طلبك #{oid}")
        await query.edit_message_text(f"✅ تم الشحن #{oid}")

    elif data.startswith("reject_"):
        _, oid, uid = data.split("_")
        orders[oid]["status"] = "rejected"
        save()
        await context.bot.send_message(uid, "❌ تم رفض الطلب")
        await query.edit_message_text("❌ تم الرفض")

    elif data.startswith("ok_"):
        _, uid, amount = data.split("_")
        balances[uid] = balances.get(uid, 0) + float(amount)
        save()
        await context.bot.send_message(uid, f"✅ تم شحن {amount}$")
        await query.edit_message_caption("✅ تم القبول")

    elif data.startswith("no_"):
        uid = data.split("_")[1]
        await context.bot.send_message(uid, "❌ تم رفض الطلب")
        await query.edit_message_caption("❌ تم الرفض")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))

print("🔥 BOT WORKING")
app.run_polling()
