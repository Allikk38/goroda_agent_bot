import telebot
import logging
import os
import sys
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# --- ПЫТАЕМСЯ ЗАГРУЗИТЬ .env ФАЙЛ ---
try:
    from dotenv import load_dotenv
    
    # Ищем .env в разных местах
    env_paths = [
        '.env',  # текущая папка
        os.path.join(os.path.dirname(__file__), '.env'),  # папка со скриптом
        '/app/.env',  # для Docker
        os.path.join(os.getcwd(), '.env'),  # рабочая директория
    ]
    
    loaded = False
    for path in env_paths:
        if os.path.exists(path):
            load_dotenv(path)
            loaded = True
            print(f"✅ Загружен .env файл: {path}")
            break
    
    if not loaded:
        print("⚠️ Файл .env не найден, используем переменные окружения системы")
        
except ImportError:
    print("⚠️ python-dotenv не установлен, используем переменные окружения системы")
except Exception as e:
    print(f"⚠️ Ошибка загрузки .env: {e}")

# --- ПОИСК ТОКЕНА ВО ВСЕХ ИСТОЧНИКАХ ---
def find_token():
    """Ищет токен в разных переменных окружения"""
    # Список возможных имен переменных
    possible_names = [
        'BOT_TOKEN', 'bot_token', 'TOKEN', 'token',
        'BOTTOKEN', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_TOKEN',
        'TELOXIDE_TOKEN', 'BOT_TOKEN_ENV'
    ]
    
    # Ищем в переменных окружения
    for name in possible_names:
        token = os.environ.get(name)
        if token and ':' in token:
            print(f"✅ Токен найден в переменной: {name}")
            return token.strip()
    
    # Ищем в .env файле (если dotenv загружен)
    try:
        from dotenv import dotenv_values
        config = dotenv_values('.env')
        for name in possible_names:
            token = config.get(name)
            if token and ':' in token:
                print(f"✅ Токен найден в .env: {name}")
                return token.strip()
    except:
        pass
    
    return None

def find_admin_id():
    """Ищет ID администратора в разных переменных"""
    possible_names = [
        'ADMIN_CHAT_ID', 'admin_chat_id', 'ADMIN_ID', 'admin_id',
        'ADMIN_CHAT', 'admin_chat'
    ]
    
    # Ищем в переменных окружения
    for name in possible_names:
        admin_id = os.environ.get(name)
        if admin_id:
            try:
                return int(admin_id.strip())
            except ValueError:
                continue
    
    # Ищем в .env файле
    try:
        from dotenv import dotenv_values
        config = dotenv_values('.env')
        for name in possible_names:
            admin_id = config.get(name)
            if admin_id:
                try:
                    return int(admin_id.strip())
                except ValueError:
                    continue
    except:
        pass
    
    return None

# --- ПОЛУЧАЕМ ПЕРЕМЕННЫЕ ---
BOT_TOKEN = find_token()
if not BOT_TOKEN:
    print("\n❌ ОШИБКА: BOT_TOKEN не найден!")
    print("\nДоступные переменные окружения:")
    for key, value in os.environ.items():
        if 'TOKEN' in key.upper() or 'BOT' in key.upper() or 'ADMIN' in key.upper():
            print(f"  {key} = {value[:20] if value else 'None'}...")
    
    print("\n📝 Инструкция:")
    print("1. Создайте файл .env в корне проекта")
    print("2. Добавьте в него строки:")
    print("   BOT_TOKEN=ваш_токен_бота")
    print("   ADMIN_CHAT_ID=ваш_telegram_id")
    print("\nИЛИ добавьте переменные в настройках хостинга")
    sys.exit(1)

ADMIN_CHAT_ID = find_admin_id()
if not ADMIN_CHAT_ID:
    print("\n❌ ОШИБКА: ADMIN_CHAT_ID не найден!")
    print("\n📝 Инструкция:")
    print("1. Создайте файл .env в корне проекта")
    print("2. Добавьте в него строку:")
    print("   ADMIN_CHAT_ID=ваш_telegram_id")
    print("\nИЛИ добавьте переменные в настройках хостинга")
    sys.exit(1)

print(f"\n✅ Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
print(f"✅ Admin ID: {ADMIN_CHAT_ID}")
print("=" * 50)

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- СОЗДАНИЕ БОТА ---
try:
    bot = telebot.TeleBot(BOT_TOKEN)
    logger.info("Бот успешно создан")
except Exception as e:
    logger.error(f"Ошибка создания бота: {e}")
    sys.exit(1)

# --- ХРАНИЛИЩЕ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ ---
user_data = {}

# --- КНОПКИ ---
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("Квартира для себя"))
    keyboard.add(KeyboardButton("Инвестиционная квартира"))
    keyboard.add(KeyboardButton("Хочу разместить свой объект"))
    keyboard.add(KeyboardButton("Просто смотрю"))
    return keyboard

def get_rooms_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(1, 6):
        keyboard.add(KeyboardButton(str(i)))
    return keyboard

def get_yes_no_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    return keyboard

# --- ОБРАБОТЧИКИ ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    user_data[user_id] = {}
    
    bot.send_message(
        user_id,
        f"Здравствуйте, {message.from_user.first_name} | Новостройки.\n"
        "Я помощник канала «Города»\n"
        "- Мой сервис помогает жителям Новосибирска и других регионов РФ "
        "в подборе самых интересных объектов недвижимости\n\n"
        "- Ответьте на мои вопросы о ваших пожеланиях, и мы сможем подобрать лучший вариант"
    )
    
    bot.send_message(
        user_id,
        "Ответьте, пожалуйста, что вас интересует?",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text in ["Квартира для себя", "Инвестиционная квартира", "Хочу разместить свой объект", "Просто смотрю"])
def handle_interest(message):
    user_id = message.chat.id
    user_data[user_id]['interest'] = message.text
    
    # Если пользователь просто смотрит - пропускаем вопросы
    if message.text == "Просто смотрю":
        bot.send_message(
            user_id,
            "✅ Отлично! Мы будем держать вас в курсе новых интересных предложений.\n"
            "Подпишитесь на наш канал, чтобы не пропустить обновления!"
        )
        user_data.pop(user_id, None)
        return
    
    msg = bot.send_message(
        user_id, 
        "Выше какой стоимости объекты не предлагать?\n(Введите сумму в рублях)"
    )
    bot.register_next_step_handler(msg, handle_budget_limit)

def handle_budget_limit(message):
    user_id = message.chat.id
    user_data[user_id]['budget_limit'] = message.text
    
    msg = bot.send_message(
        user_id,
        "Сколько комнат вы хотите в будущей квартире?",
        reply_markup=get_rooms_keyboard()
    )
    bot.register_next_step_handler(msg, handle_rooms)

def handle_rooms(message):
    user_id = message.chat.id
    user_data[user_id]['rooms'] = message.text
    
    msg = bot.send_message(user_id, "Какой район для вас предпочтителен?")
    bot.register_next_step_handler(msg, handle_district)

def handle_district(message):
    user_id = message.chat.id
    user_data[user_id]['district'] = message.text
    
    msg = bot.send_message(
        user_id, 
        "Нужна ли вам ипотека?", 
        reply_markup=get_yes_no_keyboard()
    )
    bot.register_next_step_handler(msg, handle_mortgage)

def handle_mortgage(message):
    user_id = message.chat.id
    user_data[user_id]['mortgage'] = message.text
    
    msg = bot.send_message(user_id, "Как Вас зовут?")
    bot.register_next_step_handler(msg, handle_name)

def handle_name(message):
    user_id = message.chat.id
    user_data[user_id]['name'] = message.text
    
    msg = bot.send_message(
        user_id, 
        "Напишите свой номер телефона, и мы сразу включимся в работу!"
    )
    bot.register_next_step_handler(msg, handle_phone)

def handle_phone(message):
    user_id = message.chat.id
    user_data[user_id]['phone'] = message.text
    
    # Формируем сообщение для администратора
    answer = (
        "📝 *Новая заявка с канала «Города»*\n\n"
        f"👤 *Имя:* {user_data[user_id].get('name', '—')}\n"
        f"📞 *Телефон:* {user_data[user_id].get('phone', '—')}\n"
        f"🏠 *Интерес:* {user_data[user_id].get('interest', '—')}\n"
        f"💰 *Бюджет до:* {user_data[user_id].get('budget_limit', '—')} ₽\n"
        f"🛏 *Комнаты:* {user_data[user_id].get('rooms', '—')}\n"
        f"📍 *Район:* {user_data[user_id].get('district', '—')}\n"
        f"🏦 *Ипотека:* {user_data[user_id].get('mortgage', '—')}\n"
        f"🆔 *User ID:* `{user_id}`\n"
        f"👤 *Username:* @{message.from_user.username or 'нет'}"
    )
    
    # Отправка администратору
    try:
        bot.send_message(ADMIN_CHAT_ID, answer, parse_mode='Markdown')
        logger.info(f"✅ Заявка отправлена администратору {ADMIN_CHAT_ID}")
        logger.info(f"   Пользователь: {user_data[user_id].get('name', 'Unknown')}")
    except Exception as e:
        logger.error(f"❌ Не удалось отправить сообщение администратору: {e}")
        bot.send_message(
            user_id,
            "⚠️ Произошла техническая ошибка. Пожалуйста, попробуйте позже.\n"
            "Вы также можете связаться с нами напрямую: @ваш_канал"
        )
        user_data.pop(user_id, None)
        return
    
    # Ответ пользователю
    bot.send_message(
        user_id,
        "✅ *Спасибо!* Ваши данные переданы нашему специалисту.\n"
        "Ожидайте звонка или сообщения в ближайшее время.",
        parse_mode='Markdown'
    )
    
    # Очищаем данные пользователя
    user_data.pop(user_id, None)

# --- ОБРАБОТКА НЕИЗВЕСТНЫХ СООБЩЕНИЙ ---
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(
        message.chat.id,
        "⚠️ Пожалуйста, используйте кнопки для ответа.\n"
        "Или напишите /start чтобы начать заново."
    )

# --- ОБРАБОТКА ОШИБОК ---
@bot.message_handler(content_types=['text'])
def handle_errors(message):
    """Общий обработчик ошибок"""
    try:
        # Если сообщение не обработано другими хендлерами
        pass
    except Exception as e:
        logger.error(f"Ошибка в обработчике: {e}")
        bot.send_message(
            message.chat.id,
            "⚠️ Произошла ошибка. Пожалуйста, начните заново с /start"
        )

# --- ЗАПУСК БОТА ---
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🚀 БОТ ЗАПУЩЕН")
    print("=" * 50)
    print(f"📋 Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    print(f"👤 Администратор: {ADMIN_CHAT_ID}")
    print(f"🔄 Режим: Long Polling")
    print("=" * 50 + "\n")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
