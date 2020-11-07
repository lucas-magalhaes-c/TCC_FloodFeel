
# API
# https://core.telegram.org/bots/api

from utils import FloodFeel_Keyboards, hashText, FirestoreHandler, MessageHandle
from telegram import Bot
import requests
import json
import sys

local = False
if "-local" in sys.argv:
    local = True

def main(request):
    request_json = ""
    if local:
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
    config = None
    # Get bot config data
    if local:
        config = json.loads(open("bot_config_local.json").read())
    else:
        config = json.loads(open("bot_config.json").read())

    # Initializes the message handle
    MH = MessageHandle(request_json=request_json,config=config)

    if MH.is_valid == False:
        return
    
    # insert data into BigQuery (also creates a new table if it doesnt exist yet)
    # BQH = BigQueryHandler(config=config)
    # BQH.insert_data(data=MH.data_to_bq,table_type=MH.data_type)

    FH = FirestoreHandler()
    FH.add_document_to_collection(collection="bot_data",data=MH.data_to_bq,data_type=MH.data_type)

    # Initializes the bot with the token and get the keyboard
    bot = Bot(token=config["bot_token"]) 
    text, reply_markup = MH.get_reply_keyboard()
    
    # Send message to user
    bot.send_message(
        chat_id=MH.get_user_id(),
        text=text,
        reply_markup=reply_markup
    )

    if local:
        MH.infos()
        print("> Message sent")
    

if local:
    main(None)


