import json
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726

# ===== DATA =====
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {"balances": {}, "orders": {}, "counter": 1}

balances = data["balances"]
orders = data["orders"]
order_id = data["counter"]

def save():
    with open("data.json", "w") as f:
        json.dump({"balances": balances, "orders": orders, "counter": order_id}, f)

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
        [InlineKeyboardButton("🛍 المنتجات", callback_data="products")],
        [InlineKeyboardButton("💰 إيداع", callback_data="deposit")],
        [InlineKeyboardButton("👤 حسابي", callback_data="account")]
    ]
    await update.message.reply_text("🔥 متجر الشيخ VIP",
    reply_markup=InlineKeyboardMarkup(keyboard))

# ===== CALLBACK =====
async def button(update, context):
    global order_id
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = str(query.from_user.id)

    # ===== عرض المنتجات =====
    if data == "products":
        keyboard = [[InlineKeyboardButton(p, callback_data=f"game_{p}")] for p in products]
        await query.edit_message_text("🎮 اختر اللعبة:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== اختيار لعبة =====
    elif data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game

        keyboard = [[InlineKeyboardButton(f"{p} - {products[game][p]}$", callback_data=f"pack_{p}")]
                    for p in products[game]]

        await query.edit_message_text("💎 اختر الشدة:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== اختيار باقة =====
    elif data.startswith("pack_"):
        pack = data.replace("pack_", "")
        context.user_data["pack"] = pack

        await query.edit_message_text("📩 أرسل ID الحساب")

    # ===== تأكيد =====
    elif data == "confirm":
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
            "id": context.user_data["id"]
        }

        save()

        await context.bot.send_message(ADMIN_ID,
            f"📥 طلب جديد #{oid}\n{orders[oid]}")

        await query.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

    # ===== إلغاء =====
    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ تم الإلغاء")

    # ===== حساب =====
    elif data == "account":
        bal = balances.get(uid, 0)
        await query.edit_message_text(f"💰 رصيدك: {bal}$")

    # ===== إيداع =====
    elif data == "deposit":
        keyboard = [
            [InlineKeyboardButton("💳 شام كاش", callback_data="sham")],
            [InlineKeyboardButton("📱 سيرياتيل كاش", callback_data="syriatel")]
        ]
        await query.edit_message_text("اختر طريقة الدفع:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "sham":
        context.user_data["deposit"] = True
        await query.edit_message_text("💳 رقم شام كاش:\n123456789\n📸 أرسل صورة")

    elif data == "syriatel":
        context.user_data["deposit"] = True
        await query.edit_message_text("📱 رقم سيرياتيل:\n0987654321\n📸 أرسل صورة")

    # ===== قبول الإيداع =====
    elif data.startswith("ok_"):
        target = data.split("_")[1]
        context.user_data["target"] = target
        await query.message.reply_text("💰 اكتب المبلغ")

    elif data.startswith("no_"):
        target = data.split("_")[1]
        await context.bot.send_message(target, "❌ تم رفض الإيداع")

# ===== استقبال ID =====
async def text(update, context):
    uid = str(update.message.from_user.id)

    # ===== ID =====
    if "pack" in context.user_data and "id" not in context.user_data:
        context.user_data["id"] = update.message.text

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]
        bal = balances.get(uid, 0)

        keyboard = [
            [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ]

        text = f"""📦 تأكيد الطلب:

🎮 {game}
💎 {pack}
🆔 {context.user_data['id']}

💰 السعر: {price}$
💳 رصيدك: {bal}$"""

        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== إضافة رصيد =====
    elif "target" in context.user_data:
        try:
            amount = int(update.message.text)
            target = context.user_data["target"]

            balances[target] = balances.get(target, 0) + amount
            save()

            await context.bot.send_message(target, f"✅ تم شحن {amount}$")
            await update.message.reply_text("✔️ تم")
            context.user_data.clear()
        except:
            await update.message.reply_text("❌ رقم فقط")

# ===== صورة =====
async def photo(update, context):
    if "deposit" not in context.user_data:
        return

    uid = str(update.message.from_user.id)

    keyboard = [[
        InlineKeyboardButton("✅ قبول", callback_data=f"ok_{uid}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}")
    ]]

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"📥 إثبات دفع من {uid}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ جاري المراجعة")
    context.user_data.clear()

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))

print("🔥 PRO BOT RUNNING")
app.run_polling()
