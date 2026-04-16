import os
import logging
import requests

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# تفعيل اللوج
logging.basicConfig(level=logging.INFO)

# الإعدادات
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 8015961726

API_TOKEN = "dxupxt7yced8110nyh1buuos1"
BASE_URL = "https://mega-game.net/api"

balances = {}
products_cache = {}

# الكيبورد
keyboard = [
    ["🛒 المتجر", "💰 شحن الرصيد"],
    ["📦 طلباتي", "📞 الدعم"],
    ["👤 حسابي"]
]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# بدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balances[user_id] = balances.get(user_id, 0)

    await update.message.reply_text(
        "أهلاً بك 👋\nاختر من القائمة:",
        reply_markup=markup
    )

# جلب المنتجات من API
def get_products():
    url = f"{BASE_URL}/products"
    headers = {
        "api-token": API_TOKEN,
        "Accept": "application/json"
    }

    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        return data.get("data", [])
    except Exception as e:
        print("API Error:", e)
        return []

# عرض المتجر
async def show_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_products()

    if not products:
        await update.message.reply_text("❌ ما في منتجات حالياً")
        return

    text = "🛒 المنتجات:\n\n"
    for p in products[:10]:
        text += f"🔹 {p['name']}\n💵 السعر: {p['price']}\n\n"

    await update.message.reply_text(text)

# الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🛒 المتجر":
        await show_store(update, context)

    elif text == "💰 شحن الرصيد":
        await update.message.reply_text(
            "💳 طرق الدفع:\n\n"
            "🔹 سيرياتيل كاش:\n00820198\n\n"
            "📸 أرسل صورة الإيصال"
        )

    elif text == "👤 حسابي":
        balance = balances.get(user_id, 0)
        await update.message.reply_text(f"💰 رصيدك: {balance}")

    elif text == "📦 طلباتي":
        await update.message.reply_text("📦 لا يوجد طلبات حالياً")

    elif text == "📞 الدعم":
        await update.message.reply_text("📞 تواصل مع الدعم: @username")

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
