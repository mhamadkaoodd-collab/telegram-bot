elif text == "🛍️ المتجر":
    products = get_products()
    await update.message.reply_text(f"DATA:\n{products}")
