import os
import requests
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TOKEN")

ADMIN_ID = 8015961726

API_TOKEN = "dxupxt7yced8110nyh1buuos1"
BASE_URL = "https://mega-game.net/api/fast"

balances = {}
orders = {}
products_cache = {}

USD_RATE = 13600


# 🟢 القائمة الرئيسية
def main_menu():
    return ReplyKeyboardMarkup([
        ["💰 إيداع رصيد"],
        ["🛍 المنتجات", "📋 طلباتي"],
        ["👤 حسابي", "💬 الدعم الفني"]
    ], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    balances.setdefault(user_id, 0)
    orders.setdefault(user_id, [])

    await update.message.reply_text(
        "🏠 القائمة الرئيسية:",
        reply_markup=main_menu()
    )


# 🔥 جلب المنتجات
def get_products():
    try:
        url = f"{BASE_URL}/products"
        headers = {
            "api-token": API_TOKEN,
            "Accept": "application/json"
        }

        res = requests.get(url, headers=headers).json()

        if not res["err"]:
            return res["data"]["products"]
        return []

    except Exception as e:
        print("API ERROR:", e)
        return []


# 🔥 تنفيذ الطلب
def create_order(product_id, player_id):
    try:
        url = f"{BASE_URL}/order"
        headers = {
            "api-token": API_TOKEN,
            "Accept": "application/json"
        }

        data = {
            "product_id": product_id,
            "count": 1,
            "player_id": {
                "Player_ID": player_id
            }
        }

        return requests.post(url, json=data, headers=headers).json()

    except Exception as e:
        print("ORDER ERROR:", e)
        return {"err": True}


# 🧠 التحكم بالرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    balances.setdefault(user_id, 0)
    orders.setdefault(user_id, [])

    # 💰 إيداع
    if text == "💰 إيداع رصيد":
        await update.message.reply_text(
            "💳 طرق الدفع:\n\n"
            "🔵 شام كاش:\n417504d810333979a7affca09578fa75\n\n"
            "🟢 سيرياتيل كاش:\n00820198\n\n"
            "📩 أرسل صورة الإيصال"
        )

    # 🛍 المنتجات
    elif text == "🛍 المنتجات":
        products = get_products()

        if not products:
            await update.message.reply_text("❌ فشل تحميل المنتجات")
            return

        keyboard = []
        products_cache.clear()

        for p in products:
            name = p["name"]
            price_usd = round(float(p["price"]), 2)

            button_text = f"{name} - ${price_usd}"

            products_cache[button_text] = p
            keyboard.append([button_text])

        await update.message.reply_text(
            "🛒 اختر المنتج:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # 🎯 اختيار منتج
    elif text in products_cache:
        product = products_cache[text]
        context.user_data["selected_product"] = product

        await update.message.reply_text("📥 أرسل ID اللاعب")

    # 🧾 إدخال ID
    elif "selected_product" in context.user_data:
        product = context.user_data["selected_product"]
        player_id = text

        price_usd = float(product["price"])
        price_syp = price_usd * USD_RATE

        if balances[user_id] < price_syp:
            await update.message.reply_text("❌ رصيدك غير كافي")
            return

        # خصم
        balances[user_id] -= price_syp

        # تنفيذ
        res = create_order(product["id"], player_id)

        if not res.get("err"):
            await update.message.reply_text("✅ تم تنفيذ الطلب بنجاح")
        else:
            balances[user_id] += price_syp
            await update.message.reply_text("❌ فشل الطلب وتم إعادة الرصيد")

        del context.user_data["selected_product"]

    # 📋 طلباتي
    elif text == "📋 طلباتي":
        await update.message.reply_text("📦 الطلبات تتم تلقائياً من النظام")

    # 👤 حسابي
    elif text == "👤 حسابي":
        await update.message.reply_text(f"💰 رصيدك: {balances[user_id]:.0f} ل.س")

    # 💬 دعم
    elif text == "💬 الدعم الفني":
        await update.message.reply_text("📞 @your_support")

    else:
        await update.message.reply_text("❓ اختر من القائمة")


# 📸 الإيصالات
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]

    await update.message.reply_text("✅ تم استلام الإيصال")

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=f"📥 إيصال\n👤 ID: {user_id}"
    )


# 💰 إضافة رصيد
async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])

        balances.setdefault(user_id, 0)
        balances[user_id] += amount

        await update.message.reply_text("✅ تم الشحن")

    except:
        await update.message.reply_text("/add id amount")


# 🚀 تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_balance))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()
