import os
import requests
import asyncio
import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# تفعيل اللوج
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")

ADMIN_ID = 8015961726

API_TOKEN = "dxupxt7yced8110nyh1buuos1"
BASE_URL = "https://mega-game.net/api/fast"

balances = {}
products_cache = {}
last_orders = {}

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

# 🚀 بدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    balances.setdefault(user_id, 0)

    await update.message.reply_text(
        "✨ أهلاً بك في متجر الشيخ\n\n"
        "💎 أسرع خدمة شحن ألعاب\n"
        "⚡ تنفيذ فوري وآمن\n\n"
        "اختر من القائمة للمتابعة:",
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
        return []
    except:
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

# 📦 جلب الطلبات
def get_orders():
    try:
        res = requests.get(
            f"{BASE_URL}/orders",
            headers={"api-token": API_TOKEN}
        ).json()

        if not res["err"]:
            return res["data"]["orders"]
        return []
    except:
        return []

# 🔔 متابعة الطلبات
async def check_orders(app):
    await asyncio.sleep(5)
    while True:
        try:
            orders = get_orders()

            for o in orders[:10]:
                oid = o["id"]
                status = o["status"]

                if oid not in last_orders:
                    last_orders[oid] = status
                    continue

                if last_orders[oid] != status:
                    last_orders[oid] = status

                    if status == "completed":
                        await app.bot.send_message(
                            chat_id=ADMIN_ID,
                            text=f"✅ تم تنفيذ الطلب رقم #{oid}"
                        )

        except Exception as e:
            print("CHECK ERROR:", e)

        await asyncio.sleep(20)

# 💬 الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    balances.setdefault(user_id, 0)

    # 💰 شحن
    if text == "💰 شحن الرصيد":
        await update.message.reply_text(
            "💳 طرق الدفع المتاحة:\n\n"
            "🔹 شام كاش:\n417504d810333979a7affca09578fa75\n\n"
            "🔹 سيرياتيل كاش:\n00820198\n\n"
            "📸 أرسل صورة الإيصال بعد التحويل"
        )

    # 🛍️ المتجر
    elif text == "🛍️ المتجر":
        products = get_products()

        if not products:
            await update.message.reply_text("❌ تعذر تحميل المنتجات حالياً")
            return

        keyboard = []
        products_cache.clear()

        for p in products:
            name = p["name"]
            price = round(float(p["price"]), 2)
            button = f"{name} - ${price}"

            products_cache[button] = p
            keyboard.append([button])

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
            await update.message.reply_text("✅ تم تنفيذ الطلب بنجاح 🎉")

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🛒 طلب جديد\n👤 {user_id}\n📦 {product['name']}\n🎮 {player_id}"
            )
        else:
            balances[user_id] += price
            await update.message.reply_text("❌ فشل الطلب وتم إعادة الرصيد")

        del context.user_data["product"]

    # 📦 طلباتي
    elif text == "📦 طلباتي":
        orders = get_orders()

        if not orders:
            await update.message.reply_text("📭 لا يوجد طلبات حالياً")
            return

        msg = "📦 آخر الطلبات:\n\n"

        for o in orders[:5]:
            status = "⏳ قيد التنفيذ" if o["status"] != "completed" else "✅ مكتمل"

            msg += (
                f"🆔 #{o['id']}\n"
                f"📦 المنتج: {o['product_id']}\n"
                f"💰 {round(float(o['amount']), 2)}$\n"
                f"{status}\n\n"
            )

        await update.message.reply_text(msg)

    # 👤 حسابي
    elif text == "👤 حسابي":
        await update.message.reply_text(
            f"👤 حسابك:\n\n💰 الرصيد: {balances[user_id]} ل.س"
        )

    # 📞 دعم
    elif text == "📞 الدعم":
        await update.message.reply_text("📞 تواصل معنا: @your_support")

    # 👑 لوحة التحكم
    elif text == "📊 لوحة التحكم" and user_id == ADMIN_ID:
        total_users = len(balances)
        total_money = sum(balances.values())

        await update.message.reply_text(
            f"📊 لوحة التحكم:\n\n"
            f"👥 عدد المستخدمين: {total_users}\n"
            f"💰 مجموع الأرصدة: {total_money}"
        )

    else:
        await update.message.reply_text("❗ اختر من القائمة")

# 📸 إيصالات
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    await update.message.reply_text("✅ تم استلام الإيصال وسيتم المراجعة")

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
    await update.message.reply_text("✅ تم الشحن")

# 🚀 تشغيل
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_balance))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    asyncio.create_task(check_orders(app))

    print("✅ Bot started...")
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
