
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
        collection='bot_data'
    )

    doc_ids_separated_by_date = {}
    data_separated_by_date = {}
    schema = []
    
    for doc in docs:
  
        doc_dict = doc.to_dict()
        
        # create a date on the data list
        if doc_dict["location_date"] not in data_separated_by_date:
            data_separated_by_date[doc_dict["location_date"]] = []
            doc_ids_separated_by_date[doc_dict["location_date"]] = []

        doc_ids_separated_by_date[doc_dict["location_date"]].append(doc.id)

        # inserts in the Big Query Schema order
        data_separated_by_date[doc_dict["location_date"]].append({
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

    if data_separated_by_date == []:
        print("No data to upload into bq")
        return

    # Starts BQ Handler, insert data and checks if data is upload successfuly
    BQ = BigQueryHandler(config)
    for date in data_separated_by_date:
        success = BQ.insert_data(data=data_separated_by_date[date], table_type="bot_data_fs",table_date=date)

        if success == True:
            # Update fs_state to sent to bq for all docs
            FH.set_sent_to_bq_fs_state(collection='bot_data', doc_ids=doc_ids_separated_by_date[date])
            print(f"Done. Data from date {date} was sent to Big Query")
        else:
            print(f"Failed. Data from date {date} wasn't sent to Big Query")
    
    
if "-local" in sys.argv:
    main(None)