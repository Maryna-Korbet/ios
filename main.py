import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot("BOT_TOKEN")

my_first_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

my_first_keyboard.add(KeyboardButton("👋 Hi"))
my_first_keyboard.add(KeyboardButton("Bye!"))

@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.send_message(message.chat.id, f"Hello, {message.from_user.username} your surname {message.from_user.last_name}", 
                     reply_markup=my_first_keyboard)


bot.infinity_polling() 