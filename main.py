import json
from datetime import datetime
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
    data = {"balances": {}, "orders": {}, "users": {}, "counter": 1}

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
    "PUBG": {
        "60 UC": 0.9,
        "325 UC": 4.5
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
    user = update.message.from_user
    uid = str(user.id)

    if uid not in users:
        users[uid] = {
            "name": user.full_name,
            "username": user.username,
            "join": str(datetime.now()),
            "spent": 0,
            "orders": 0
        }
        save()

    await update.message.reply_text(
        "⚡ مرحباً بك في متجر الشيخ\nاختر من الأزرار 👇",
        reply_markup=main_menu()
    )

# ===== التعامل مع النص =====
async def text(update, context):
    global order_id

    msg = update.message.text
    user = update.message.from_user
    uid = str(user.id)

    # ===== رجوع =====
    if msg == "🔙 رجوع":
        context.user_data.clear()
        await update.message.reply_text("🔙 رجعت", reply_markup=main_menu())
        return

    # ===== منتجات =====
    if msg == "🛍 المنتجات":
        keyboard = ReplyKeyboardMarkup(
            [["PUBG"], ["🔙 رجوع"]],
            resize_keyboard=True
        )
        await update.message.reply_text("🎮 اختر لعبة:", reply_markup=keyboard)
        return

    if msg == "PUBG":
        context.user_data["game"] = "PUBG"
        keyboard = ReplyKeyboardMarkup(
            [["60 UC", "325 UC"], ["🔙 رجوع"]],
            resize_keyboard=True
        )
        await update.message.reply_text("💎 اختر الباقة:", reply_markup=keyboard)
        return

    if msg in ["60 UC", "325 UC"]:
        context.user_data["pack"] = msg
        await update.message.reply_text("📩 أرسل ID الحساب:")
        return

    # ===== استقبال ID =====
    if "pack" in context.user_data and "id" not in context.user_data:
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
        return

    # ===== إيداع =====
    if msg == "💰 إيداع رصيد":
        keyboard = ReplyKeyboardMarkup(
            [["💳 شام كاش", "📱 سيريتيل كاش"], ["🔙 رجوع"]],
            resize_keyboard=True
        )
        await update.message.reply_text("اختر طريقة الدفع:", reply_markup=keyboard)
        return

    if msg == "💳 شام كاش":
        context.user_data["deposit"] = True
        await update.message.reply_text(
            "💳 رقم شام كاش:\n`417504d810333979a7affca09578fa75`\n\nاكتب المبلغ الذي تريد شحنه:",
            parse_mode="Markdown"
        )
        return

    if msg == "📱 سيريتيل كاش":
        context.user_data["deposit"] = True
        await update.message.reply_text(
            "📱 رقم سيريتيل:\n`00820198`\n\nاكتب المبلغ الذي تريد شحنه:",
            parse_mode="Markdown"
        )
        return

    # ===== إدخال مبلغ =====
    if "deposit" in context.user_data and "amount" not in context.user_data:
        if not msg.isdigit():
            await update.message.reply_text("❌ اكتب رقم فقط")
            return

        context.user_data["amount"] = msg
        await update.message.reply_text("📸 أرسل صورة الإيصال")
        return

    # ===== حسابي =====
    if msg == "👤 حسابي":
        user_data = users.get(uid, {})
        bal = balances.get(uid, 0)

        text_msg = f"""👤 معلومات حسابي

🆔 {uid}
📝 @{user_data.get("username")}
👨 {user_data.get("name")}

💰 الرصيد: ${round(bal,2)}
💸 المصروف: ${user_data.get("spent",0)}
📦 الطلبات: {user_data.get("orders",0)}

📅 {user_data.get("join")}"""

        await update.message.reply_text(text_msg)
        return

    # ===== طلباتي =====
    if msg == "📦 طلباتي":
        my_orders = [o for o in orders.values() if o["user"] == uid]

        if not my_orders:
            await update.message.reply_text("❌ لا يوجد طلبات")
            return

        text_orders = ""
        for o in my_orders[-5:]:
            text_orders += f"{o['game']} - {o['pack']} - ID:{o['id']}\n"

        await update.message.reply_text(text_orders)
        return

    # ===== دعم =====
    if msg == "📞 الدعم الفني":
        await update.message.reply_text(f"📞 تواصل: {SUPPORT}")
        return

# ===== الأزرار =====
async def button(update, context):
    global order_id

    query = update.callback_query
    await query.answer()
    data = query.data
    uid = str(query.from_user.id)

    # ===== تأكيد الطلب =====
    if data == "confirm":
        game = context.user_data["game"]
        pack = context.user_data["pack"]
        pid = context.user_data["id"]
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
            "id": pid
        }

        save()

        await context.bot.send_message(
            ADMIN_ID,
            f"""📥 طلب جديد #{oid}

👤 {uid}
🎮 {game}
💎 {pack}
🆔 {pid}
💰 {price}$"""
        )

        await query.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ تم الإلغاء")

    # ===== قبول الشحن =====
    elif data.startswith("ok_"):
        _, target, amount = data.split("_")
        amount = float(amount)

        balances[target] = balances.get(target, 0) + amount
        save()

        await context.bot.send_message(target, f"✅ تم شحن {amount}$")
        await query.edit_message_caption("✅ تم القبول")

    elif data.startswith("no_"):
        target = data.split("_")[1]
        await context.bot.send_message(target, "❌ تم الرفض")
        await query.edit_message_caption("❌ تم الرفض")

# ===== صورة الإيصال =====
async def photo(update, context):
    if "deposit" not in context.user_data:
        return

    uid = str(update.message.from_user.id)
    amount = context.user_data.get("amount")

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

    await update.message.reply_text("⏳ بانتظار الموافقة")
    context.user_data.clear()

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))

print("🔥 BOT RUNNING")
app.run_polling()
