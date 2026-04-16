import os
import requests
import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# 🔧 لوج
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")

ADMIN_ID = 8015961726

API_TOKEN = "dxupxt7yced8110nyh1buuos1"
BASE_URL = "https://mega-game.net/api/fast"

balances = {}
products_cache = {}

USD_RATE = 13600

# 🏠 القائمة الرئيسية
def main_menu(user_id):
    keyboard = [
        ["💰 شحن الرصيد"],
        ["🛍️ المتجر", "📦 طلباتي"],
        ["👤 حسابي", "📞 الدعم"]
    ]

    if user_id == ADMIN_ID:
        keyboard.append(["📊 لوحة التحكم"])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# 🚀 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    balances.setdefault(user_id, 0)

    await update.message.reply_text(
        "✨ أهلاً بك في متجر الشيخ\n\n"
        "💎 شحن ألعاب بشكل فوري\n"
        "⚡ سرعة - أمان - دعم مستمر\n\n"
        "اختر من القائمة:",
        reply_markup=main_menu(user_id)
    )

# 🔄 جلب المنتجات
def get_products():
    try:
        res = requests.get(
            f"{BASE_URL}/products",
            headers={"api-token": API_TOKEN}
        ).json()

        if not res["err"]:
            return res["data"]["products"]
    except:
        pass
    return []

# 🛒 تنفيذ الطلب
def create_order(product_id, player_id):
    try:
        res = requests.post(
            f"{BASE_URL}/order",
            headers={"api-token": API_TOKEN},
            json={
                "product_id": product_id,
                "count": 1,
                "player_id": {"Player_ID": player_id}
            }
        ).json()
        return res
    except:
        return {"err": True}

# 💬 الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    balances.setdefault(user_id, 0)

    # 💰 شحن
    if text == "💰 شحن الرصيد":
        await update.message.reply_text(
            "💳 طرق الدفع:\n\n"
            "🔹 شام كاش:\n417504d810333979a7affca09578fa75\n\n"
            "🔹 سيرياتيل كاش:\n00820198\n\n"
            "📸 أرسل صورة الإيصال"
        )

    # 🛍️ المتجر
    elif text == "🛍️ المتجر":
        products = get_products()

        if not products:
            await update.message.reply_text("❌ فشل تحميل المنتجات")
            return

        keyboard = []
        products_cache.clear()

        for p in products:
            name = p["name"]
            price = round(float(p["price"]), 2)

            btn = f"{name} - ${price}"
            products_cache[btn] = p

            keyboard.append([btn])

        await update.message.reply_text(
            "🛒 اختر المنتج:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # اختيار منتج
    elif text in products_cache:
        context.user_data["product"] = products_cache[text]
        await update.message.reply_text("📥 أرسل ID اللاعب:")

    # تنفيذ الطلب
    elif "product" in context.user_data:
        product = context.user_data["product"]
        player_id = text

        price = int(float(product["price"]) * USD_RATE)

        if balances[user_id] < price:
            await update.message.reply_text("❌ رصيدك غير كافي")
            return

        balances[user_id] -= price

        res = create_order(product["id"], player_id)

        if not res.get("err"):
            await update.message.reply_text("✅ تم الطلب بنجاح 🎉")
        else:
            balances[user_id] += price
            await update.message.reply_text("❌ فشل الطلب")

        del context.user_data["product"]

    # 📦 طلباتي
    elif text == "📦 طلباتي":
        await update.message.reply_text("📭 سيتم إضافتها قريباً")

    # 👤 حسابي
    elif text == "👤 حسابي":
        await update.message.reply_text(
            f"💰 رصيدك: {balances[user_id]} ل.س"
        )

    # 📞 دعم
    elif text == "📞 الدعم":
        await update.message.reply_text("📞 تواصل: @your_support")

    # 👑 لوحة تحكم
    elif text == "📊 لوحة التحكم" and user_id == ADMIN_ID:
        await update.message.reply_text(
            f"👥 المستخدمين: {len(balances)}\n"
            f"💰 مجموع الأموال: {sum(balances.values())}"
        )

    else:
        await update.message.reply_text("❗ اختر من القائمة")

# 📸 إيصال
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    await update.message.reply_text("✅ تم استلام الإيصال")

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"📥 إيصال\n👤 {user_id}"
    )

# 💰 إضافة رصيد
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    amount = int(context.args[1])

    balances.setdefault(user_id, 0)
    balances[user_id] += amount

    await context.bot.send_message(chat_id=user_id, text=f"💰 تم شحن {amount}")
    await update.message.reply_text("✅ تم")

# 🚀 تشغيل (مهم جداً)
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_balance))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🔥 BOT WORKING...")
    app.run_polling()

if __name__ == "__main__":
    main()
