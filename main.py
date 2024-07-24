import telebot
import os
import json

from dotenv import load_dotenv
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

try:
    bot.get_me()
    print("Bot is active.")
except telebot.apihelper.ApiTelegramException as e:
    print(f"Telegram API error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

my_first_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
my_first_keyboard.add(KeyboardButton("👋 Hi"))
my_first_keyboard.add(KeyboardButton("Bye!"))

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
menu_keyboard.add(KeyboardButton('Add income'))
menu_keyboard.add(KeyboardButton('Add costs'))
menu_keyboard.add(KeyboardButton('View the report'))

def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def update_data():
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

data = load_data()

@bot.message_handler(commands=["start"])
def start(message: Message):
    try:
        bot.send_message(message.chat.id, f"Hello, {message.from_user.username}", reply_markup=my_first_keyboard)
    except Exception as e:
        print(f"Error sending start message: {e}")

@bot.message_handler(func=lambda message: message.text == "👋 Hi")
def handle_hi(message: Message):
    try:
        if str(message.chat.id) not in data.keys():
            data[str(message.chat.id)] = []
            update_data()
        sent_message = bot.send_message(message.chat.id, 'Choose menu:', reply_markup=menu_keyboard)
        bot.register_next_step_handler(sent_message, button_parse)
    except Exception as e:
        print(f"Error handling 'Hi': {e}")

@bot.message_handler(func=lambda message: message.text == "Bye!")
def handle_bye(message: Message):
    try:
        bot.send_message(message.chat.id, 'See you next time!')
    except Exception as e:
        print(f"Error handling 'Bye!': {e}")

def button_parse(message: Message):
    try:
        if message.text == "Add income":
            sent_message = bot.send_message(message.chat.id, 'Enter the receipt amount and comment with a space: ')
            bot.register_next_step_handler(sent_message, handler_income)
        elif message.text == "Add costs":
            sent_message = bot.send_message(message.chat.id, 'Enter the cost amount and comment separated by a space: ')
            bot.register_next_step_handler(sent_message, handler_outcome)
        elif message.text == 'View the report':
            full_count_income = 0
            full_count_outcome = 0

            for operation in data[str(message.chat.id)]:
                if operation['status'] == 'plus':
                    full_count_income += operation['count']
                else:
                    full_count_outcome += operation['count']

            message_text = f'The total amount of expenses: {full_count_outcome} $ \nThe total amount of income: {full_count_income} $\n\n'

            for operation in data[str(message.chat.id)]:
                if operation['status'] == 'plus':
                    message_text += f"+ {operation['count']} | {operation['comment']}\n"
                else:
                    message_text += f"- {operation['count']} | {operation['comment']}\n"
            bot.send_message(message.chat.id, message_text)
            sent_message = bot.send_message(message.chat.id, 'Choose menu:', reply_markup=menu_keyboard)
            bot.register_next_step_handler(sent_message, button_parse)
        else:
            bot.send_message(message.chat.id, 'Unknown command')
            sent_message = bot.send_message(message.chat.id, 'Choose menu:', reply_markup=menu_keyboard)
            bot.register_next_step_handler(sent_message, button_parse)
    except Exception as e:
        print(f"Error parsing button: {e}")

def handler_income(message: Message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            raise ValueError('Invalid input. Please enter the amount and comment separated by a space.')
        count = int(parts[0])
        comment = parts[1]
        data[str(message.chat.id)].append({
            'count': count,
            'comment': comment,
            'status': 'plus'
        })
        update_data()
        bot.send_message(message.chat.id, 'Income added!')
    except (IndexError, ValueError) as e:
        bot.send_message(message.chat.id, str(e))
    finally:
        sent_message = bot.send_message(message.chat.id, 'Choose menu:', reply_markup=menu_keyboard)
        bot.register_next_step_handler(sent_message, button_parse)

def handler_outcome(message: Message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            raise ValueError('Invalid input. Please enter the amount and comment separated by a space.')
        count = int(parts[0])
        comment = parts[1]
        data[str(message.chat.id)].append({
            'count': count,
            'comment': comment,
            'status': 'minus'
        })
        update_data()
        bot.send_message(message.chat.id, 'Expense added!')
    except (IndexError, ValueError) as e:
        bot.send_message(message.chat.id, str(e))
    finally:
        sent_message = bot.send_message(message.chat.id, 'Choose menu:', reply_markup=menu_keyboard)
        bot.register_next_step_handler(sent_message, button_parse)

bot.infinity_polling()