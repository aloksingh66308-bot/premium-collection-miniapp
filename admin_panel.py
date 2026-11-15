from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_states = {}

def register_admin_handlers(bot, settings, orders, save_json):

    def is_admin(user_id):
        return user_id == settings["admin_id"]

    def show_panel(chat_id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💰 Change Price", callback_data="admin_price"))
        kb.add(InlineKeyboardButton("✏️ Edit Welcome", callback_data="admin_welcome"))
        kb.add(InlineKeyboardButton("📢 Set Channel", callback_data="admin_channel"))
        kb.add(InlineKeyboardButton("📊 Payment Stats", callback_data="admin_stats"))
        bot.send_message(chat_id, "⚙️ ADMIN PANEL", reply_markup=kb)

    @bot.message_handler(commands=["admin"])
    def admin_command(message):
        if not is_admin(message.from_user.id):
            bot.reply_to(message, "⛔ Access Denied")
            return
        show_panel(message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("admin_"))
    def admin_buttons(call):
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Access Denied")
            return

        action = call.data[6:]
        bot.answer_callback_query(call.id)

        if action == "price":
            admin_states[call.from_user.id] = "price"
            bot.send_message(call.message.chat.id, "Nayi price bhejein. Example: 299")

        elif action == "welcome":
            admin_states[call.from_user.id] = "welcome"
            bot.send_message(call.message.chat.id, "Naya welcome message bhejein.")

        elif action == "channel":
            admin_states[call.from_user.id] = "channel"
            bot.send_message(call.message.chat.id, "Naya private Channel ID bhejein.")

        elif action == "stats":
            total = len(orders)
            paid = sum(1 for x in orders.values() if x.get("status") == "paid")
            pending = sum(1 for x in orders.values() if x.get("status") not in ("paid", "expired"))
            bot.send_message(
                call.message.chat.id,
                f"📊 PAYMENT STATS\n\nTotal Orders: {total}\nPaid Orders: {paid}\nPending Orders: {pending}"
            )

    @bot.message_handler(func=lambda m: m.from_user.id in admin_states)
    def admin_input(message):
        if not is_admin(message.from_user.id):
            admin_states.pop(message.from_user.id, None)
            return

        action = admin_states.pop(message.from_user.id)

        if action == "price":
            try:
                amount = int(message.text.strip())
                if amount < 1:
                    raise ValueError
                settings["amount"] = amount
                save_json("settings.json", settings)
                bot.reply_to(message, f"✅ Price updated: ₹{amount}")
            except ValueError:
                bot.reply_to(message, "❌ Sirf valid amount bhejein. Example: 299")

        elif action == "welcome":
            settings["welcome"] = message.text
            save_json("settings.json", settings)
            bot.reply_to(message, "✅ Welcome message updated.")

        elif action == "channel":
            try:
                channel_id = int(message.text.strip())
                settings["channel_id"] = channel_id
                save_json("settings.json", settings)
                bot.reply_to(message, "✅ Channel ID updated.")
            except ValueError:
                bot.reply_to(message, "❌ Valid numeric Channel ID bhejein.")
