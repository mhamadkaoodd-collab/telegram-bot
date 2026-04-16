import json
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726

# ===== تخزين =====
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

# ===== البيانات =====
games = [
    "PUBG MOBILE", "FREE FIRE", "CLASH OF CLANS", "CLASH ROYALE",
    "BRAWL STARS", "FC MOBILE", "CALL OF DUTY", "8BALL POOL"
]

apps = [
    "TikTok", "Google Play", "Pubg Voucher", "iTunes"
]

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🛍 المنتجات"],
        ["💰 رصيدي", "📋 طلباتي"],
        ["📥 إيداع", "💬 الدعم"]
    ]
    await update.message.reply_text(
        "🔥 متجر احترافي VIP",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ===== HANDLE =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_id

    text = update.message.text
    user = str(update.message.from_user.id)

    if user not in balances:
        balances[user] = 0

    # 🛍 المنتجات
    if text == "🛍 المنتجات":
        keyboard = [
            ["1️⃣ الألعاب", "2️⃣ التطبيقات"],
            ["3️⃣ سيرياتيل", "4️⃣ MTN"],
            ["🔙 رجوع"]
        ]
        await update.message.reply_text("اختر القسم:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # 🎮 الألعاب
    elif text == "1️⃣ الألعاب":
        keyboard = [[f"{i+1}️⃣ {g}"] for i, g in enumerate(games)]
        keyboard.append(["🔙 رجوع"])
        await update.message.reply_text("🎮 اختر لعبة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # اختيار لعبة
    elif any(g in text for g in games):
        context.user_data["game"] = text
        keyboard = [
            ["1️⃣ الفئة 1", "2️⃣ الفئة 2"],
            ["3️⃣ الفئة 3"],
            ["🔙 رجوع"]
        ]
        await update.message.reply_text("اختر الباقة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # اختيار باكج
    elif "الفئة" in text:
        context.user_data["pack"] = text
        await update.message.reply_text("📩 أرسل ID الحساب")

    # إدخال ID
    elif "pack" in context.user_data:
        game = context.user_data["game"]
        pack = context.user_data["pack"]

        oid = str(order_id)
        order_id += 1

        orders[oid] = {
            "user": user,
            "game": game,
            "pack": pack,
            "id": text,
            "status": "pending"
        }

        save()

        keyboard = [[InlineKeyboardButton("✅ تم التنفيذ", callback_data=f"done_{oid}")]]

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 طلب جديد\n\n🆔 #{oid}\n👤 {user}\n🎮 {game}\n📦 {pack}\n🆔 الحساب: {text}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await update.message.reply_text(f"✅ تم إرسال طلبك #{oid}")
        context.user_data.clear()

    # 📱 التطبيقات
    elif text == "2️⃣ التطبيقات":
        keyboard = [[f"{i+1}️⃣ {a}"] for i, a in enumerate(apps)]
        keyboard.append(["🔙 رجوع"])
        await update.message.reply_text("📱 اختر تطبيق:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # 📡 سيرياتيل
    elif text == "3️⃣ سيرياتيل":
        keyboard = [
            ["1️⃣ شحن رصيد", "2️⃣ دفع فاتورة"],
            ["3️⃣ سيرياتيل كاش"],
            ["🔙 رجوع"]
        ]
        await update.message.reply_text("📡 اختر الخدمة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # 📶 MTN
    elif text == "4️⃣ MTN":
        keyboard = [
            ["1️⃣ شحن رصيد", "2️⃣ دفع فاتورة"],
            ["🔙 رجوع"]
        ]
        await update.message.reply_text("📶 اختر الخدمة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # 🔙 رجوع
    elif text == "🔙 رجوع":
        await start(update, context)

    # 💰 رصيد
    elif text == "💰 رصيدي":
        await update.message.reply_text(f"💰 رصيدك: {balances[user]}")

    # 📋 طلباتي
    elif text == "📋 طلباتي":
        msg = "📦 طلباتك:\n\n"
        for oid, o in orders.items():
            if o["user"] == user:
                msg += f"#{oid} - {o['game']} - {o['pack']} - {o['status']}\n"
        await update.message.reply_text(msg if msg != "📦 طلباتك:\n\n" else "لا يوجد طلبات")

    # 📥 إيداع
    elif text == "📥 إيداع":
        await update.message.reply_text(
            "💰 طرق الإيداع:\n\n"
            "🔵 شام كاش:\n417504d810333979a7affca09578fa75\n\n"
            "🟢 سيرياتيل كاش:\n00820198\n\n"
            "📸 أرسل صورة التحويل"
        )

    # 💬 دعم
    elif text == "💬 الدعم":
        await update.message.reply_text("📞 تواصل @your_support")

# ===== صور =====
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = str(update.message.from_user.id)

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"💰 إيصال من {user}"
    )

    await update.message.reply_text("✅ تم إرسال الإيصال")

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
    if str(update.message.from_user.id) != str(ADMIN_ID):
        return

    try:
        uid = str(context.args[0])
        amount = int(context.args[1])

        balances[uid] = balances.get(uid, 0) + amount
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
