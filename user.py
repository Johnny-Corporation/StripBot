from dataclasses import dataclass
import time
from telebot import TeleBot


#Database
from db_controller import Controller
db_controller = Controller()

from __main__ import *

@dataclass
class User:

    bot: TeleBot
    chat_id: int
    agreed: bool = False

    def __post_init__(self):
        self.used_photos: int = 0
        self.photos_limit: int = 1

    def photo_stripting(self):

        if self.used_photos>=self.photos_limit:
            self.bot.send_message(self.chat_id, templates['ru']['photos_excess.txt'], parse_mode="HTML")
            return

        wait_message = self.bot.send_message(self.chat_id, templates['ru']['wait.txt'], parse_mode="HTML")
        

        time.sleep(3)

        self.bot.delete_message(self.chat_id, wait_message.message_id)
        self.bot.send_message(self.chat_id, "МЫ ПОКА НЕ СДЕЛАЛИ НО ТЫ МОЖЕШЬ ЗАПЛАТИТЬЫ")

        self.used_photos += 1
        db_controller.update_used_photos_by_chat_id(self.chat_id, self.used_photos)


    def apply_payment(self, photos):

        self.photos_limit += photos

        db_controller.update_limit_photos_by_chat_id(self.chat_id, self.photos_limit)

    def add_new_user(self):
        db_controller.add_user(chat_id=self.chat_id, limit_of_photos=self.photos_limit, used_photos=self.used_photos)

    
    def load_data(self):
        user_data = db_controller.get_user_by_chat_id(user_chat_id=self.chat_id)

        if user_data != {}:
            self.photos_limit = user_data["LimitPhotos"]
            self.used_photos = user_data["UsedPhotos"]
            return 
    
        return False


    