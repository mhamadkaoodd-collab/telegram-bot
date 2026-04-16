import json
import random
import string
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8260446715:AAE53tOR8UQ9vdrLDcBXptg8Y-tys61rNg8"
ADMIN_ID = 8015961726

# ===== تخزين =====
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {"balances": {}, "orders": {}, "codes": {}, "counter": 1}

balances = data.get("balances", {})
orders = data.get("orders", {})
codes = data.get("codes", {})
order_id = data.get("counter", 1)

def save():
    with open("data.json", "w") as f:
        json.dump({
            "balances": balances,
            "orders": orders,
            "codes": codes,
            "counter": order_id
        }, f)

# ===== حالات =====
user_state = {}

# ===== مستويات =====
def get_level(count):
    if count >= 20:
        return "💎 ماسي", 6
    elif count >= 10:
        return "🥇 ذهبي", 4
    elif count >= 5:
        return "🥈 فضي", 2
    else:
        return "🥉 برونزي", 0

# ===== ألعاب =====
games = ["PUBG MOBILE","FREE FIRE","CLASH OF CLANS","BRAWL STARS"]

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[str(update.message.from_user.id)] = "idle"

    keyboard = [
        ["🛍 المنتجات"],
        ["💰 رصيدي", "📦 طلباتي"],
        ["📥 إيداع", "👤 حسابي"],
        ["💬 الدعم"]
    ]

    await update.message.reply_text(
        "🔥 متجر VIP",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ===== HANDLE =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global order_id

    user = str(update.message.from_user.id)
    text = update.message.text

    if user not in balances:
        balances[user] = 0

    state = user_state.get(user, "idle")

    # ===== المنتجات =====
    if text == "🛍 المنتجات":
        user_state[user] = "choosing_game"
        keyboard = [[g] for g in games] + [["🔙 رجوع"]]
        await update.message.reply_text("🎮 اختر لعبة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # ===== اختيار لعبة =====
    elif state == "choosing_game" and text in games:
        context.user_data["game"] = text
        user_state[user] = "choosing_pack"

        keyboard = [["💎 60 UC", "💎 325 UC"], ["🔙 رجوع"]]
        await update.message.reply_text("اختر الباقة:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # ===== اختيار باكج =====
    elif state == "choosing_pack":
        context.user_data["pack"] = text
        user_state[user] = "entering_id"
        await update.message.reply_text("📩 أرسل ID الحساب")

    # ===== إدخال ID =====
    elif state == "entering_id":
        context.user_data["player_id"] = text
        user_state[user] = "confirm_order"

        await update.message.reply_text(
            f"📦 تأكيد الطلب:\n\n"
            f"🎮 {context.user_data['game']}\n"
            f"📦 {context.user_data['pack']}\n"
            f"🆔 {text}\n\n"
            f"اكتب (تأكيد) للمتابعة"
        )

    # ===== تأكيد =====
    elif state == "confirm_order" and text == "تأكيد":
        oid = str(order_id)
        order_id += 1

        orders[oid] = {
            "user": user,
            "game": context.user_data["game"],
            "pack": context.user_data["pack"],
            "id": context.user_data["player_id"],
            "status": "pending"
        }

        save()

        user_state[user] = "idle"
        context.user_data.clear()

        keyboard = [[InlineKeyboardButton("✅ تم التنفيذ", callback_data=f"done_{oid}")]]

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📥 طلب جديد #{oid}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await update.message.reply_text("✅ تم إرسال الطلب")

    # ===== إيداع =====
    elif text == "📥 إيداع":
        user_state[user] = "waiting_payment"

        await update.message.reply_text(
            "💳 إيداع\n\n"
            "📌 عنوان المحفظة:\n"
            "`417504d810333979a7affca09578fa75`\n\n"
            "📩 أرسل رقم العملية"
        )

    # ===== رقم العملية =====
    elif state == "waiting_payment":
        user_state[user] = "idle"

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 عملية من {user}\nرقم: {text}"
        )

        await update.message.reply_text("✅ تم إرسال طلب المراجعة")

    # ===== كود هدية =====
    elif text.startswith("redeem "):
        code = text.split(" ")[1]

        if code in codes:
            amount = codes.pop(code)
            balances[user] += amount
            save()
            await update.message.reply_text(f"🎁 تم إضافة {amount}$")
        else:
            await update.message.reply_text("❌ كود غير صالح")

    # ===== حسابي =====
    elif text == "👤 حسابي":
        user_orders = [o for o in orders.values() if o["user"] == user]
        level, discount = get_level(len(user_orders))

        await update.message.reply_text(
            f"👤 حسابك\n\n"
            f"💰 {balances[user]}$\n"
            f"📦 {len(user_orders)} طلب\n"
            f"🏆 {level}\n"
            f"🎁 خصم {discount}%"
        )

    # ===== رجوع =====
    elif text == "🔙 رجوع":
        user_state[user] = "idle"
        await start(update, context)

# ===== تنفيذ =====
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    oid = query.data.split("_")[1]

    if oid in orders:
        orders[oid]["status"] = "completed"
        save()

        await context.bot.send_message(
            chat_id=int(orders[oid]["user"]),
            text=f"🎉 تم تنفيذ طلبك #{oid}"
        )

        await query.edit_message_text("✅ تم التنفيذ")

# ===== توليد كود =====
async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != str(ADMIN_ID):
        return

    amount = int(context.args[0])
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    codes[code] = amount
    save()

    await update.message.reply_text(f"🎁 الكود:\n{code}\n💰 {amount}$")

# ===== تشغيل =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gen", gen))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(CallbackQueryHandler(done))

print("🔥 LEVEL 6 RUNNING")
app.run_polling()
