import json
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import initialize_database, get_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config():
    with open(os.path.join(BASE_DIR, "config.json"), encoding="utf-8") as f:
        return json.load(f)

def load_token():
    env_path = os.path.join(BASE_DIR, ".env")
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("BOT_TOKEN="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("BOT_TOKEN missing from .env")

config = load_config()
initialize_database()
bot = telebot.TeleBot(load_token())

def welcome_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)

    categories = config["categories"]
    for category in categories:
        keyboard.add(InlineKeyboardButton(
            f"💜 {category['name']}",
            callback_data=f"category:{category['id']}"
        ))

    keyboard.row(
        InlineKeyboardButton(
            "📩 Contact Admin",
            url="https://t.me/Spideyownerr"
        ),
        InlineKeyboardButton(
            "📖 How To Use Bot",
            callback_data="tutorial"
        )
    )
    return keyboard

@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (user.id, user.username, user.first_name)
        )

    welcome_text = (
        "✨ WELCOME TO OUR PREMIUM COLLECTION ✨\n\n"
        "Select Your Category According To Your Choice.\n\n"
        "All Categories Are Available At Affordable Prices On Telegram.\n\n"
        "👇 Choose Your Category Below:"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=welcome_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "tutorial")
def tutorial(call):
    bot.answer_callback_query(
        call.id,
        "Tutorial link abhi configure nahi hua hai."
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("category:"))
def category_details(call):
    category_id = int(call.data.split(":")[1])
    category = next(
        (c for c in config["categories"] if c["id"] == category_id),
        None
    )

    if not category:
        bot.answer_callback_query(call.id, "Category nahi mili.")
        return

    if not category["enabled"]:
        bot.answer_callback_query(
            call.id,
            "Ye category abhi available nahi hai.",
            show_alert=True
        )
        return

    text = (
        f"📦 {category['name']}\n\n"
        f"{category['description'] or 'Description coming soon.'}\n\n"
        f"🎬 Collection: {category['collection_count']} Items\n"
        f"💰 Price: ₹{category['price']}"
    )
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "⬅️ Back to Home",
        callback_data="home"
    ))

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "home")
def home(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "✨ Welcome back! Select your category:",
        reply_markup=welcome_keyboard()
    )

print("Premium Collection Bot is starting...")
bot.infinity_polling(skip_pending=True, timeout=30)
