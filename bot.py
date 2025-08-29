import telebot
from telebot import types

# Замени 'ТВОЙ_ТОКЕН_БОТА' на токен, который ты получил от BotFather
TOKEN = 'ТВОЙ_ТОКЕН_БОТА'
bot = telebot.TeleBot(TOKEN)

# Класс для хранения статуса пользователя
class UserStatus:
    def __init__(self, telegram_id, available=True, kitchen=None):
        self.telegram_id = telegram_id
        self.available = available  # True = доступен, False = уехал/недоступен
        self.kitchen = kitchen      # 'kitchen1' или 'kitchen2' или None

    def __repr__(self):
        return f"User(ID: {self.telegram_id}, Available: {self.available}, Kitchen: {self.kitchen})"

# Словари для хранения объектов UserStatus
# Ключ: telegram_id, Значение: объект UserStatus
all_users = {} # Будем хранить всех пользователей здесь
kitchen1_users = {} # ID пользователей, которые выбрали Кухню 1
kitchen2_users = {} # ID пользователей, которые выбрали Кухню 2

def get_user_status(user_id):
    """Получает объект UserStatus для пользователя по ID, создает новый, если его нет."""
    if user_id not in all_users:
        all_users[user_id] = UserStatus(user_id)
    return all_users[user_id]

def update_main_keyboard(chat_id, user_id):
    """Обновляет главную клавиатуру пользователя в зависимости от его статуса."""
    user = get_user_status(user_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    btn_choose_kitchen = types.KeyboardButton("Выбрать кухню")
    btn_monthly_schedule = types.KeyboardButton("График на месяц")
    btn_when_am_i = types.KeyboardButton("Когда я?")

    # Кнопка "Я уехал" или "Я вернулся" меняется в зависимости от user.available
    if user.available:
        btn_im_away_or_back = types.KeyboardButton("Я уехал")
    else:
        btn_im_away_or_back = types.KeyboardButton("Я вернулся")

    markup.add(btn_choose_kitchen, btn_im_away_or_back, btn_monthly_schedule, btn_when_am_i)
    bot.send_message(chat_id, "Выбери действие:", reply_markup=markup)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    get_user_status(user_id) # Убедимся, что пользователь есть в all_users
    update_main_keyboard(message.chat.id, user_id)


@bot.message_handler(func=lambda message: message.text == "Выбрать кухню")
def choose_kitchen_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton("Кухня 1", callback_data='select_kitchen1') # Изменили callback_data
    itembtn2 = types.InlineKeyboardButton("Кухня 2", callback_data='select_kitchen2') # Изменили callback_data
    markup.add(itembtn1, itembtn2)

    bot.send_message(message.chat.id, "Выбери, к какой кухне ты относишься:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_kitchen'))
def callback_inline_kitchen_selection(call):
    user_id = call.from_user.id
    user = get_user_status(user_id)
    selected_kitchen = call.data.replace('select_', '') # Получаем 'kitchen1' или 'kitchen2'

    if user.kitchen == selected_kitchen:
        bot.send_message(call.message.chat.id, f"Ты уже в {selected_kitchen.replace('kitchen', 'Кухне ')}.")
    else:
        # Обновляем кухню пользователя
        user.kitchen = selected_kitchen
        bot.send_message(call.message.chat.id, f"Ты добавлен в {selected_kitchen.replace('kitchen', 'Кухню ')}!")

        # Обновляем словари кухонь
        if selected_kitchen == 'kitchen1':
            kitchen1_users[user_id] = user
            if user_id in kitchen2_users:
                del kitchen2_users[user_id]
        elif selected_kitchen == 'kitchen2':
            kitchen2_users[user_id] = user
            if user_id in kitchen1_users:
                del kitchen1_users[user_id]
    
    # После выбора кухни можно удалить сообщение с кнопками выбора кухни
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    
    # Также обновим главную клавиатуру, чтобы она отражала изменения (хотя здесь не обязательно)
    # update_main_keyboard(call.message.chat.id, user_id) 

    print(f"Пользователь {user_id} теперь в {user.kitchen}. Доступен: {user.available}")
    print(f"Кухня 1: {list(kitchen1_users.keys())}")
    print(f"Кухня 2: {list(kitchen2_users.keys())}")


@bot.message_handler(func=lambda message: message.text in ["Я уехал", "Я вернулся"])
def toggle_user_availability(message):
    user_id = message.from_user.id
    user = get_user_status(user_id)

    if message.text == "Я уехал":
        user.available = False
        bot.send_message(message.chat.id, "Хорошо, я отметил, что ты уехал.")
    else: # message.text == "Я вернулся"
        user.available = True
        bot.send_message(message.chat.id, "Добро пожаловать обратно! Я отметил, что ты вернулся.")
    
    # Обновляем клавиатуру, чтобы изменить кнопку
    update_main_keyboard(message.chat.id, user_id)
    print(f"Пользователь {user_id} доступен: {user.available}")


# Обработчики для других кнопок (пока просто заглушки)
@bot.message_handler(func=lambda message: message.text == "График на месяц")
def monthly_schedule(message):
    bot.send_message(message.chat.id, "Вот твой график на месяц. (Пока не реализовано)")

@bot.message_handler(func=lambda message: message.text == "Когда я?")
def when_am_i(message):
    bot.send_message(message.chat.id, "Ты сейчас тут. (Пока не реализовано)")

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)