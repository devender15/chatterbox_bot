import os
import telebot
import openai

# reading secret keys from .env file
BOT_TOKEN = ""
OPENAI_KEY = ""


# creating our bot instance
bot = telebot.TeleBot(BOT_TOKEN)


def search_openai(message):
    openai.api_key = OPENAI_KEY
    completion = openai.Completion.create(engine="text-davinci-003", prompt=message, max_tokens=1000)

    return completion.choices[0].text

@bot.message_handler(commands=['start', 'hello', "speak"])
def send_welcome(message):
    bot.reply_to(message, "How are you?")

@bot.message_handler(func=lambda msg: True)
def handle_message(message):

    if(message.text.lower() == "i am fine" or message.text.lower() == "im fine"):
        bot.reply_to(message, "Good 😇")
    
    else:
        bot.reply_to(message, search_openai(message.text))


bot.infinity_polling()