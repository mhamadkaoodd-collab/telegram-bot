import json
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726
SUPPORT = "@Star_IDOO796256363"

# ===== تحميل البيانات =====
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {"balances": {}, "orders": {}, "counter": 1, "spent": {}, "joined": {}}

balances = data["balances"]
orders = data["orders"]
order_id = data["counter"]
spent = data.get("spent", {})
joined = data.get("joined", {})

def save():
    with open("data.json", "w") as f:
        json.dump({
            "balances": balances,
            "orders": orders,
            "counter": order_id,
            "spent": spent,
            "joined": joined
        }, f)

# ===== المنتجات =====
products = {
    "PUBG": {
        "60 UC": 0.9,
        "325 UC": 4.5,
    }
}

# ===== القائمة الرئيسية =====
def main_menu():
    return ReplyKeyboardMarkup([
        ["🛍 المنتجات"],
        ["💰 إيداع رصيد", "📦 طلباتي"],
        ["👤 حسابي", "📞 الدعم الفني"]
    ], resize_keyboard=True)

# ===== START =====
async def start(update, context):
    uid = str(update.message.from_user.id)

    if uid not in joined:
        import datetime
        joined[uid] = str(datetime.datetime.now())

    await update.message.reply_text(
        "⚡ مرحبا بك في متجر الشيخ",
        reply_markup=main_menu()
    )

# ===== الرسائل =====
async def text(update, context):
    global order_id

    msg = update.message.text
    uid = str(update.message.from_user.id)

    # ===== رجوع =====
    if msg == "رجوع":
        context.user_data.clear()
        await update.message.reply_text("🔙 رجعت", reply_markup=main_menu())
        return

    # ===== منتجات =====
    if msg == "🛍 المنتجات":
        keyboard = ReplyKeyboardMarkup([
            ["PUBG"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر اللعبة:", reply_markup=keyboard)

    elif msg == "PUBG":
        context.user_data["game"] = "PUBG"
        keyboard = ReplyKeyboardMarkup([
            ["60 UC", "325 UC"],
            ["رجوع"]
        ], resize_keyboard=True)
        await update.message.reply_text("اختر الشدة:", reply_markup=keyboard)

    elif msg in ["60 UC", "325 UC"]:
        context.user_data["pack"] = msg
        await update.message.reply_text("📩 أرسل ID الحساب")

    # ===== استلام ID =====
    elif "pack" in context.user_data and "id" not in context.user_data:
        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]
        bal = balances.get(uid, 0)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ])

        await update.message.reply_text(
            f"""📦 تأكيد الطلب

🎮 {game}
💎 {pack}
🆔 {msg}

💰 السعر: {price}$
💳 رصيدك: {bal}$""",
            reply_markup=keyboard
        )

    # ===== إيداع =====
    elif msg == "💰 إيداع رصيد":
        keyboard = ReplyKeyboardMarkup([
            ["💳 شام كاش", "📱 سيرياتيل كاش"],
            ["رجوع"]
        ], resize_keyboard=True)

        await update.message.reply_text("اختر طريقة الدفع:", reply_markup=keyboard)

    elif msg == "💳 شام كاش":
        context.user_data["deposit"] = "sham"
        await update.message.reply_text(
            "💳 رقم شام كاش:\n`417504d810333979a7affca09578fa75`\n\n✍️ اكتب المبلغ",
            parse_mode="Markdown"
        )

    elif msg == "📱 سيرياتيل كاش":
        context.user_data["deposit"] = "syriatel"
        await update.message.reply_text(
            "📱 رقم سيرياتيل:\n`00820198`\n\n✍️ اكتب المبلغ",
            parse_mode="Markdown"
        )

    # ===== إدخال مبلغ الإيداع =====
    elif "deposit" in context.user_data and "amount" not in context.user_data:
        try:
            amount = float(msg)
            context.user_data["amount"] = amount
            await update.message.reply_text("📸 أرسل صورة الإيصال")
        except:
            await update.message.reply_text("❌ اكتب رقم فقط")

    # ===== طلباتي =====
    elif msg == "📦 طلباتي":
        user_orders = [f"#{k} - {v['pack']}" for k, v in orders.items() if v["user"] == uid]
        if not user_orders:
            await update.message.reply_text("❌ لا يوجد طلبات")
        else:
            await update.message.reply_text("\n".join(user_orders))

    # ===== حسابي =====
    elif msg == "👤 حسابي":
        bal = balances.get(uid, 0)
        sp = spent.get(uid, 0)
        total_orders = len([o for o in orders.values() if o["user"] == uid])

        await update.message.reply_text(
            f"""👤 معلومات حسابي

🆔 {uid}
💰 الرصيد: {bal}$
💸 المصروف: {sp}$
📦 الطلبات: {total_orders}
📅 الانضمام: {joined.get(uid, "غير معروف")}"""
        )

    # ===== دعم =====
    elif msg == "📞 الدعم الفني":
        await update.message.reply_text(f"راسل الدعم: {SUPPORT}")

# ===== الصور =====
async def photo(update, context):
    if "deposit" not in context.user_data:
        return

    uid = str(update.message.from_user.id)
    amount = context.user_data["amount"]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ قبول", callback_data=f"ok_{uid}_{amount}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}")
        ]
    ])

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"📥 طلب شحن\n👤 {uid}\n💰 {amount}$",
        reply_markup=keyboard
    )

    await update.message.reply_text("⏳ تم إرسال طلبك")
    context.user_data.clear()

# ===== الأزرار =====
async def button(update, context):
    global order_id

    query = update.callback_query
    await query.answer()
    data = query.data

    # ===== تأكيد شراء =====
    if data == "confirm":
        uid = str(query.from_user.id)

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        if balances.get(uid, 0) < price:
            await query.edit_message_text("❌ رصيدك غير كافي")
            return

        balances[uid] -= price
        spent[uid] = spent.get(uid, 0) + price

        oid = str(order_id)
        order_id += 1

        orders[oid] = {
            "user": uid,
            "game": game,
            "pack": pack,
            "id": context.user_data["id"]
        }

        save()

        await context.bot.send_message(
            ADMIN_ID,
            f"""📦 طلب جديد #{oid}

👤 {uid}
🎮 {game}
💎 {pack}
🆔 {context.user_data["id"]}
💰 {price}$"""
        )

        await query.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ تم الإلغاء")

    # ===== قبول شحن =====
    elif data.startswith("ok_"):
        _, uid, amount = data.split("_")
        amount = float(amount)

        balances[uid] = balances.get(uid, 0) + amount
        save()

        await context.bot.send_message(uid, f"✅ تم شحن {amount}$")
        await query.edit_message_caption("✅ تم القبول")

    elif data.startswith("no_"):
        uid = data.split("_")[1]
        await context.bot.send_message(uid, "❌ تم رفض الطلب")
        await query.edit_message_caption("❌ تم الرفض")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))

print("🔥 BOT WORKING")
app.run_polling()
