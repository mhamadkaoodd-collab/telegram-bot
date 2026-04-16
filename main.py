import json
from telegram import *
from telegram.ext import *

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726
SUPPORT = "t.me/USERNAME"  # حط يوزرك

SHAM = "417504d810333979a7affca09578fa75"
SYRIATEL = "00820198"

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

# ===== المنتجات =====
products = {
    "PUBG": {"60 UC": 0.9},
    "FREE FIRE": {"100💎": 1}
}

# ===== القائمة الرئيسية (تحت) =====
def main_menu():
    return ReplyKeyboardMarkup([
        ["🛍 المنتجات"],
        ["💰 إيداع رصيد", "👤 حسابي"],
        ["📦 طلباتي", "📞 الدعم الفني"]
    ], resize_keyboard=True)

# ===== START =====
async def start(update, context):
    await update.message.reply_text(
        "⚡ أهلا بك في متجر الشيخ\nاختر من الأزرار بالأسفل 👇",
        reply_markup=main_menu()
    )

# ===== TEXT =====
async def text(update, context):
    global order_id
    uid = str(update.message.from_user.id)
    msg = update.message.text

    # ===== المنتجات =====
    if msg == "🛍 المنتجات":
        keyboard = [[InlineKeyboardButton(g, callback_data=f"game_{g}")] for g in products]
        await update.message.reply_text("🎮 اختر اللعبة:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== حساب =====
    elif msg == "👤 حسابي":
        bal = balances.get(uid, 0)
        await update.message.reply_text(f"💰 رصيدك: {bal}$")

    # ===== إيداع =====
    elif msg == "💰 إيداع رصيد":
        keyboard = [
            [InlineKeyboardButton("💳 شام كاش", callback_data="sham")],
            [InlineKeyboardButton("📱 سيرياتيل كاش", callback_data="syriatel")]
        ]
        await update.message.reply_text("اختر طريقة الدفع:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== الدعم =====
    elif msg == "📞 الدعم الفني":
        await update.message.reply_text(f"📩 تواصل معي مباشرة:\n{SUPPORT}")

    # ===== ID =====
    elif "pack" in context.user_data and "id" not in context.user_data:
        context.user_data["id"] = msg

        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]
        bal = balances.get(uid, 0)

        keyboard = [
            [InlineKeyboardButton("✅ تأكيد", callback_data="confirm")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]
        ]

        await update.message.reply_text(
            f"""📦 تأكيد الطلب:

🎮 {game}
💎 {pack}
🆔 {msg}

💰 السعر: {price}$
💳 رصيدك: {bal}$""",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== إدخال مبلغ للأدمن =====
    elif "add_balance" in context.user_data:
        try:
            amount = float(msg)
            target = context.user_data["add_balance"]

            balances[target] = balances.get(target, 0) + amount
            save()

            await context.bot.send_message(target, f"✅ تم شحن {amount}$")
            await update.message.reply_text("✔️ تم الشحن")
            context.user_data.clear()
        except:
            await update.message.reply_text("❌ اكتب رقم فقط")

# ===== CALLBACK =====
async def button(update, context):
    global order_id
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = str(q.from_user.id)

    # ===== لعبة =====
    if data.startswith("game_"):
        game = data.split("_")[1]
        context.user_data["game"] = game

        keyboard = [[InlineKeyboardButton(p, callback_data=f"pack_{p}")]
                    for p in products[game]]

        await q.edit_message_text("💎 اختر الباقة:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ===== باقة =====
    elif data.startswith("pack_"):
        pack = data.replace("pack_", "")
        context.user_data["pack"] = pack
        await q.edit_message_text("📩 أرسل ID الحساب")

    # ===== تأكيد =====
    elif data == "confirm":
        game = context.user_data["game"]
        pack = context.user_data["pack"]
        price = products[game][pack]

        if balances.get(uid, 0) < price:
            await q.edit_message_text("❌ رصيدك غير كافي")
            return

        balances[uid] -= price

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
            f"""📥 طلب جديد #{oid}

👤 المستخدم: {uid}
🎮 {game}
💎 {pack}
🆔 {context.user_data["id"]}"""
        )

        await q.edit_message_text(f"✅ تم الطلب #{oid}")
        context.user_data.clear()

    elif data == "cancel":
        context.user_data.clear()
        await q.edit_message_text("❌ تم الإلغاء")

    # ===== شام كاش =====
    elif data == "sham":
        context.user_data["deposit"] = True
        await q.edit_message_text(
            f"""💳 شام كاش

انسخ الرقم 👇
`{SHAM}`

📸 أرسل صورة التحويل""",
            parse_mode="Markdown"
        )

    # ===== سيرياتيل =====
    elif data == "syriatel":
        context.user_data["deposit"] = True
        await q.edit_message_text(
            f"""📱 سيرياتيل كاش

انسخ الرقم 👇
`{SYRIATEL}`

📸 أرسل صورة التحويل""",
            parse_mode="Markdown"
        )

    # ===== قبول =====
    elif data.startswith("ok_"):
        user_id = data.split("_")[1]
        context.user_data["add_balance"] = user_id
        await q.message.reply_text("💰 اكتب المبلغ لإضافته")

    # ===== رفض =====
    elif data.startswith("no_"):
        user_id = data.split("_")[1]
        await context.bot.send_message(user_id, "❌ تم رفض الإيداع")

# ===== صورة =====
async def photo(update, context):
    if "deposit" not in context.user_data:
        return

    uid = str(update.message.from_user.id)

    keyboard = [[
        InlineKeyboardButton("✅ قبول", callback_data=f"ok_{uid}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}")
    ]]

    await context.bot.send_photo(
        ADMIN_ID,
        update.message.photo[-1].file_id,
        caption=f"📥 إثبات دفع من:\n{uid}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ تم إرسال الإثبات، انتظر الموافقة")
    context.user_data.clear()

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT, text))
app.add_handler(MessageHandler(filters.PHOTO, photo))

print("🔥 BOT WORKING")
app.run_polling()
