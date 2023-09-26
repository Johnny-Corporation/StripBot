# --- IMPORT LIBRARIES ---
from os import environ, makedirs, path, remove, path, listdir
from dotenv import load_dotenv
from datetime import datetime


# Bot API
from telebot import TeleBot, types
from telebot.apihelper import ApiTelegramException

makedirs("output//", exist_ok=True)



# ---------- TEMPLATES ----------

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




# --- CLASS IMPORT ---
users = {}
from user import User





load_dotenv(".env")

bot_token = environ.get("BOT_API_TOKEN")
dev_IDs = environ.get("DEVELOPER_CHAT_IDS").split(",")



# --------------- BOT INITIALIZATION ---------------

bot_token = environ.get("BOT_API_TOKEN")

bot = TeleBot(bot_token)
bot_id = bot.get_me().id
bot_username = bot.get_me().username



# ---------- PAYMENT INITIALIZATION ----------

yoomoney_token = environ.get("PAYMENT_RUS_TOKEN")

nums_sums = {2: 100, 5: 300, 10: 600, 15: 900}

from pay import *



# ---------- TIME FILTER ----------

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


# ---------- REPLY FILTER ----------

blacklist = {}  # chat_id:[messages_ids] needed for filtering messages
reply_blacklist = {}  # chat_id:[messages_ids] needed for filtering replies to messages
def reply_blacklist_filter(message: types.Message):
    """Blocks message if it is a reply to message which is in reply_blacklist"""
    if message.chat.id not in blacklist:
        return True
    return (message.reply_to_message is None) or (
        message.reply_to_message.message_id not in reply_blacklist[message.chat.id]
    )


# ---------- COMMANDS HANDLERS ----------

from handlers import *

bot.polling()
