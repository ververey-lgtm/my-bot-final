from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import os

# Ключи API
YOUGILE_API_KEY = os.getenv('YOUGILE_API_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Базовый URL Yougile API
YOUGILE_BASE_URL = "https://ru.yougile.com/api-v2"

class YougileClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get_projects(self):
        """Получить список всех проектов"""
        try:
            response = requests.get(
                f"{YOUGILE_BASE_URL}/projects", 
                headers=self.headers,
                params={'limit': 50}
            )
            print("Статус код проектов:", response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                print("Найдено проектов:", len(data.get('content', [])))
                return data.get('content', [])
            else:
                print(f"Ошибка API: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Ошибка при получении проектов: {e}")
            return []

# Создаем клиент Yougile
yougile_client = YougileClient(YOUGILE_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - показывает список проектов"""
    print("Получение проектов из Yougile...")
    
    projects = yougile_client.get_projects()
    
    if not projects:
        await update.message.reply_text("Проекты не найдены или ошибка доступа к Yougile")
        return
    
    # Создаем кнопки с названиями проектов
    keyboard = [[project['title']] for project in projects]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Сохраняем проекты в контекст
    context.user_data['projects'] = {project['title']: project['id'] for project in projects}
    
    await update.message.reply_text(
        "Выберите проект:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех сообщений"""
    if update.message.text:
        await update.message.reply_text(f"Вы написали: {update.message.text}")

def main():
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Настраиваем вебхук для Render
    url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
    
    print(f"Запуск бота с вебхуком на: {url}")
    print("Токен бота:", bool(BOT_TOKEN))
    print("Yougile ключ:", bool(YOUGILE_API_KEY))
    
    # Запускаем вебхук
    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path=BOT_TOKEN,
        webhook_url=f"{url}/{BOT_TOKEN}",
        secret_token='WEBHOOK_SECRET'
    )

if __name__ == '__main__':
    main()
