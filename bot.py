from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
                print("Ответ:", response.text)
                return []
                
        except Exception as e:
            print(f"Ошибка при получении проектов: {e}")
            return []
    
    def get_columns(self, project_id):
        """Получить колонки проекта"""
        try:
            response = requests.get(
                f"{YOUGILE_BASE_URL}/projects/{project_id}/columns", 
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json().get('content', [])
            return []
        except:
            return []
    
    def get_tasks(self, project_id):
        """Получить все задачи проекта"""
        try:
            response = requests.get(
                f"{YOUGILE_BASE_URL}/projects/{project_id}/tasks", 
                headers=self.headers,
                params={'limit': 100}
            )
            if response.status_code == 200:
                return response.json().get('content', [])
            return []
        except:
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

async def handle_project_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора проекта"""
    project_name = update.message.text
    projects = context.user_data.get('projects', {})
    
    if project_name not in projects:
        await update.message.reply_text("Проект не найден")
        return
    
    project_id = projects[project_name]
    await update.message.reply_text(f"Загружаю задачи проекта '{project_name}'...")
    
    # Получаем задачи и колонки
    tasks = yougile_client.get_tasks(project_id)
    columns = yougile_client.get_columns(project_id)
    
    # Создаем словарь колонок
    columns_dict = {col['id']: col['title'] for col in columns}
    
    # Формируем сообщение
    if not tasks:
        message = "В проекте нет задач"
    else:
        message = f"Задачи проекта '{project_name}':\n\n"
        for task in tasks[:10]:  # Показываем первые 10 задач
            column_name = columns_dict.get(task.get('columnId'), 'Неизвестный статус')
            message += f"• {task.get('title', 'Без названия')} - {column_name}\n"
        
        if len(tasks) > 10:
            message += f"\n... и еще {len(tasks) - 10} задач"
    
    await update.message.reply_text(message)
    
    # Снова показываем кнопки
    keyboard = [[project] for project in projects.keys()]
    await update.message.reply_text(
        "Выберите другой проект:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def main():
    # Удаляем вебхук перед запуском
    import requests
    delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    response = requests.get(delete_url)
    print("Удаление вебхука:", response.json())
    
    # Тестируем подключение к Yougile
    print("Проверка подключения к Yougile...")
    test_url = f"{YOUGILE_BASE_URL}/projects"
    test_response = requests.get(test_url, headers=yougile_client.headers)
    print("Статус Yougile:", test_response.status_code)
    print("Ответ Yougile:", test_response.text[:200])  # Первые 200 символов
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_project_selection))
    
    print("Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
