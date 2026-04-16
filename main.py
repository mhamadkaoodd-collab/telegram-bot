import json
from telegram import *
from telegram.ext import *
from datetime import datetime

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726
SUPPORT_USERNAME = "@Star_IDOO796256363"

SHAM_NUMBER = "417504d810333979a7affca09578fa75"
SYRIATEL_NUMBER = "00820198"

# ===== DATA =====
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {"balances": {}, "orders": {}, "spent": {}, "counter": 1}

balances = data["balances"]
orders = data["orders"]
spent = data["spent"]
order_id = data["counter"]

def save():
    with open("data.json", "w") as f:
        json.dump({
            "balances": balances,
            "orders": orders,
            "spent": spent,
            "counter": order_id
        }, f)

# ===== المنتجات =====
products = {
    "PUBG MOBILE": {
        "60 UC": 0.9,
        "325 UC": 4.5,
    },
    "FREE FIRE": {
        "100💎": 1,
    }
}

# ===== START =====
async def start(update, context):
    keyboard = [
        ["🛍 المنتجات"],
        ["💰 إيداع رصيد", "📦 طلباتي"],
        ["👤 حسابي", "💳 طرق الدفع"],
        ["📞 الدعم الفني"]
    ]
    await update.message.reply_text(
        "⚡ مرحباً بك في متجر Haedr Shop\n👇 اختر من الأزرار:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ===== النصوص =====
async def text(update, context):
    global order_id
    uid = str(update.message.from_user.id)
    name = update.message.from_user.full_name
    username = update.message.from_user.username or "لا يوجد"

    msg = update.message.text

    # ===== المنتجات =====
    if msg == "🛍 المنتجات":
        keyboard = [[p] for p in products]
        keyboard.append(["🔙 رجوع"])
        await update.message.reply_text("🎮 اختر اللعبة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif msg in products:
        context.user_data["game"] = msg
        keyboard = [[p] for p in products[msg]]
        keyboard.append(["🔙 رجوع"])
        await update.message.reply_text("💎 اختر الشدة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif "game" in context.user_data and msg in products[context.user_data["game"]]:
        context.user_data["pack"] = msg
        await update.message.reply_text("📩 أرسل ID الحساب")

    elif "pack" in context.user_data and "id" not in context.user_data:
        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]
        bal = balances.get(uid, 0)

        after = round(bal - price, 2)

        keyboard = [
            ["✅ تأكيد الشراء"],
            ["❌ إلغاء"]
        ]

        text_msg = f"""
📦 تأكيد الطلب:

🎮 {game}
💎 {pack}
🆔 {msg}

💰 السعر: {price}$
💳 رصيدك الحالي: {bal}$
📉 بعد الشراء: {after}$

هل تريد تأكيد الشراء؟
"""
        await update.message.reply_text(text_msg, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif msg == "✅ تأكيد الشراء":
        game = context.user_data.get("game")
        pack = context.user_data.get("pack")
        price = products[game][pack]

        if balances.get(uid, 0) < price:
            await update.message.reply_text("❌ رصيدك غير كافي")
            return

        balances[uid] -= price
        spent[uid] = spent.get(uid, 0) + price

        oid = str(order_id)
        order_id += 1

        orders[oid] = {
            "user": uid,
            "game": game,
            "pack": pack,
            "id": context.user_data["id"]
        }

        save()

        await context.bot.send_message(ADMIN_ID,
            f"📥 طلب جديد #{oid}\n{orders[oid]}")

        await update.message.reply_text(f"✅ تم تنفيذ الطلب رقم #{oid}")
        context.user_data.clear()

    elif msg == "❌ إلغاء":
        context.user_data.clear()
        await update.message.reply_text("❌ تم الإلغاء")

    # ===== الإيداع =====
    elif msg == "💰 إيداع رصيد":
        keyboard = [
            ["💳 شام كاش", "📱 سيريتيل كاش"],
            ["🔙 رجوع"]
        ]
        await update.message.reply_text("اختر طريقة الدفع:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    elif msg == "💳 شام كاش":
        context.user_data["deposit"] = "sham"
        await update.message.reply_text(f"""💳 رقم شام كاش:
`{SHAM_NUMBER}`

📩 اكتب المبلغ الذي تريد شحنه:
""", parse_mode="Markdown")

    elif msg == "📱 سيريتيل كاش":
        context.user_data["deposit"] = "syriatel"
        await update.message.reply_text(f"""📱 رقم سيريتيل:
`{SYRIATEL_NUMBER}`

📩 اكتب المبلغ الذي تريد شحنه:
""", parse_mode="Markdown")

    elif "deposit" in context.user_data and "amount" not in context.user_data:
        try:
            amount = float(msg)
            context.user_data["amount"] = amount
            await update.message.reply_text("📸 أرسل صورة الإيصال الآن")
        except:
            await update.message.reply_text("❌ اكتب رقم فقط")

    # ===== طلباتي =====
    elif msg == "📦 طلباتي":
        user_orders = [o for o in orders.values() if o["user"] == uid]

        if not user_orders:
            await update.message.reply_text("📭 لا يوجد طلبات")
            return

        text_msg = "📦 طلباتك:\n\n"
        for o in user_orders:
            text_msg += f"{o['game']} - {o['pack']} - ID: {o['id']}\n"

        await update.message.reply_text(text_msg)

    # ===== حسابي =====
    elif msg == "👤 حسابي":
        bal = round(balances.get(uid, 0), 2)
        sp = round(spent.get(uid, 0), 2)

        text_msg = f"""👤 معلومات حسابي

🆔 ID: {uid}
👤 الاسم: {name}
📛 اليوزر: @{username}

💰 الرصيد: ${bal}
💸 المصروف: ${sp}

📦 الطلبات: {len([o for o in orders.values() if o['user']==uid])}
📅 تاريخ الانضمام: {datetime.now().strftime('%Y-%m-%d')}
"""
        await update.message.reply_text(text_msg)

    # ===== طرق الدفع =====
    elif msg == "💳 طرق الدفع":
        await update.message.reply_text(f"""💳 طرق الدفع:

شام كاش:
`{SHAM_NUMBER}`

سيريتيل:
`{SYRIATEL_NUMBER}`
""", parse_mode="Markdown")

    # ===== دعم =====
    elif msg == "📞 الدعم الفني":
        await update.message.reply_text(f"📞 تواصل مباشرة:\n{SUPPORT_USERNAME}")

# ===== صورة =====
async def photo(update, context):
    if "amount" not in context.user_data:
        return

    uid = str(update.message.from_user.id)
    amount = context.user_data["amount"]

    keyboard = [[
        InlineKeyboardButton("✅ قبول", callback_data=f"ok_{uid}_{amount}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}")
    ]]

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"📥 طلب شحن\n👤 {uid}\n💰 {amount}$",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ تم إرسال الطلب للإدارة")
    context.user_data.clear()

# ===== الأدمن =====
async def button(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("ok_"):
        _, uid, amount = data.split("_")
        amount = float(amount)

        balances[uid] = balances.get(uid, 0) + amount
        save()

        await context.bot.send_message(uid, f"✅ تم شحن {amount}$ إلى حسابك")
        await query.edit_message_caption("✅ تم القبول")

    elif data.startswith("no_"):
        uid = data.split("_")[1]
        await context.bot.send_message(uid, "❌ تم رفض الطلب")
        await query.edit_message_caption("❌ تم الرفض")

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))
app.add_handler(CallbackQueryHandler(button))

print("🔥 BOT WORKING")
app.run_polling()
