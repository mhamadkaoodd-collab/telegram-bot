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

# جلب المنتجات (نسخة ذكية)
def get_products():
    headers = {
        "api-token": API_TOKEN,
        "Accept": "application/json"
    }

    endpoints = [
        "/products",
        "/services",
        "/items"
    ]

    for ep in endpoints:
        try:
            url = BASE_URL + ep
            res = requests.get(url, headers=headers, timeout=10)

            print("TRY:", url)
            print("STATUS:", res.status_code)
            print("RESPONSE:", res.text[:200])

            if res.status_code == 200:
                data = res.json()

                if isinstance(data, dict):
                    if "data" in data:
                        return data["data"]
                    elif "products" in data:
                        return data["products"]
                    else:
                        return list(data.values())[0]

                elif isinstance(data, list):
                    return data

        except Exception as e:
            print("ERROR:", e)

    return []

# عرض المتجر
async def show_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_products()

    if not products:
        await update.message.reply_text("❌ ما في منتجات حالياً (أو API غلط)")
        return

    text = "🛒 المنتجات:\n\n"

    for p in products[:10]:
        name = p.get("name", "بدون اسم")
        price = p.get("price", "؟")

        text += f"🔹 {name}\n💵 السعر: {price}\n\n"

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
