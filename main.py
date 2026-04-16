import json
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ⚠️ حط توكنك (غيره لاحقاً)
TOKEN = "8260446715:AAEuhMk61QkIxHC4HT2sHNjaeGDaz_AhZ3M"
ADMIN_ID = 8015961726

# ===== تحميل البيانات =====
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {"balances": {}, "orders": {}, "counter": 1}

balances = data["balances"]
orders = data["orders"]
order_id_counter = data["counter"]

def save():
    with open("data.json", "w") as f:
        json.dump({
            "balances": balances,
            "orders": orders,
            "counter": order_id_counter
        }, f)

# ===== الألعاب + الباكجات =====
games = {
    "PUBG MOBILE": ["60 UC", "325 UC", "660 UC", "1800 UC"],
    "FREE FIRE": ["100💎", "310💎", "520💎"],
    "CLASH OF CLANS": ["Gold Pass"],
    "BRAWL STARS": ["30 Gems", "80 Gems"],
    "CALL OF DUTY": ["80 CP", "400 CP"]
}

# ===== القائمة =====
main_menu = [
    ["🎮 الألعاب"],
    ["💰 رصيدي", "📋 طلباتي"],
    ["📥 إيداع", "💬 الدعم"]
]

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if user_id not in balances:
        balances[user_id] = 0
        save()

    await update.message.reply_text(
        "🔥 متجر احترافي VIP",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

# ===== HANDLE =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_id_counter

    user_id = str(update.message.from_user.id)
    text = update.message.text

    if user_id not in balances:
        balances[user_id] = 0

    # 🎮 الألعاب
    if text == "🎮 الألعاب":
        keyboard = [[g] for g in games.keys()]
        await update.message.reply_text(
            "🎮 اختر لعبة:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # اختيار لعبة
    elif text in games:
        context.user_data["game"] = text
        keyboard = [[p] for p in games[text]]

        await update.message.reply_text(
            f"📦 اختر الباكج:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # اختيار باكج
    elif "game" in context.user_data:
        context.user_data["pack"] = text
        await update.message.reply_text("📩 أرسل ID الحساب")

    # إدخال ID
    elif "pack" in context.user_data:
        game = context.user_data["game"]
        pack = context.user_data["pack"]

        oid = str(order_id_counter)
        order_id_counter += 1

        orders[oid] = {
            "user": user_id,
            "game": game,
            "pack": pack,
            "id": text,
            "status": "pending"
        }

        save()

        keyboard = [[InlineKeyboardButton("✅ تم التنفيذ", callback_data=f"done_{oid}")]]

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 طلب جديد\n\n🆔 #{oid}\n👤 {user_id}\n🎮 {game}\n📦 {pack}\n🆔 {text}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await update.message.reply_text(f"✅ تم إرسال طلبك #{oid}")

        context.user_data.clear()

    # 💰 رصيد
    elif text == "💰 رصيدي":
        await update.message.reply_text(f"💰 رصيدك: {balances[user_id]}")

    # 📋 طلباتي
    elif text == "📋 طلباتي":
        msg = "📦 طلباتك:\n\n"
        for oid, o in orders.items():
            if o["user"] == user_id:
                msg += f"#{oid} - {o['game']} - {o['pack']} - {o['status']}\n"

        await update.message.reply_text(msg if msg != "📦 طلباتك:\n\n" else "لا يوجد طلبات")

    # 📥 إيداع
    elif text == "📥 إيداع":
        await update.message.reply_text("📸 أرسل صورة التحويل")

    # 💬 دعم
    elif text == "💬 الدعم":
        await update.message.reply_text("📞 تواصل @your_support")

# ===== الصور =====
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"💰 إيصال\n👤 {user_id}"
    )

    await update.message.reply_text("✅ تم إرسال الإيصال")

# ===== تنفيذ =====
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    oid = query.data.replace("done_", "")

    if oid in orders:
        orders[oid]["status"] = "completed"
        save()

        user_id = orders[oid]["user"]

        await context.bot.send_message(
            chat_id=int(user_id),
            text=f"🎉 تم تنفيذ طلبك #{oid}"
        )

        await query.edit_message_text(f"✅ تم التنفيذ #{oid}")

# ===== إضافة رصيد =====
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != str(ADMIN_ID):
        return

    try:
        user = str(context.args[0])
        amount = int(context.args[1])

        balances[user] = balances.get(user, 0) + amount
        save()

        await update.message.reply_text("✅ تم شحن الرصيد")

    except:
        await update.message.reply_text("❌ استخدم:\n/add id amount")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(MessageHandler(filters.PHOTO, photo))
app.add_handler(CallbackQueryHandler(done))

print("🔥 BOT RUNNING")
app.run_polling()
