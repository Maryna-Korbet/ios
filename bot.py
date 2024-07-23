import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
import json

with open('data.json', 'r') as file:
    data = json.load(file)

def update_data():
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

bot = telebot.TeleBot("YOUR_ACTUAL_BOT_TOKEN")

try:
    bot.get_me()
    print("Bot is active.")
except telebot.apihelper.ApiTelegramException as e:
    print(f"Telegram API error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
menu_keyboard.add(KeyboardButton('Додати надходження'))
menu_keyboard.add(KeyboardButton('Додати витрати'))
menu_keyboard.add(KeyboardButton('Переглянути звіт'))

@bot.message_handler(commands=['start'])
def start(message: Message):
    if str(message.chat.id) not in data.keys():
        data[str(message.chat.id)] = []
        update_data()
    sent_message = bot.send_message(message.chat.id, 'Оберіть пункт меню:', reply_markup=menu_keyboard)
    bot.register_next_step_handler(sent_message, button_parse)

def button_parse(message: Message):
    if message.text == "Додати надходження":
        sent_message = bot.send_message(message.chat.id, 'Введіть суму надходження та коментар через пробіл: ')
        bot.register_next_step_handler(sent_message, handler_income)
    elif message.text == "Додати витрати":
        sent_message = bot.send_message(message.chat.id, 'Введіть суму витрат та коментар через пробіл: ')
        bot.register_next_step_handler(sent_message, handler_outcome)
    elif message.text == 'Переглянути звіт':
        full_count_income = 0
        full_count_outcome = 0

        for operation in data[str(message.chat.id)]:
            if operation['status'] == 'plus':
                full_count_income += operation['count']
            else:
                full_count_outcome += operation['count']

        message_text = f'Загальна сума витрат: {full_count_outcome} грн \nЗагальна сума надходжень: {full_count_income} грн\n\n'

        for operation in data[str(message.chat.id)]:
            if operation['status'] == 'plus':
                message_text += f"+ {operation['count']} | {operation['comment']}\n"
            else:
                message_text += f"- {operation['count']} | {operation['comment']}\n"
        bot.send_message(message.chat.id, message_text)
        start(message)
    else:
        bot.send_message(message.chat.id, 'Невідома команда')
        start(message)

def handler_income(message: Message):
    count = message.text.split(' ', 1)[0]
    comment = message.text.split(' ', 1)[1]
    data[str(message.chat.id)].append(
        {
            'count': int(count),
            'comment': comment,
            'status': 'plus'
        }
    )
    bot.send_message(message.chat.id, 'Надходження додано')
    update_data()
    start(message)

def handler_outcome(message: Message):
    count = message.text.split(' ', 1)[0]
    comment = message.text.split(' ', 1)[1]
    data[str(message.chat.id)].append(
        {
            'count': int(count),
            'comment': comment,
            'status': 'minus'
        }
    )
    bot.send_message(message.chat.id, 'Витрата додана')
    update_data()
    start(message)

bot.infinity_polling()