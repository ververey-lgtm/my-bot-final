from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, Filters
import requests
import os
import json

# Ключи API
YOUGILE_API_KEY = os.getenv('YOUGILE_API_KEY')  # Добавьте в настройки Render
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Базовый URL Yougile API
YOUGILE_BASE_URL = "https://ru.yougile.com/api-v2"

class YougileClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_projects(self):
        """Получить список всех проектов"""
        response = requests.get(f"{YOUGILE_BASE_URL}/projects", headers=self.headers)
        return response.json().get('content', [])
    
    def get_columns(self, project_id):
        """Получить колонки проекта"""
        response = requests.get(f"{YOUGILE_BASE_URL}/projects/{project_id}/columns", headers=self.headers)
        return response.json().get('content', [])
    
    def get_tasks(self, project_id):
        """Получить все задачи проекта"""
        response = requests.get(f"{YOUGILE_BASE_URL}/projects/{project_id}/tasks", headers=self.headers)
        return response.json().get('content', [])

# Создаем клиент Yougile
yougile_client = YougileClient(YOUGILE_API_KEY)

async def start(update: Update, context: CallbackContext):
    """Команда /start - показывает список проектов"""
    projects = yougile_client.get_projects()
    
    if not projects:
        await update.message.reply_text("Проекты не найдены")
        return
    
    # Создаем кнопки с названиями проектов
    keyboard = [[project['title']] for project in projects]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Сохраняем проекты в контекст для последующего использования
    context.user_data['projects'] = {project['title']: project['id'] for project in projects}
    
    await update.message.reply_text(
        "Выберите проект:",
        reply_markup=reply_markup
    )

async def handle_project_selection(update: Update, context: CallbackContext):
    """Обработчик выбора проекта"""
    project_name = update.message.text
    projects = context.user_data.get('projects', {})
    
    if project_name not in projects:
        await update.message.reply_text("Проект не найден")
        return
    
    project_id = projects[project_name]
    
    # Получаем задачи и колонки проекта
    tasks = yougile_client.get_tasks(project_id)
    columns = yougile_client.get_columns(project_id)
    
    # Создаем словарь колонок для быстрого доступа
    columns_dict = {col['id']: col['title'] for col in columns}
    
    # Формируем сообщение с задачами
    if not tasks:
        message = "В проекте нет задач"
    else:
        message = f"Задачи проекта '{project_name}':\n\n"
        for task in tasks:
            column_name = columns_dict.get(task['columnId'], 'Неизвестный статус')
            message += f"• {task['title']} - {column_name}\n"
    
    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Снова показываем кнопки проектов
    keyboard = [[project] for project in projects.keys()]
    await update.message.reply_text(
        "Выберите другой проект или введите /start:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def cancel(update: Update, context: CallbackContext):
    """Отмена действия"""
    await update.message.reply_text(
        "Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    
    # Обработчик текстовых сообщений (выбор проекта)
    app.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_project_selection))
    
    print("Бот с интеграцией Yougile запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
