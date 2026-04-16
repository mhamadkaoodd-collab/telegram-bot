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

# ===== القائمة =====
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

# ===== النص =====
async def text(update, context):
    global order_id

    msg = update.message.text
    uid = str(update.message.from_user.id)

    if msg == "🛍 المنتجات":
        await update.message.reply_text("🎮 اختر لعبة:", reply_markup=ReplyKeyboardMarkup([["PUBG"], ["🔙 رجوع"]], resize_keyboard=True))
        return

    if msg == "PUBG":
        context.user_data["game"] = "PUBG"
        await update.message.reply_text("💎 اختر الباقة:", reply_markup=ReplyKeyboardMarkup([["60 UC", "325 UC"], ["🔙 رجوع"]], resize_keyboard=True))
        return

    if msg in ["60 UC", "325 UC"]:
        context.user_data["pack"] = msg
        await update.message.reply_text("📩 أرسل ID الحساب:")
        return

    if "pack" in context.user_data and "id" not in context.user_data:
        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ])

        await update.message.reply_text(
            f"""📦 تأكيد الطلب

🎮 {game}
💎 {pack}
🆔 {msg}
💰 {price}$""",
            reply_markup=keyboard
        )
        return

    if msg == "👤 حسابي":
        bal = balances.get(uid, 0)
        await update.message.reply_text(f"💰 رصيدك: {bal}$")
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

        oid = str(order_id)
        order_id += 1

        orders[oid] = {
            "user": uid,
            "game": game,
            "pack": pack,
            "id": pid,
            "status": "pending"
        }

        save()

        # أزرار الأدمن
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ تم الشحن", callback_data=f"done_{oid}"),
                InlineKeyboardButton("❌ رفض", callback_data=f"reject_{oid}")
            ]
        ])

        await context.bot.send_message(
            ADMIN_ID,
            f"""📥 طلب جديد #{oid}

👤 {uid}
🎮 {game}
💎 {pack}
🆔 {pid}
💰 {price}$""",
            reply_markup=keyboard
        )

        await query.edit_message_text("⏳ الرجاء الانتظار، يتم شحن الشدات")
        context.user_data.clear()

    # ===== تم الشحن =====
    elif data.startswith("done_"):
        oid = data.split("_")[1]
        order = orders.get(oid)

        if not order:
            return

        order["status"] = "done"
        save()

        await context.bot.send_message(order["user"], "✅ تم شحن شداتك بنجاح")
        await query.edit_message_text(f"✅ تم الشحن #{oid}")

    # ===== رفض =====
    elif data.startswith("reject_"):
        oid = data.split("_")[1]
        order = orders.get(oid)

        if not order:
            return

        order["status"] = "rejected"
        save()

        await context.bot.send_message(order["user"], "❌ تم رفض الطلب")
        await query.edit_message_text(f"❌ تم رفض #{oid}")

    elif data == "cancel":
        context.user_data.clear()
        await query.edit_message_text("❌ تم الإلغاء")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))

print("🔥 BOT RUNNING")
app.run_polling()
