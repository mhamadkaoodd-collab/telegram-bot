async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    balances.setdefault(user_id, 0)

    if text == "💰 شحن الرصيد":
        await update.message.reply_text(
            "💳 طرق الدفع:\n\n"
            "شام كاش:\n417504d810333979a7affca09578fa75\n\n"
            "سيرياتيل:\n00820198"
        )

    elif text == "🛍️ المتجر":
        products = get_products()

        if not products:
            await update.message.reply_text("❌ المتجر فاضي أو API خربان")
            return

        keyboard = []
        products_cache.clear()

        for p in products:
            name = p.get("name", "منتج")
            price = p.get("price", 0)

            button = f"{name} - ${price}"
            products_cache[button] = p
            keyboard.append([button])

        await update.message.reply_text(
            "🛒 اختر منتج:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    elif text in products_cache:
        context.user_data["product"] = products_cache[text]
        await update.message.reply_text("📥 ارسل ID اللاعب")

    elif "product" in context.user_data:
        product = context.user_data["product"]
        player_id = text

        price = int(float(product["price"]) * USD_RATE)

        if balances[user_id] < price:
            await update.message.reply_text("❌ رصيدك ما بكفي")
            return

        balances[user_id] -= price

        res = create_order(product["id"], player_id)

        if not res.get("err"):
            await update.message.reply_text("✅ تم الطلب")
        else:
            balances[user_id] += price
            await update.message.reply_text("❌ فشل الطلب")

        del context.user_data["product"]

    elif text == "📦 طلباتي":
        await update.message.reply_text("📦 قريباً")

    elif text == "👤 حسابي":
        await update.message.reply_text(f"💰 رصيدك: {balances[user_id]}")

    elif text == "📞 الدعم":
        await update.message.reply_text("راسلنا: @your_support")

    else:
        await update.message.reply_text("❗ اختر من القائمة")
