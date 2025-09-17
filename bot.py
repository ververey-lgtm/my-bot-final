from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import os
import json

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
        print(f"YougileClient инициализирован с ключом: {api_key[:10]}...")  # Логируем начало ключа
    
    def get_projects(self):
        """Получить список всех проектов"""
        try:
            url = f"{YOUGILE_BASE_URL}/projects"
            print(f"Делаем запрос к: {url}")
            print(f"Заголовки: {self.headers}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            print(f"Статус код: {response.status_code}")
            print(f"Ответ сервера: {response.text[:200]}...")  # Первые 200 символов
            
            if response.status_code == 200:
                data = response.json()
                projects = data.get('content', [])
                print(f"Найдено проектов: {len(projects)}")
                return projects
            else:
                print(f"Ошибка API! Статус: {response.status_code}")
                print(f"Полный ответ: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return []
        except Exception as e:
            print(f"Общая ошибка: {e}")
            return []

# Создаем клиент Yougile
yougile_client = YougileClient(YOUGILE_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text("🔄 Запрашиваю проекты из Yougile...")
    
    projects = yougile_client.get_projects()
    
    if not projects:
        await update.message.reply_text(
            "❌ Не удалось получить проекты.\n\n"
            "Возможные причины:\n"
            "• Неверный API-ключ\n"
            "• Ключ не активирован\n"
            "• Нет доступа к API\n"
            "• Нет созданных проектов в Yougile"
        )
        return
    
    # Создаем кнопки с названиями проектов
    keyboard = [[project['title']] for project in projects]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Сохраняем проекты в контекст
    context.user_data['projects'] = {project['title']: project['id'] for project in projects}
    
    await update.message.reply_text(
        "✅ Проекты получены! Выберите проект:",
        reply_markup=reply_markup
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text(f"Вы выбрали: {update.message.text}")

def main():
    # Проверяем переменные окружения
    print("=" * 50)
    print("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ:")
    print(f"BOT_TOKEN: {'Есть' if BOT_TOKEN else 'Нет'}")
    print(f"YOUGILE_API_KEY: {'Есть' if YOUGILE_API_KEY else 'Нет'}")
    
    if YOUGILE_API_KEY:
        print(f"Длина ключа: {len(YOUGILE_API_KEY)} символов")
        print(f"Начало ключа: {YOUGILE_API_KEY[:10]}...")
    
    print("=" * 50)
    
    # Удаляем вебхук на всякий случай
    try:
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        response = requests.get(delete_url)
        print("Удаление вебхука:", response.json())
    except Exception as e:
        print("Ошибка при удалении вебхука:", e)
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Бот запущен в режиме polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
