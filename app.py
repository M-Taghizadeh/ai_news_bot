import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
import pandas as pd

TOKEN = '5821119327:AAG9ddgr14MYFeZIngOGDMh7w0qyH5s4hyY'
bot = telebot.TeleBot(TOKEN)
CHANNEL_ID = '@ai_news_farsi'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("ارسال متن به کانال"))
    keyboard.add(KeyboardButton("ارسال تصویر به کانال"))
    bot.send_message(message.chat.id, "سلام! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "ارسال متن به کانال")
def send_text_to_channel(message):
    bot.send_message(message.chat.id, "لطفاً متن مورد نظر را بنویسید:")
    bot.register_next_step_handler(message, process_text_step)


def process_text_step(message):
    try:
        text_to_send = message.text
        bot.send_message(CHANNEL_ID, text_to_send)
        bot.reply_to(message, 'متن با موفقیت در کانال ارسال شد.')
    except Exception as e:
        bot.reply_to(message, f'خطا در ارسال متن: {str(e)}')


@bot.message_handler(func=lambda message: message.text == "ارسال تصویر به کانال")
def send_photo_to_channel(message):
    bot.send_message(message.chat.id, "لطفاً یک عکس را برای ارسال به کانال ارسال کنید:")
    bot.register_next_step_handler(message, process_photo_step)


def process_photo_step(message):
    try:
        if message.photo:
            photo = message.photo[-1].file_id
            bot.send_photo(CHANNEL_ID, photo)
            bot.reply_to(message, 'تصویر با موفقیت در کانال ارسال شد.')
        else:
            bot.reply_to(message, 'لطفاً یک عکس ارسال کنید.')
    except Exception as e:
        bot.reply_to(message, f'خطا در ارسال تصویر: {str(e)}')



df = pd.read_csv("ai_news_bot/news_content.csv")
@bot.message_handler(commands=['send_news'])
def send_news(message):
    text = ""
    for i in range(len(df['title'])):
        row = df.iloc[i]
        text += row['title_fa']

    bot.send_message(CHANNEL_ID, text)


bot.polling()






