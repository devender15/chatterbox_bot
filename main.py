import praw
import telebot
import openai
import os
from dotenv import load_dotenv

# loading our secret keys from .env file
load_dotenv()

# global variables storing secret keys
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

# creating our bot instance
bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_KEY


# REDDIT DATA

# names of some popular subreddits
subs = ["TIL", "TrueOfMyChest", "IWantToLearn", "Futurology", "Showerthoughts", "unpopularopinion", "LifeProTip", "Teenagers"]

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="telegram bot"
)


# functions
def search_openai(message):
    completion = openai.Completion.create(engine="text-davinci-003", prompt=message, max_tokens=1000)
    return completion.choices[0].text

def create_image(chat_id, message):
    try:
        response = openai.Image.create(
            prompt=message,
            n=1,
            size="1024x1024"
        )
        bot.send_photo(chat_id, response["data"][0]["url"])

    except:
        bot.send_message(chat_id, "Sorry, I can't create an image for this topic 😞")

def reddit_stories(message):
    top_stories = reddit.subreddit(message.text).hot(limit=10)
    stories = []
    for story in top_stories:
        if(len(story.selftext) > 0):
            stories.append({
                "title": story.title,
                "content": story.selftext,
                "author": story.author.name
            })

    for i in range(len(stories)):
        bot.send_message(message.chat.id, f"Title: {stories[i]['title']}\n\n\nStory: {stories[i]['content']}\n\n\nPosted by: {stories[i]['author']}" )

def reddit_videos(message):
    
    subreddit = reddit.subreddit("crazyfuckingvideos")

    try:
        for submission in subreddit.new(limit=1):
            if submission.is_video:
                bot.send_video(chat_id=message.chat.id, video=submission.url) 
            else:
                bot.send_message(chat_id=message.chat.id, text="Sorry, I can't find any videos 😞")
    except:
        bot.send_message(chat_id=message.chat.id, text="Sorry, I can't find any videos 😞")

# bot commands
@bot.message_handler(commands=['start', 'hello', "speak"])
def send_welcome(message):
    bot.reply_to(message, "How are you?")

@bot.message_handler(commands=['chat'])
def handle_message(message):

    if(message.text.lower() == "i am fine" or message.text.lower() == "im fine"):
        bot.reply_to(message, "Good 😇")
    
    else:
        bot.reply_to(message, search_openai(message.text))

@bot.message_handler(commands=['create'])
def handle_image(message):
    if("image" in message.text.lower()):
        bot.reply_to(message, "hold on, I'm creating an image for you...")
        create_image(message.chat.id, message.text)

@bot.message_handler(commands=['reddit'])
def handle_reddit(message):
    if("read" in message.text.lower()):
        markup = telebot.types.ReplyKeyboardMarkup(row_width=len(subs), one_time_keyboard=True)
        for sub in subs:
            option = telebot.types.KeyboardButton(sub)
            markup.add(option)
        bot.send_message(chat_id=message.chat.id, text="Select any sub: ", reply_markup=markup)
    
    elif("video" in message.text.lower()):
        reddit_videos(message)

@bot.message_handler(func=lambda msg: msg.text in subs)
def send_reddit_stories(message):
    bot.send_message(message.chat.id, "Here are some stories from r/" + message.text)
    reddit_stories(message)


bot.infinity_polling()