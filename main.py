# 🚀 تشغيل
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_balance))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ Bot started...")

    # تشغيل البوت أولاً
    await app.initialize()
    await app.start()

    # تشغيل الإشعارات بعد ما يشتغل البوت
    asyncio.create_task(check_orders(app))

    # تشغيل الاستقبال
    await app.updater.start_polling()

# تشغيل
if __name__ == "__main__":
    asyncio.run(main())
