import json
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726
SUPPORT = "@Star_IDOO796256363"

SHAM = "417504d810333979a7affca09578fa75"
SYRIATEL = "00820198"

# ===== تحميل البيانات =====
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {"balances": {}, "orders": {}, "users": {}, "counter": 1}

balances = data["balances"]
orders = data["orders"]
users = data["users"]
order_id = data["counter"]

def save():
    with open("data.json", "w") as f:
        json.dump({
            "balances": balances,
            "orders": orders,
            "users": users,
            "counter": order_id
        }, f)

# ===== المنتجات =====
products = {
    "PUBG": {
        "60 UC": 0.9,
        "325 UC": 4.5,
    }
}

# ===== START =====
async def start(update, context):
    uid = str(update.message.from_user.id)

    if uid not in users:
        users[uid] = {
            "spent": 0,
            "orders": 0,
            "joined": str(update.message.date)
        }

    keyboard = [
        ["🛍 المنتجات"],
        ["💰 إيداع رصيد", "📦 طلباتي"],
        ["👤 حسابي", "💳 طرق الدفع"],
        ["📞 الدعم الفني"]
    ]

    await update.message.reply_text(
        "⚡ مرحبا بك في متجر الشيخ\nاختر من الأسفل 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ===== TEXT =====
async def text(update, context):
    global order_id

    msg = update.message.text
    uid = str(update.message.from_user.id)

    # ===== رجوع =====
    if msg == "🔙 رجوع":
        context.user_data.clear()
        return await start(update, context)

    # ===== المنتجات =====
    if msg == "🛍 المنتجات":
        keyboard = [[KeyboardButton(p)] for p in products]
        keyboard.append(["🔙 رجوع"])

        return await update.message.reply_text(
            "🎮 اختر لعبة:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # ===== اختيار لعبة =====
    if msg in products:
        context.user_data["game"] = msg

        keyboard = [[KeyboardButton(f"{p} - {products[msg][p]}$")] for p in products[msg]]
        keyboard.append(["🔙 رجوع"])

        return await update.message.reply_text(
            "💎 اختر الشدة:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # ===== اختيار باقة =====
    for game in products:
        for pack in products[game]:
            if msg.startswith(pack):
                context.user_data["pack"] = pack
                return await update.message.reply_text("📩 أرسل ID الحساب:")

    # ===== إدخال ID =====
    if "pack" in context.user_data and "id" not in context.user_data:
        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]
        bal = balances.get(uid, 0)

        keyboard = [
            ["✅ تأكيد الشراء"],
            ["❌ إلغاء"]
        ]

        return await update.message.reply_text(
            f"""📦 تأكيد الطلب:

🎮 {game}
💎 {pack}
🆔 {msg}

💰 السعر: {price}$
💳 رصيدك: {bal}$""",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # ===== تأكيد =====
    if msg == "✅ تأكيد الشراء":
        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        if balances.get(uid, 0) < price:
            return await update.message.reply_text("❌ رصيدك غير كافي")

        balances[uid] -= price

        oid = str(order_id)
        order_id += 1

        orders[oid] = {
            "user": uid,
            "game": game,
            "pack": pack,
            "id": context.user_data["id"],
            "status": "قيد التنفيذ"
        }

        users[uid]["orders"] += 1
        users[uid]["spent"] += price

        save()

        # إرسال للأدمن
        await context.bot.send_message(
            ADMIN_ID,
            f"""📥 طلب جديد #{oid}

👤 المستخدم: {uid}
🎮 اللعبة: {game}
💎 الباقة: {pack}
🆔 ID: {context.user_data['id']}
💰 السعر: {price}$"""
        )

        context.user_data.clear()
        return await update.message.reply_text("✅ تم إرسال طلبك")

    if msg == "❌ إلغاء":
        context.user_data.clear()
        return await update.message.reply_text("❌ تم الإلغاء")

    # ===== الإيداع =====
    if msg == "💰 إيداع رصيد":
        keyboard = [
            ["💳 شام كاش", "📱 سيرياتيل كاش"],
            ["🔙 رجوع"]
        ]
        return await update.message.reply_text("اختر الطريقة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    if msg == "💳 شام كاش":
        context.user_data["deposit"] = "شام كاش"
        return await update.message.reply_text(f"""💳 رقم شام كاش:
`{SHAM}`

✉️ اكتب المبلغ:""", parse_mode="Markdown")

    if msg == "📱 سيرياتيل كاش":
        context.user_data["deposit"] = "سيرياتيل"
        return await update.message.reply_text(f"""📱 رقم سيرياتيل:
`{SYRIATEL}`

✉️ اكتب المبلغ:""", parse_mode="Markdown")

    # ===== إدخال المبلغ =====
    if "deposit" in context.user_data and "amount" not in context.user_data:
        if not msg.replace(".", "").isdigit():
            return await update.message.reply_text("❌ اكتب رقم فقط")

        context.user_data["amount"] = msg
        return await update.message.reply_text("📸 أرسل صورة التحويل")

    # ===== حسابي =====
    if msg == "👤 حسابي":
        user = users.get(uid, {"spent":0,"orders":0})
        bal = balances.get(uid, 0)

        return await update.message.reply_text(
            f"""👤 معلومات حسابك

🆔 {uid}
💰 الرصيد: {bal}$
💸 المصروف: {user['spent']}$
📦 الطلبات: {user['orders']}"""
        )

    # ===== طلباتي =====
    if msg == "📦 طلباتي":
        text_orders = ""
        for oid, o in orders.items():
            if o["user"] == uid:
                text_orders += f"\n#{oid} | {o['game']} | {o['pack']} | {o['status']}"

        return await update.message.reply_text(text_orders or "لا يوجد طلبات")

    # ===== طرق الدفع =====
    if msg == "💳 طرق الدفع":
        return await update.message.reply_text(
            f"""💳 طرق الدفع:

شام كاش:
`{SHAM}`

سيرياتيل:
`{SYRIATEL}`""",
            parse_mode="Markdown"
        )

    # ===== دعم =====
    if msg == "📞 الدعم الفني":
        return await update.message.reply_text(f"راسل الدعم:\n{SUPPORT}")

# ===== الصورة (طلب الشحن) =====
async def photo(update, context):
    uid = str(update.message.from_user.id)

    if "amount" not in context.user_data:
        return

    amount = context.user_data["amount"]
    method = context.user_data["deposit"]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ قبول", callback_data=f"ok_{uid}_{amount}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}")
        ]
    ])

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"""📥 طلب شحن

👤 {uid}
💳 {method}
💰 {amount}$""",
        reply_markup=keyboard
    )

    await update.message.reply_text("⏳ تم إرسال طلبك")
    context.user_data.clear()

# ===== الأزرار (قبول/رفض) =====
async def button(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("ok_"):
        _, uid, amount = data.split("_")
        amount = float(amount)

        balances[uid] = balances.get(uid, 0) + amount
        save()

        await context.bot.send_message(uid, f"✅ تم شحن {amount}$")
        await query.edit_message_caption("✅ تم القبول")

    elif data.startswith("no_"):
        uid = data.split("_")[1]
        await context.bot.send_message(uid, "❌ تم الرفض")
        await query.edit_message_caption("❌ تم الرفض")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))
app.add_handler(CallbackQueryHandler(button))

print("🔥 BOT WORKING")
app.run_polling()
