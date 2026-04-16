import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726

# ===== تحميل =====
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

# ===== الألعاب + الأسعار =====
games = {
    "PUBG": {"60 UC": 1, "325 UC": 5, "660 UC": 10},
    "FREE FIRE": {"100💎": 1, "310💎": 3},
    "BRAWL STARS": {"30 Gems": 2, "80 Gems": 5}
}

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍 المنتجات", callback_data="products")],
        [InlineKeyboardButton("💰 رصيدي", callback_data="balance")],
        [InlineKeyboardButton("📋 طلباتي", callback_data="orders")]
    ]
    await update.message.reply_text("🔥 متجر LEVEL 4", reply_markup=InlineKeyboardMarkup(keyboard))

# ===== CALLBACK =====
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_id

    query = update.callback_query
    await query.answer()
    data = query.data
    user = str(query.from_user.id)

    if user not in balances:
        balances[user] = 0

    # 🛍 المنتجات
    if data == "products":
        keyboard = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in games]
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main")])
        await query.edit_message_text("🎮 اختر لعبة:", reply_markup=InlineKeyboardMarkup(keyboard))

    # 🎮 لعبة
    elif data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game

        keyboard = [
            [InlineKeyboardButton(f"{p} 💰{price}$", callback_data=f"pack_{p}")]
            for p, price in games[game].items()
        ]
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="products")])

        await query.edit_message_text(f"📦 {game}", reply_markup=InlineKeyboardMarkup(keyboard))

    # 📦 باكج
    elif data.startswith("pack_"):
        pack = data.split("_")[1]
        game = context.user_data["game"]
        price = games[game][pack]

        if balances[user] < price:
            await query.answer("❌ رصيدك غير كافي", show_alert=True)
            return

        context.user_data["pack"] = pack
        await query.edit_message_text("📩 أرسل ID الحساب")

    # 💰 الرصيد
    elif data == "balance":
        await query.edit_message_text(f"💰 رصيدك: {balances[user]}$")

    # 📋 الطلبات
    elif data == "orders":
        msg = ""
        for oid, o in orders.items():
            if o["user"] == user:
                msg += f"#{oid} - {o['game']} - {o['status']}\n"
        await query.edit_message_text(msg if msg else "لا يوجد طلبات")

    elif data == "main":
        await start(update, context)

# ===== استقبال ID =====
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_id

    if "pack" in context.user_data:
        user = str(update.message.from_user.id)
        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = games[game][pack]

        oid = str(order_id)
        order_id += 1

        balances[user] -= price

        orders[oid] = {
            "user": user,
            "game": game,
            "pack": pack,
            "status": "pending"
        }

        save()

        keyboard = [[InlineKeyboardButton("✅ تم التنفيذ", callback_data=f"done_{oid}")]]

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 طلب جديد\n#{oid}\n🎮 {game}\n📦 {pack}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await update.message.reply_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

# ===== تنفيذ =====
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    oid = query.data.split("_")[1]

    if oid in orders:
        orders[oid]["status"] = "completed"
        save()

        await context.bot.send_message(
            chat_id=int(orders[oid]["user"]),
            text=f"🎉 تم تنفيذ طلبك #{oid}"
        )

        await query.edit_message_text(f"✅ تم التنفيذ #{oid}")

# ===== إضافة رصيد =====
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    user = str(context.args[0])
    amount = int(context.args[1])

    balances[user] = balances.get(user, 0) + amount
    save()

    await update.message.reply_text("✅ تم الشحن")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(CallbackQueryHandler(done))
app.add_handler(MessageHandler(filters.TEXT, message_handler))

print("🔥 LEVEL 4 BOT RUNNING")
app.run_polling()
