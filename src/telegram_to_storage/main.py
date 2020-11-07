import requests
import json
import sys

# import pdb
# pdb.set_trace()

def main(request):
    request_json = ""
    config = None

    if "-local" in sys.argv:
        request_json = json.loads(open("../debug/telegram_to_storage_req.json").read())
        config = json.loads(open("bot_config_local.json").read())
    else:
        request_json = request.get_json()

        # Get bot config data
        config = json.loads(open("bot_config.json").read())
    
    token = config["bot_token"]

    
    if "-id" in sys.argv: # local debug
        file_id = sys.argv[sys.argv.index("-id") + 1]
        request_json = {"file_ids":[]}
        request_json["file_ids"].append(file_id)

    for file_id in request_json["file_ids"]:

        try:
            # Configure get file path and make a request for complete info
            info = requests.get(config["getFilePath_url"].replace("<token>",token).replace("<file_id>", file_id))
            info = info.json()["result"]
            print(info)
        except:
            print("Failed to get file info from Telegram")

        if "file_path" in info:
            try:
                # Configure get file path and make a request for complete info
                filedata = requests.get(config["getFile_url"].replace("<token>",token).replace("<file_path>", info["file_path"]))
                
                if "-local" in sys.argv:
                    with open('example.jpg', 'wb') as f:
                        f.write(filedata.content)
            except:
                print("Failed to get file data from Telegram")
        else: 
            print("Failed to get file path")

if "-local" in sys.argv:
    main(None)
        

