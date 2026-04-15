import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TOKEN")

# 👑 الأدمن (إنت)
ADMIN_ID = 8015961726

# 💰 تخزين الرصيد
balances = {}

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

    if text == "💰 إيداع رصيد":
        await update.message.reply_text(
            "💳 طرق الدفع:\n\n"
            "🔵 شام كاش:\n"
            "417504d810333979a7affca09578fa75\n\n"
            "🟢 سيرياتيل كاش:\n"
            "00820198\n\n"
            "📩 بعد التحويل أرسل صورة الإيصال هنا"
        )

    elif text == "🛍 المنتجات":
        await update.message.reply_text("🛒 هذه قائمة المنتجات")

    elif text == "📋 طلباتي":
        await update.message.reply_text("📦 لا يوجد طلبات حالياً")

    elif text == "👤 حسابي":
        balance = balances[user_id]
        await update.message.reply_text(f"💰 رصيدك الحالي: {balance} ل.س")

    elif text == "💬 الدعم الفني":
        await update.message.reply_text("📞 تواصل معنا عبر @your_support")


# 📸 استقبال صور الإيصالات
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]

    # رد للزبون
    await update.message.reply_text("✅ تم استلام الإيصال، سيتم مراجعته")

    # إرسال الصورة للأدمن
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=f"📥 إيصال جديد\n👤 ID: {user_id}"
    )


# 💰 إضافة رصيد (للأدمن فقط)
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
        await update.message.reply_text("❌ استخدم هكذا:\n/add 123456 5000")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_balance))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()
