import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    text = update.message.text

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
        await update.message.reply_text("👤 معلومات حسابك")

    elif text == "💬 الدعم الفني":
        await update.message.reply_text("📞 تواصل معنا عبر @your_support")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
