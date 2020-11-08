
from utils import FirestoreHandler, BigQueryHandler
from datetime import datetime
import sys
import json

date = datetime.today().strftime('%Y-%m-%d')

def main (request):
    config = None

    if "-local" in sys.argv:
        config = json.loads(open("bot_config_local.json").read())
    else:
        # Get bot config data
        config = json.loads(open("bot_config.json").read())

    FH = FirestoreHandler()
    docs = FH.get_documents(
        collection='bot_data', 
        field='location_date', 
        operator='==', 
        field_value=date,
        sent_to_bq=False
    )

    doc_ids = []
    data = []
    schema = []
    for doc in docs:
        doc_ids.append(doc.id)
        
        doc_dict = doc.to_dict()

        # inserts in the Big Query Schema order
        data.append({
            "location_date": doc_dict["location_date"],
            "user_id_hash": doc_dict["user_id_hash"],
            "location_timestamp_ms": doc_dict["location_timestamp_ms"],
            "latitude": doc_dict["latitude"],
            "longitude": doc_dict["longitude"],
            "photo_date": doc_dict["photo_date"],
            "photo_timestamp_ms": doc_dict["photo_timestamp_ms"],
            "file_id": doc_dict["file_id"],
            "file_unique_id": doc_dict["file_unique_id"]
        })

    # Starts BQ Handler, insert data and checks if data is upload successfuly
    BQ = BigQueryHandler(config)
    success = BQ.insert_data(data, "bot_data_fs")

    if success == True:
        #TODO: update data in Firestore
        print("Done. Data was sent to Big Query")
    else:
        print("Failed. Data wasn't sent to Big Query")
    
    # for doc in docs:
    #     print(f'{doc.id} => {doc.to_dict()}')
    
    


if "-local" in sys.argv:
    main(None)