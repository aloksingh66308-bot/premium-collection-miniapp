import telebot
from config import BOT_TOKEN
import time

bot = telebot.TeleBot(BOT_TOKEN)
print("Waiting for channel post...")

while True:
    updates = bot.get_updates(timeout=20)
    for update in updates:
        if update.channel_post:
            print("CHANNEL ID:", update.channel_post.chat.id)
            print("Channel Found Successfully!")
            exit()
