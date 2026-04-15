import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TOKEN")

ADMIN_ID = 123456789  # حط ID تبعك

# 🔥 تخزين الرصيد
balances = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # عرض ID (مؤقت)
    await update.message.reply_text(f"ID: {user_id}")

    if user_id not in balances:
        balances[user_id] = 0

    keyboard = [
        ["💰 إيداع رصيد"],
        ["🛍 المنتجات", "📋 طلباتي"],
        ["👤 حسابي", "💬 الدعم الفني"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🏠 القائمة
