from telegram.ext import Application, CommandHandler
import os

TOKEN = os.getenv('BOT_TOKEN')

async def start(update, context):
    await update.message.reply_text('Бот запущен и работает! ✅')

# Инициализация приложения
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Бот инициализирован успешно!")
print("Токен получен:", bool(TOKEN))

# Простой запуск поллинга (самый надежный способ)
if __name__ == '__main__':
    print("Бот запускается...")
    app.run_polling()
    print("Бот работает и ждет сообщения...")
