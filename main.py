import json
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726

# ===== DATA =====
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

# ===== PUBG PACKS =====
pubg = {
    "💎 60 UC - 0.9$": 0.9,
    "💎 325 UC - 4.5$": 4.5,
    "💎 660 UC - 9$": 9,
    "💎 1800 UC - 22$": 22,
    "💎 3850 UC - 45$": 45,
    "💎 8100 UC - 91$": 91
}

# ===== START =====
async def start(update, context):
    keyboard = [
        ["🛍 المنتجات"],
        ["💰 إيداع", "📦 طلباتي"],
        ["👤 حسابي"]
    ]
    await update.message.reply_text("🔥 متجر الشيخ VIP", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== PRODUCTS =====
async def products(update, context):
    keyboard = [["🎮 PUBG MOBILE"], ["🔙 رجوع"]]
    await update.message.reply_text("اختر:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== PUBG =====
async def pubg_menu(update, context):
    keyboard = [[p] for p in pubg.keys()]
    keyboard.append(["🔙 رجوع"])
    await update.message.reply_text("اختر الشدة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== SELECT PACK =====
async def select_pack(update, context):
    text = update.message.text
    context.user_data["price"] = pubg[text]
    context.user_data["pack"] = text
    await update.message.reply_text("📩 أرسل ID الحساب")

# ===== GET ID =====
async def get_id(update, context):
    context.user_data["id"] = update.message.text

    uid = str(update.message.from_user.id)
    bal = balances.get(uid, 0)
    price = context.user_data["price"]

    await update.message.reply_text(
        f"📦 تأكيد الشراء:\n\n{context.user_data['pack']}\n🆔 {context.user_data['id']}\n\n💰 السعر: {price}$\n💳 رصيدك: {bal}$"
    )

    keyboard = [
        [InlineKeyboardButton("✅ تأكيد", callback_data="buy")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
    ]

    await update.message.reply_text("هل تريد تأكيد الشراء؟", reply_markup=InlineKeyboardMarkup(keyboard))

# ===== BUY =====
async def buy(update, context):
    global order_id
    query = update.callback_query
    await query.answer()

    uid = str(query.from_user.id)
    price = context.user_data["price"]

    if balances.get(uid, 0) < price:
        await query.message.reply_text("❌ رصيدك غير كافي")
        return

    balances[uid] -= price

    oid = str(order_id)
    order_id += 1

    orders[oid] = {
        "user": uid,
        "pack": context.user_data["pack"],
        "id": context.user_data["id"]
    }

    save()

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 طلب جديد #{oid}\n{orders[oid]}"
    )

    await query.message.reply_text("✅ تم تنفيذ الطلب")
    context.user_data.clear()

# ===== CANCEL =====
async def cancel(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.message.reply_text("❌ تم الإلغاء")

# ===== DEPOSIT =====
async def deposit(update, context):
    keyboard = [
        ["💳 شام كاش", "📱 سيرياتيل كاش"],
        ["🔙 رجوع"]
    ]
    await update.message.reply_text("اختر طريقة الدفع:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== SHAM =====
async def sham(update, context):
    await update.message.reply_text("📋 رقم شام كاش:\n123456789")

# ===== SYRIATEL =====
async def syriatel(update, context):
    await update.message.reply_text("📋 رقم سيرياتيل:\n0987654321")

# ===== PHOTO =====
async def photo(update, context):
    uid = str(update.message.from_user.id)

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"📥 إيصال من {uid}"
    )

    await update.message.reply_text("⏳ تم إرسال طلبك، انتظر الموافقة")

# ===== ACCOUNT =====
async def account(update, context):
    uid = str(update.message.from_user.id)
    bal = balances.get(uid, 0)

    await update.message.reply_text(f"👤 حسابك\n💰 {bal}$")

# ===== HANDLE =====
async def handle(update, context):
    text = update.message.text

    if text == "🛍 المنتجات":
        await products(update, context)

    elif text == "🎮 PUBG MOBILE":
        await pubg_menu(update, context)

    elif text in pubg:
        await select_pack(update, context)

    elif "pack" in context.user_data and "id" not in context.user_data:
        await get_id(update, context)

    elif text == "💰 إيداع":
        await deposit(update, context)

    elif text == "💳 شام كاش":
        await sham(update, context)

    elif text == "📱 سيرياتيل كاش":
        await syriatel(update, context)

    elif text == "👤 حسابي":
        await account(update, context)

    elif text == "🔙 رجوع":
        await start(update, context)

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(MessageHandler(filters.PHOTO, photo))

app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
app.add_handler(CallbackQueryHandler(cancel, pattern="cancel"))

print("🔥 BOT READY")
app.run_polling()
