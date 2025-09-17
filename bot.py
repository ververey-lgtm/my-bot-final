from telegram.ext import Application, CommandHandler
import os

TOKEN = os.getenv('BOT_TOKEN')

async def start(update, context):
    await update.message.reply_text('Бот запущен и работает! ✅')

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Бот инициализирован успешно!")
print("Токен получен:", bool(TOKEN))

# Для Render с вебхуком
if __name__ == '__main__':
    print("Бот запускается в режиме вебхука...")
    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=TOKEN,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )
