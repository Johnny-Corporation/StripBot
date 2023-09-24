# --- IMPORT LIBRARIES ---
from os import environ, makedirs, path, remove, path, listdir
from dotenv import load_dotenv
from datetime import datetime

# Bot API
from telebot import TeleBot, types
from telebot.apihelper import ApiTelegramException



#CLASSES IMPORT

# groups = {}  # {group chat_id:Johnny object}
# from Johnny import Johnny



# --------------- BOT INITIALIZATION ---------------

load_dotenv(".env")

bot_token = environ.get("BOT_API_TOKEN")

bot = TeleBot(bot_token)
bot_id = bot.get_me().id
bot_username = bot.get_me().username



# --- TEMPLATES ---

def load_templates(dir: str) -> dict:
    """Get templates dict {language_code: {file_name: content}}

    Args:
        dir (str): path to directory with templates

    Returns:
        dict
    """
    file_dict = {}
    for language_code in listdir(dir):
        if path.isfile(path.join(dir, language_code)):
            with open(path.join(dir, language_code), "r") as f:
                file_dict[language_code] = f.read()
            continue
        for file_name in listdir(path.join(dir, language_code)):
            if file_name.endswith(".txt"):
                file_path = path.join(dir, language_code, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    if language_code not in file_dict:
                        file_dict[language_code] = {file_name: content}
                    else:
                        file_dict[language_code][file_name] = content
    return file_dict

templates = load_templates("templates\\")



# --- TIME FILTER ---

start_time = datetime.now()
skip_old_messages = True  # True until message older than bot start time received
ignored_messages = 0  # count number of ignored messages when bot was offline for logs
def time_filter(message: types.Message):
    """Filters message which were sent before bot start"""
    global skip_old_messages, ignored_messages
    if not skip_old_messages:
        return True
    message_time = datetime.fromtimestamp(message.date)
    if start_time < message_time:
        skip_old_messages = False
        return True
    else:
        ignored_messages += 1
        return False


# --- COMMANDS HANDLERS ---

@bot.message_handler(commands=["start"], func=time_filter)
def start(message):

    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text='Согласен',
        callback_data="agreement",
    )
    markup.add(button)

    bot.send_message(message.chat.id, templates['ru']["start.txt"], reply_markup=markup, parse_mode="Markdown")
@bot.callback_query_handler(func=lambda call: "True")
def keyboard_buttons_handler(call):
    if call.data == "agreement":
        welcome(call.message)


def welcome(message):

    bot.send_message(message.chat.id, templates['ru']['welcome.txt'])


# --- MESSAGES HANDLERS ---

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
    func=lambda message: time_filter(message)
)
def other_messages_handler(message: types.Message):
    """Handles ignored messages"""
    
    bot.send_message(message.chat.id, templates['ru']['info.txt'])


@bot.message_handler(
    content_types=[
        "photo"
    ],
    func=lambda message: time_filter(message)
)
def photo_messages_handler(message: types.Message):
    """Handles photos messages"""
    
    # PHOTO STRIPTING

    bot.send_message(message.chat.id, templates['ru']['wait.txt'])







bot.infinity_polling(timeout=500)
