import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TOKEN")

# 👑 الأدمن
ADMIN_ID = 8015961726

# 💰 تخزين الرصيد
balances = {}

# 📦 تخزين الطلبات المؤقتة
orders = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in balances:
        balances[user_id] = 0

    keyboard = [
        ["💰 إيداع رصيد"],
        ["🛍 المنتجات", "📋 طلباتي"],
        ["👤 حسابي", "💬 الدعم الفني"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🏠 القائمة الرئيسية:\nاختر الخدمة:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in balances:
        balances[user_id] = 0

    # 💰 إيداع
    if text == "💰 إيداع رصيد":
        await update.message.reply_text(
            "💳 طرق الدفع:\n\n"
            "🔵 شام كاش:\n417504d810333979a7affca09578fa75\n\n"
            "🟢 سيرياتيل كاش:\n00820198\n\n"
            "📩 بعد التحويل أرسل صورة الإيصال هنا"
        )

    # 🛍 المنتجات
    elif text == "🛍 المنتجات":
        await update.message.reply_text(
            "🎮 قائمة الألعاب:\n\n"
            "🔹 PUBG\n\n"
            "اكتب: PUBG"
        )

    # 🎮 PUBG
    elif text == "PUBG":
        await update.message.reply_text(
            "🎮 شحن شدات PUBG:\n\n"
            "60 UC\n325 UC\n660 UC\n\n"
            "✏️ اكتب الكمية التي تريدها"
        )

    # اختيار باقة
    elif text in ["60 UC", "325 UC", "660 UC"]:
        orders[user_id] = {"product": text}
        await update.message.reply_text("📥 أرسل ID اللاعب")

    # إدخال ID
    elif user_id in orders:
        product = orders[user_id]["product"]
        player_id = text

        # إرسال الطلب للأدمن
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🛒 طلب جديد\n\n"
                f"👤 المستخدم: {user_id}\n"
                f"🎮 ID: {player_id}\n"
                f"📦 المنتج: {product}"
            )
        )

        await update.message.reply_text("✅ تم إرسال طلبك، سيتم التنفيذ قريباً")

        del orders[user_id]

    elif text == "📋 طلباتي":
        await update.message.reply_text("📦 سيتم عرض الطلبات لاحقاً")

    elif text == "👤 حسابي":
        balance = balances[user_id]
        await update.message.reply_text(f"💰 رصيدك الحالي: {balance} ل.س")

    elif text == "💬 الدعم الفني":
        await update.message.reply_text("📞 تواصل معنا عبر @your_support")

# 📸 استقبال الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]

    await update.message.reply_text("✅ تم استلام الإيصال، سيتم مراجعته")

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=f"📥 إيصال جديد\n👤 ID: {user_id}"
    )

# 💰 إضافة رصيد
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])

        if user_id not in balances:
            balances[user_id] = 0

        balances[user_id] += amount

        await update.message.reply_text(f"✅ تم إضافة {amount} للمستخدم {user_id}")

    except:
        await update.message.reply_text("❌ استخدم:\n/add 123456 5000")

# ✅ إنهاء الطلب (شحن تم)
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ تم شحن طلبك بنجاح 🎉"
        )

        await update.message.reply_text("✅ تم إبلاغ المستخدم")

    except:
        await update.message.reply_text("❌ استخدم:\n/done user_id")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_balance))
app.add_handler(CommandHandler("done", done))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()
