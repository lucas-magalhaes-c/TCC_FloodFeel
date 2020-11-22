from utils import FirestoreHandler, data_generator
from datetime import datetime, timedelta
import requests
import json
import sys

start_time = datetime.strptime('21/11/20 17:00:00', '%d/%m/%y %H:%M:%S') - timedelta(hours=3) #BRT=GMT-3
end_time = datetime.strptime('21/11/20 17:40:00', '%d/%m/%y %H:%M:%S') - timedelta(hours=3) #BRT=GMT-3

local = False
if "-local" in sys.argv:
    local = True

def main(request):
    
    data_to_upload = data_generator(
        start_time=start_time,
        end_time=end_time,
        lat_long_list=["-23.545889,-46.733944"],
        number_per_lat_long=5
    )
    print(f"Uploading {len(data_to_upload)} documents...")

    FH = FirestoreHandler()
    try:
        for data in data_to_upload:
            FH.add_document_to_collection(
                collection='bot_data',
                data=data,
                data_type="generated"
            )
        print(f"Documents uploaded. Total: {len(data_to_upload)}")
    except Exception as e:
        print(f"Failed to upload {len(data_to_upload)} documents:\n",e)

if local:
    main(None)