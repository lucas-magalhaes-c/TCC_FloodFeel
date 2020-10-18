
# API
# https://core.telegram.org/bots/api

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ReplyMarkup 
# from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import requests
import json
import sys

def main(request):
    request_json = ""
    if "-local" in sys.argv:
        if "-callback" in sys.argv:
            request_json = json.loads(open("debug/payload_callback.json").read())
        else:
            request_json = json.loads(open("debug/payload.json").read())
    else:
        request_json = request.get_json()
        print(request_json)

    # Ignore requests with no body
    if request_json is None:
        return
    
    run_bot(request_json)

def run_bot(request_json):
    # Get bot config data
    config = json.loads(open("bot_config.json").read())

    # Initializes the message handle
    MH = MessageHandle(request_json=request_json,config=config)

    if MH.is_valid() == False:
        return

    # Initializes the bot with the token
    bot = Bot(token=config["bot_token"]) 

    MH.show_details()
    
    keyboard = [
        [InlineKeyboardButton(text="Consultar enchentes em São Paulo", callback_data='M1')],
        [InlineKeyboardButton(text="Inserir novo foco de enchente", callback_data='M2')],
        [InlineKeyboardButton(text="Cadastrar", callback_data='M3')],
        [InlineKeyboardButton(text="Compartilhar", callback_data='M4')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(
        chat_id=MH.get_user_id(),
        text="Olá, {}!".format(MH.get_username()),
        reply_markup=reply_markup
    )


class MessageHandle():
    def __init__(self,request_json,config):
        
        try:
            request_json["callback_query"]
            self.is_callback_query = True
        except: 
            self.is_callback_query = False

        print("is callback:",self.is_callback_query)
        self.bot_id = config["bot_id"]
        self.bot_name = config["bot_name"]
        self._configure(request_json)

        
    def _configure(self,request_json):
        message = None

        if self.is_callback_query == True:
            message = request_json["callback_query"]["message"]
            
            try:
                self.callback_data = request_json["callback_query"]["data"]
            except:
                self.callback_data = None
                print("Fail to configure requested callback")
        else: 
            message =  request_json["message"]

        # chat info
        try:
            self.chat = message["chat"]
        except:
            self.chat = None
        
        # request from info
        try:
            self.request_from = message["from"]
        except:
            self.request_from = None

        
    def _validate(self):
        if self.is_callback_query:
            try:
                if self.bot_id == self.request_from["id"] and self.bot_name == self.request_from["first_name"]:
                    self.is_valid = True
                else:
                    self.is_valid = False
                    print("Failed on validation: bot id doesnt match")
            except:
                print("Failed on callback query validation")
        else:
            if self.request_from["is_bot"] == True:
                self.is_valid = False
                print("Failed: request from bot")
            else:
                self.is_valid = True

    def show_details(self):
        print("> Chat\nUser id: {}\nUser: {}".format(self.chat["id"],self.chat["first_name"]))
            
    def get_user_id(self):
        return self.chat["id"]
    
    def get_username(self):
        return self.chat["first_name"]

    def get_callback_data(self):
        if self.is_callback_query == True:
            return self.callback_data
        else:
            return None
    
    def is_valid(self):
        return self.is_valid

main(None)

