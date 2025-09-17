from telegram.ext import Application, CommandHandler
import os

TOKEN = os.getenv('BOT_TOKEN')

async def start(update, context):
    await update.message.reply_text('Бот запущен!')

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Бот инициализирован успешно!")
print("Токен получен:", bool(TOKEN))
