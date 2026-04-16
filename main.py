import json
from datetime import datetime
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726
SUPPORT = "@Star_IDOO796256363"

# ===== DATA =====
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {
        "balances": {},
        "orders": {},
        "users": {},
        "counter": 1
    }

balances = data["balances"]
orders = data["orders"]
users = data["users"]
order_id = data["counter"]

def save():
    with open("data.json", "w") as f:
        json.dump({
            "balances": balances,
            "orders": orders,
            "users": users,
            "counter": order_id
        }, f)

# ===== المنتجات =====
products = {
    "PUBG MOBILE": {
        "60 UC": 0.9,
        "325 UC": 4.5,
    }
}

# ===== START =====
async def start(update, context):
    uid = str(update.message.from_user.id)

    if uid not in users:
        users[uid] = {
            "spent": 0,
            "orders": 0,
            "join": str(datetime.now())
        }
        save()

    keyboard = ReplyKeyboardMarkup([
        ["🛍 المنتجات"],
        ["💰 إيداع رصيد", "📦 طلباتي"],
        ["👤 حسابي", "💬 الدعم الفني"]
    ], resize_keyboard=True)

    await update.message.reply_text("⚡ مرحبا بك في متجر الشيخ", reply_markup=keyboard)

# ===== TEXT =====
async def text(update, context):
    global order_id
    msg = update.message.text
    uid = str(update.message.from_user.id)

    # ===== المنتجات =====
    if msg == "🛍 المنتجات":
        keyboard = [[InlineKeyboardButton(p, callback_data=f"game_{p}")] for p in products]
        await update.message.reply_text("🎮 اختر اللعبة:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== حسابي =====
    elif msg == "👤 حسابي":
        user = update.message.from_user
        bal = balances.get(uid, 0)
        spent = users[uid]["spent"]
        orders_count = users[uid]["orders"]

        text = f"""👤 معلومات حسابي

🆔 معرف التيليجرام: {uid}
📝 المعرف: @{user.username if user.username else "لا يوجد"}
👨 الاسم: {user.full_name}

💰 الرصيد الحالي: ${round(bal,2)}
💸 إجمالي المصروف: ${round(spent,2)}
📦 إجمالي الطلبات: {orders_count}

🥇 المستوى الحالي: ذهبي
🎁 الخصم: 4%

📅 تاريخ الانضمام:
{users[uid]["join"]}
"""
        await update.message.reply_text(text)

    # ===== طلباتي =====
    elif msg == "📦 طلباتي":
        user_orders = [o for o in orders.values() if o["user"] == uid]
        if not user_orders:
            await update.message.reply_text("❌ لا يوجد طلبات")
        else:
            text = "📦 طلباتك:\n\n"
            for o in user_orders[-5:]:
                text += f"{o['game']} - {o['pack']}\n"
            await update.message.reply_text(text)

    # ===== الدعم =====
    elif msg == "💬 الدعم الفني":
        await update.message.reply_text(f"📞 تواصل مباشر:\n{SUPPORT}")

    # ===== إيداع =====
    elif msg == "💰 إيداع رصيد":
        keyboard = ReplyKeyboardMarkup([
            ["💳 شام كاش", "📱 سيرياتيل كاش"],
            ["🔙 رجوع"]
        ], resize_keyboard=True)

        await update.message.reply_text("اختر طريقة الدفع:", reply_markup=keyboard)

    elif msg == "💳 شام كاش":
        context.user_data["deposit"] = "sham"
        await update.message.reply_text(
            "💳 رقم شام كاش:\n`417504d810333979a7affca09578fa75`\n\n✍️ اكتب المبلغ الذي تريد شحنه:",
            parse_mode="Markdown"
        )

    elif msg == "📱 سيرياتيل كاش":
        context.user_data["deposit"] = "syriatel"
        await update.message.reply_text(
            "📱 رقم سيرياتيل:\n`00820198`\n\n✍️ اكتب المبلغ الذي تريد شحنه:",
            parse_mode="Markdown"
        )

    # ===== إدخال مبلغ =====
    elif "deposit" in context.user_data and "amount" not in context.user_data:
        if not msg.isdigit():
            await update.message.reply_text("❌ اكتب رقم فقط")
            return

        context.user_data["amount"] = int(msg)
        await update.message.reply_text("📸 أرسل صورة الإيصال")

    # ===== ID =====
    elif "pack" in context.user_data and "id" not in context.user_data:
        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        keyboard = [
            [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ]

        await update.message.reply_text(
            f"📦 تأكيد الطلب:\n\n🎮 {game}\n💎 {pack}\n🆔 {msg}\n💰 السعر: {price}$",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ===== الصور (الإيداع) =====
async def photo(update, context):
    if "deposit" not in context.user_data:
        return

    uid = str(update.message.from_user.id)
    amount = context.user_data["amount"]

    keyboard = [[
        InlineKeyboardButton("✅ قبول", callback_data=f"ok_{uid}_{amount}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}")
    ]]

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"📥 طلب شحن\n👤 {uid}\n💰 {amount}$",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ تم إرسال الطلب للإدارة")
    context.user_data.clear()

# ===== CALLBACK =====
async def button(update, context):
    global order_id
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = str(query.from_user.id)

    # ===== اختيار لعبة =====
    if data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game

        keyboard = [[InlineKeyboardButton(p, callback_data=f"pack_{p}")]
                    for p in products[game]]

        await query.edit_message_text("اختر الباقة:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("pack_"):
        context.user_data["pack"] = data.replace("pack_", "")
        await query.edit_message_text("📩 أرسل ID الحساب")

    # ===== تأكيد شراء =====
    elif data == "confirm":
        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        if balances.get(uid, 0) < price:
            await query.edit_message_text("❌ رصيدك غير كافي")
            return

        balances[uid] -= price
        users[uid]["spent"] += price
        users[uid]["orders"] += 1

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

👤 المستخدم: {uid}
🎮 اللعبة: {game}
💎 الباقة: {pack}
🆔 ID: {context.user_data['id']}
💰 السعر: {price}$"""
        )

        await query.edit_message_text("✅ تم إرسال الطلب")
        context.user_data.clear()

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ تم الإلغاء")

    # ===== قبول الشحن =====
    elif data.startswith("ok_"):
        _, user_id, amount = data.split("_")
        balances[user_id] = balances.get(user_id, 0) + int(amount)
        save()

        await context.bot.send_message(user_id, f"✅ تم شحن {amount}$")
        await query.edit_message_caption("✅ تم القبول")

    elif data.startswith("no_"):
        user_id = data.split("_")[1]
        await context.bot.send_message(user_id, "❌ تم رفض الطلب")
        await query.edit_message_caption("❌ تم الرفض")

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))

print("🔥 BOT WORKING")
app.run_polling()
