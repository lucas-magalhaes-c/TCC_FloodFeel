
# API
# https://core.telegram.org/bots/api

from telegram import Bot
import requests
import json
import sys
from utils import FloodFeel_Keyboards, hashText
import time 

timestamp_ms = round(time.time() * 1000)

def main(request):
    request_json = ""
    if "-local" in sys.argv:
        if "-payload" in sys.argv:
            payload = sys.argv[sys.argv.index("-payload") + 1]
            request_json = json.loads(open("debug/payload_"+payload+".json").read())
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

    if MH.is_valid_request() == False:
        return

    # Initializes the bot with the token
    bot = Bot(token=config["bot_token"]) 

    MH.show_details()

    text, reply_markup = MH.get_reply_keyboard()

    bot.send_message(
        chat_id=MH.get_user_id(),
        text=text,
        reply_markup=reply_markup
    )


class MessageHandle():
    def __init__(self,request_json,config):
        self.location = None
        self.photo_data = None
        self.message_text = None
        self.message = None
        self.callback_data = None
        self.data_to_bq = {}
        self.bq_table = None
        self.hash_salt = config["hash_salt"]

        try:
            request_json["callback_query"]
            self.is_callback_query = True
        except: 
            self.is_callback_query = False

        self.bot_id = config["bot_id"]
        self.bot_name = config["bot_name"]

        # configure from request json
        self._configure(request_json)

        # check if request is valid
        self._validate()

        # configure data to be inserted on Big Query
        self._configureBQData()

    def get_reply_keyboard(self):
        FFKeyboards = FloodFeel_Keyboards(callback_data=self.callback_data,message=self.message)
        
        return FFKeyboards.get_reply()
            
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
            message = request_json["message"]
            self.message = message
            try:
                self.message_text = request_json["message"]["text"]
            except:
                self.message_text = None
                print("Fail to configure requested message")

        # chat info
        try:
            self.chat = message["chat"]
        except:
            print("Failed on extracting chat")
            self.chat = None
        
        # request from info
        try:
            self.request_from = message["from"]
        except:
            print("Failed on extracting request from data")
            self.request_from = None

        # geolocation info
        if "location" in message:
            self.location = message["location"]

        # photo info
        if "photo" in message:
            self.photo_data = message["photo"]
        
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
    
    def is_valid_request(self):
        return self.is_valid

    def _configureBQData(self):
        if self.location != None or self.photo_data != None:
            self.data_to_bq["user_id_hash"] = hashText(text=str(self.get_user_id()), salt=self.hash_salt)
            self.data_to_bq["timestamp_ms"] = timestamp_ms

            if self.location != None:
                # table to send the data
                self.bq_table = "location"

                self.data_to_bq["latitute"] = self.location["latitude"]
                self.data_to_bq["longitude"] = self.location["longitude"]
            elif self.photo_data != None:
                # table to send the data
                self.bq_table = "photo"

                # pick the best quality photo in the list (the last element is the best)
                best_photo = self.photo_data[-1]

                self.data_to_bq["file_id"] = best_photo["file_id"]
                self.data_to_bq["file_unique_id"] = best_photo["file_unique_id"]
        
        print(self.data_to_bq)


if "-local" in sys.argv:
    main(None)


