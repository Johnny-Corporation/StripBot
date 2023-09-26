from __main__ import *

@bot.message_handler(commands=["start"], func=time_filter)
def start(message):
    if (message.chat.id not in users):
        users[message.chat.id] = User(bot, message.chat.id)
        sign_in = users[message.chat.id].load_data()
        if sign_in == False:
            users[message.chat.id].add_new_user()
        blacklist[message.chat.id] = []
        reply_blacklist[message.chat.id] = []

    if users[message.chat.id].agreed == False:
        agreement(message)
        return

    welcome(message)

    


def agreement(message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text='Согласен',
        callback_data="agreement",
    )
    markup.add(button)

    bot.send_message(message.chat.id, templates['ru']["start.txt"], reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(commands=["load", "help"], func=time_filter)   #For loading buttons
def welcome(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    text = "ㅤ📲Менюㅤ"
    itembtn = types.KeyboardButton(text)
    markup.add(itembtn)


    bot.send_message(message.chat.id, templates['ru']['welcome.txt'], reply_markup=markup)



def menu(message, back_from=False):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            text="Купить фото💸🌌",
            callback_data="buy_photos"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text="Служба поддержки❓👨‍💻",
            callback_data="feedback"
        )
    )

    if back_from:
        bot.edit_message_text(templates["ru"]["menu.txt"], message.chat.id, message.message_id, reply_markup=keyboard)
        return

    bot.send_message(message.chat.id, templates["ru"]["menu.txt"], reply_markup=keyboard)


def buy_photos(message):
    keyboard = types.InlineKeyboardMarkup()

    for num in nums_sums:

        num_ = types.InlineKeyboardButton(text=f"{num}",callback_data=f"payment-{num}-{nums_sums[num]}")
        sum_ = types.InlineKeyboardButton(text=f"{nums_sums[num]}",callback_data=f"payment-{num}-{nums_sums[num]}")
        keyboard.add(num_,sum_)

    back = keyboard.add(types.InlineKeyboardButton(text="<<<",callback_data=f"back_to_menu"))

    bot.edit_message_text(templates['ru']['purchase.txt'], message.chat.id, message.message_id, parse_mode="HTML", reply_markup=keyboard)


# ---------- BUTTONS HANDLER ----------

@bot.callback_query_handler(func=lambda call: True)
def keyboard_buttons_handler(call):

    if call.data == "agreement":
        users[call.message.chat.id].agreed = True
        welcome(call.message)

    elif call.data == "back_to_menu":
        menu(call.message, back_from=True)
    elif call.data == "buy_photos":
        buy_photos(call.message)
    elif call.data == "feedback":
        reply_to = bot.send_message(
            call.message.chat.id,
            templates['ru']['feedback_how_to_send.txt'],
        )
        reply_blacklist[call.message.chat.id].append(reply_to.message_id)
        bot.register_for_reply(reply_to, feedback_reply_handler)

    elif 'payment' in call.data:
        # accept_payment()

        photos = (call.data).split('-')[1]
        cost = (call.data).split('-')[2]

        accept_payment(message=call.message, photos=photos, cost=cost)



# ---------- MESSAGES HANDLERS ----------

@bot.message_handler(
    content_types=[
        "text",
        "audio",
        "document",
        "sticker",
        "video",
        "video_note",
        "voice",
        "location"
    ],
    func=lambda message: time_filter(message) and reply_blacklist_filter(message)
)
def other_messages_handler(message: types.Message):
    """Handles ignored messages"""

    if (message.chat.id not in users):
        users[message.chat.id] = User(bot, message.chat.id)
        sign_in = users[message.chat.id].load_data()
        if sign_in == False:
            users[message.chat.id].add_new_user()
        blacklist[message.chat.id] = []
        reply_blacklist[message.chat.id] = []

    if users[message.chat.id].agreed == False:
        agreement(message)
        return
    
    if message.text == "ㅤ📲Менюㅤ":
        menu(message)
        return
    

    bot.send_message(message.chat.id, templates['ru']['info.txt'])


@bot.message_handler(
    content_types=[
        "photo"
    ],
    func=lambda message: time_filter(message) and reply_blacklist_filter(message)
)
def photo_messages_handler(message: types.Message):
    """Handles photos messages"""

    if (message.chat.id not in users):
        users[message.chat.id] = User(bot, message.chat.id)
        sign_in = users[message.chat.id].load_data()
        if sign_in == False:
            users[message.chat.id].add_new_user()
        blacklist[message.chat.id] = []
        reply_blacklist[message.chat.id] = []

    if users[message.chat.id].agreed == False:
        agreement(message)
        return
    
    # PHOTO STRIPTING

    new_thread = threading.Thread(
        target=users[message.chat.id].photo_stripting
    )
    new_thread.start()

    


# ---------- REPLY HANDLER ----------

def feedback_reply_handler(inner_message):
    
    chat_info = bot.get_chat(inner_message.chat.id)
    username = chat_info.username
    for id_ in dev_IDs:
        bot.send_message(id_, f"Вам отправлено обращение с {bot_username}\n\nОтправитель: {username}\nТекст:\n{inner_message.text}")

    
    bot.send_message(inner_message.chat.id, templates['ru']['feedback_sent.txt'])