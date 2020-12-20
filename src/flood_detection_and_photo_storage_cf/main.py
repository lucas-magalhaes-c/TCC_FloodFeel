from utils import FirestoreHandler, StorageHandler
import requests
import sys
import json


# The photo is stored in storage with the name <user_id_hash><photo_timestamp_ms>.jpg

def main (request):
    config = None

    config = json.loads(open("config_local.json").read()) if "-local" in sys.argv else json.loads(open("config.json").read())

    getFilePath_url_base = config["getFilePath_url"].replace("<token>", config["bot_token"])
    getFile_url_base = config["getFile_url"].replace("<token>", config["bot_token"])

    FH = FirestoreHandler()
    docs = FH.get_documents_waiting_for_flood_detection(
        collection='bot_data'
    )

    SH = StorageHandler("received_images")

    number_of_files = 0

    for doc in docs:
        doc_dict = doc.to_dict()

        # get the file path of the file_id on telegram server
        getFilePath_url = getFilePath_url_base.replace("<file_id>",doc_dict["file_id"])
        response = requests.get(getFilePath_url).json()
        file_path = response["result"]["file_path"]

        # get the file from telegram server
        getFile_url = getFile_url_base.replace("<file_path>",file_path)
        response = requests.get(getFile_url)
        
        # TODO: send the photo to flood validation
        #
        # Module on GCP
        # Simulation
        data = {
            "user_id_hash": doc.id,
            "is_flood": True
        }
        
        # update document state
        FH.add_document_to_collection(
            collection='bot_data',
            data=data,
            data_type='flood_detection'
        )

        # save photo in Google Storage
        folder = "detected_as_flood" if data["is_flood"] == True else "detected_as_not_flood"
        SH.upload_image(
            image_data=response.content,
            storage_file_path=f'{folder}/{data["user_id_hash"]}_{doc_dict["photo_timestamp_ms"]}',
            img_type="jpg"
        )
        number_of_files = number_of_files + 1
    
    print('No data to check and upload' if number_of_files == 0 else f'{number_of_files} photos validated and uploaded')
    return '', 201
        

if "-local" in sys.argv:
    main(None)