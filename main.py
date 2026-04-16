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

pubg_packs = [
    "💎 60 UC",
    "💎 325 UC",
    "💎 660 UC",
    "💎 1800 UC",
    "💎 3850 UC",
    "💎 8100 UC"
]

prices = {
    "💎 60 UC": 1,
    "💎 325 UC": 5,
    "💎 660 UC": 10,
    "💎 1800 UC": 25,
    "💎 3850 UC": 50,
    "💎 8100 UC": 100
}

# ===== START =====
async def start(update, context):
    keyboard = [
        ["🛍 المنتجات"],
        ["💰 إيداع", "📦 طلباتي"],
        ["👤 حسابي", "💬 الدعم"]
    ]
    await update.message.reply_text("🔥 متجر VIP LEVEL 11", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== حسابي (احترافي) =====
async def account(update, context):
    user = update.message.from_user
    uid = str(user.id)

    bal = balances.get(uid, 0)
    total = len([o for o in orders.values() if o["user"] == uid])

    await update.message.reply_text(
f"""👤 معلومات حسابي

🆔 ID: {uid}
👤 @{user.username if user.username else 'لا يوجد'}

💰 الرصيد الحالي: {bal}$
📦 الطلبات: {total}

🏆 المستوى: ذهبي
🎁 الخصم: 4%"""
    )

# ===== المنتجات =====
async def products(update, context):
    keyboard = [
        ["🎮 الألعاب", "📱 التطبيقات"],
        ["📡 سيرياتيل", "📶 MTN"],
        ["🔙 رجوع"]
    ]
    await update.message.reply_text("🛍 اختر القسم:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== الألعاب =====
async def games_menu(update, context):
    keyboard = [[g] for g in games] + [["🔙 رجوع"]]
    await update.message.reply_text("🎮 اختر لعبة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== التطبيقات =====
async def apps_menu(update, context):
    keyboard = [[a] for a in apps] + [["🔙 رجوع"]]
    await update.message.reply_text("📱 اختر تطبيق:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== اختيار لعبة =====
async def select_item(update, context):
    item = update.message.text
    context.user_data["item"] = item

    if item == "PUBG MOBILE":
        keyboard = [
            ["💎 60 UC", "💎 325 UC"],
            ["💎 660 UC", "💎 1800 UC"],
            ["💎 3850 UC", "💎 8100 UC"],
            ["🔙 رجوع"]
        ]
        await update.message.reply_text("اختر الشدة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    else:
        keyboard = [["💰 10", "💰 25"], ["🔙 رجوع"]]
        await update.message.reply_text("اختر الباقة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== اختيار باقة =====
async def select_pack(update, context):
    context.user_data["pack"] = update.message.text
    await update.message.reply_text("📩 أرسل ID الحساب")

# ===== تأكيد =====
async def confirm(update, context):
    context.user_data["id"] = update.message.text

    await update.message.reply_text(
f"""📦 تأكيد الطلب:

🎮 {context.user_data['item']}
{context.user_data['pack']}
🆔 {context.user_data['id']}

✍️ اكتب (تأكيد)"""
    )

# ===== إرسال الطلب =====
async def send_order(update, context):
    global order_id

    uid = str(update.message.from_user.id)
    pack = context.user_data["pack"]

    price = prices.get(pack, 5)

    if balances.get(uid, 0) < price:
        await update.message.reply_text("❌ رصيدك غير كافي")
        return

    balances[uid] -= price

    oid = str(order_id)
    order_id += 1

    orders[oid] = {
        "user": uid,
        "item": context.user_data["item"],
        "pack": pack,
        "id": context.user_data["id"]
    }

    save()

    keyboard = [[InlineKeyboardButton("✅ تم التنفيذ", callback_data=f"done_{oid}")]]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 طلب #{oid}\n{orders[oid]}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(f"✅ تم إرسال طلبك #{oid}")
    context.user_data.clear()

# ===== تنفيذ =====
async def done(update, context):
    query = update.callback_query
    await query.answer()

    oid = query.data.split("_")[1]

    await context.bot.send_message(
        chat_id=int(orders[oid]["user"]),
        text=f"🎉 تم تنفيذ طلبك #{oid}"
    )

    await query.edit_message_text(f"✅ تم تنفيذ #{oid}")

# ===== إيداع =====
async def deposit(update, context):
    keyboard = [
        ["💳 شام كاش", "📱 سيرياتيل كاش"],
        ["🔙 رجوع"]
    ]
    await update.message.reply_text("💰 اختر طريقة الإيداع:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== شام =====
async def sham(update, context):
    await update.message.reply_text("📌 العنوان:")
    await update.message.reply_text("f30ccc46c72d2d3850e23de000c3b2156")
    await update.message.reply_text("📩 أرسل صورة أو رقم العملية")

# ===== سيرياتيل =====
async def syriatel(update, context):
    await update.message.reply_text("📌 الرقم:")
    await update.message.reply_text("09XXXXXXXX")
    await update.message.reply_text("📩 أرسل صورة أو رقم العملية")

# ===== صورة =====
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
        caption=f"💰 طلب إيداع\n👤 {uid}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ جاري المراجعة...")

# ===== أزرار الأدمن =====
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

    elif "UC" in text or "💰" in text:
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

print("🔥 BOT RUNNING LEVEL 11")
app.run_polling()
