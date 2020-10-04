
# API
# https://core.telegram.org/bots/api

import requests
import json
import sys

def main(request):
    request_json = ""
    if "-local" in sys.argv:
        request_json = json.loads(open("debug/payload.json").read())
    else:
        request_json = request.get_json()
        print(request_json)

    # Ignore requests with no body
    if request_json is None:
        return
    
    # Ignore requests from bots
    if request_json["message"]["from"]["is_bot"] != None and request_json["message"]["from"]["is_bot"] is True:
        print("Request from bot ignored")
        return

    run_bot(request_json)

def run_bot(request_json):
    # Get bot config data
    config = json.loads(open("bot_config.json").read())
    TBOT = TelegramBot(config) 

    if request_json["message"] != None:
        MH = MessageHandle(request_json["message"])
        MH.showDetails()

        TBOT.sendMessage(
            msg="Olá, {}!".format(MH.getUserName()),
            chat_id=MH.getChatId()
            )
    

class TelegramBot():
    def __init__(self,config):
        self.token = config["bot_token"]
        self.base = "https://api.telegram.org/bot{}".format(self.token)+"/"

    def sendMessage(self, msg, chat_id):
        url = self.base + "sendMessage?chat_id={}&text={}".format(chat_id,msg)
        if msg is not None:
            requests.get(url)
        print("Msg enviada")

class MessageHandle():
    def __init__(self,message):
        self._configure(message)
        
    def _configure(self,message):
        try:
            self.user_id = message["from"]["id"]
        except:
            self.user_id = None

        try:
            self.user_name = message["from"]["first_name"]
        except:
            self.user_name = None
        
        try:
            self.chat_id = message["chat"]["id"]
        except:
            self.chat_id = None

    def showDetails(self):
        print("User id: {}\nUser: {}\nChat id: {}".format(self.user_id,self.user_name,self.chat_id))
            
    def getUserId(self):
        return self.user_id
    
    def getUserName(self):
        return self.user_name

    def getChatId(self):
        return self.chat_id

main(None)


