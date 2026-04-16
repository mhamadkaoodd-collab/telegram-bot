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

# ===== LISTS =====
games = ["PUBG MOBILE", "FREE FIRE", "CLASH ROYALE"]
apps = ["TikTok", "Google Play"]

# ===== START =====
async def start(update, context):
    keyboard = [
        ["🛍 المنتجات"],
        ["💰 إيداع", "📦 طلباتي"],
        ["👤 حسابي", "💬 الدعم"]
    ]
    await update.message.reply_text(
        "🔥 متجر VIP LEVEL 11",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ===== PRODUCTS =====
async def products(update, context):
    keyboard = [
        ["🎮 الألعاب", "📱 التطبيقات"],
        ["📡 سيرياتيل", "📶 MTN"],
        ["🔙 رجوع"]
    ]
    await update.message.reply_text("🛍 اختر القسم:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== MENUS =====
async def games_menu(update, context):
    keyboard = [[g] for g in games] + [["🔙 رجوع"]]
    await update.message.reply_text("🎮 اختر لعبة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def apps_menu(update, context):
    keyboard = [[a] for a in apps] + [["🔙 رجوع"]]
    await update.message.reply_text("📱 اختر تطبيق:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== SELECT =====
async def select_item(update, context):
    context.user_data["item"] = update.message.text
    keyboard = [["💰 10", "💰 25"], ["🔙 رجوع"]]
    await update.message.reply_text("اختر الباقة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def select_pack(update, context):
    context.user_data["pack"] = update.message.text
    await update.message.reply_text("📩 أرسل ID الحساب")

async def confirm(update, context):
    context.user_data["id"] = update.message.text
    await update.message.reply_text(
        f"📦 تأكيد الطلب:\n{context.user_data['item']}\n{context.user_data['pack']}\nID: {context.user_data['id']}\n\nاكتب (تأكيد)"
    )

# ===== SEND ORDER =====
async def send_order(update, context):
    global order_id

    if "item" not in context.user_data:
        return

    uid = str(update.message.from_user.id)

    oid = str(order_id)
    order_id += 1

    orders[oid] = {
        "user": uid,
        "item": context.user_data["item"],
        "pack": context.user_data["pack"],
        "id": context.user_data["id"],
        "status": "pending"
    }

    save()

    keyboard = [[InlineKeyboardButton("✅ تم التنفيذ", callback_data=f"done_{oid}")]]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 طلب جديد #{oid}\n{orders[oid]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(f"✅ تم إرسال طلبك #{oid}")
    context.user_data.clear()

# ===== تنفيذ الطلب =====
async def done(update, context):
    query = update.callback_query
    await query.answer()

    oid = query.data.split("_")[1]

    if oid in orders:
        orders[oid]["status"] = "done"
        save()

        await context.bot.send_message(
            chat_id=int(orders[oid]["user"]),
            text=f"🎉 تم تنفيذ طلبك #{oid}"
        )

        await query.edit_message_text(f"✅ تم تنفيذ الطلب #{oid}")

# ===== DEPOSIT =====
async def deposit(update, context):
    keyboard = [
        ["💳 شام كاش", "📱 سيرياتيل كاش"],
        ["🔙 رجوع"]
    ]
    await update.message.reply_text("💰 اختر طريقة الإيداع:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== شام =====
async def sham(update, context):
    await update.message.reply_text("📋 انسخ العنوان:")
    await update.message.reply_text("417504d810333979a7affca09578fa75")

# ===== سيرياتيل =====
async def syriatel(update, context):
    await update.message.reply_text("📋 انسخ الرقم:")
    await update.message.reply_text("00820198")

# ===== PHOTO =====
async def photo(update, context):
    user = update.message.from_user
    uid = str(user.id)

    keyboard = [[
        InlineKeyboardButton("✅ قبول", callback_data=f"ok_{uid}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}")
    ]]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"📥 إيصال\n👤 {uid}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ جاري المراجعة...")

# ===== قبول =====
async def buttons(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.data.split("_")[1]

    if "ok" in query.data:
        context.user_data["target"] = uid
        await query.message.reply_text("💰 اكتب المبلغ")

    else:
        await context.bot.send_message(chat_id=int(uid), text="❌ تم رفض الإيداع")

# ===== إضافة رصيد =====
async def add_balance(update, context):
    if "target" not in context.user_data:
        return

    uid = context.user_data["target"]

    try:
        amount = int(update.message.text)
        balances[uid] = balances.get(uid, 0) + amount
        save()

        await context.bot.send_message(chat_id=int(uid), text=f"✅ تم شحن {amount}$")
        await update.message.reply_text("✔️ تم")

        context.user_data.clear()

    except:
        await update.message.reply_text("❌ رقم فقط")

# ===== حساب =====
async def account(update, context):
    user = update.message.from_user
    uid = str(user.id)

    bal = balances.get(uid, 0)
    total = len([o for o in orders.values() if o["user"] == uid])

    await update.message.reply_text(
        f"👤 حسابك\n🆔 {uid}\n👤 @{user.username if user.username else 'لا يوجد'}\n💰 {bal}$\n📦 الطلبات: {total}"
    )

# ===== HANDLE =====
async def handle(update, context):
    text = update.message.text

    if text == "🛍 المنتجات":
        await products(update, context)

    elif text == "🎮 الألعاب":
        await games_menu(update, context)

    elif text == "📱 التطبيقات":
        await apps_menu(update, context)

    elif text in games or text in apps:
        await select_item(update, context)

    elif "💰" in text:
        await select_pack(update, context)

    elif text == "تأكيد":
        await send_order(update, context)

    elif "item" in context.user_data and "id" not in context.user_data:
        await confirm(update, context)

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

    else:
        await add_balance(update, context)

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))
app.add_handler(MessageHandler(filters.PHOTO, photo))
app.add_handler(CallbackQueryHandler(done, pattern="done_"))
app.add_handler(CallbackQueryHandler(buttons, pattern="ok_|no_"))

print("🔥 LEVEL 11 RUNNING")
app.run_polling()
