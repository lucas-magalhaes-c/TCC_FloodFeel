from utils import FirestoreHandler, data_generator
from datetime import datetime, timedelta
import requests
import json
import sys

water_level_info_list = {
    0: {"water_level": 0, "water_level_case": "Não soube informar"},
    1: {"water_level": 1, "water_level_case": "Nível 1"},
    2: {"water_level": 2, "water_level_case": "Nível 2"},
    3: {"water_level": 3, "water_level_case": "Nível 3"},
    4: {"water_level": 4, "water_level_case": "Nível 4"}
}

water_level_info_case = 0
number_per_lat_long = 1
start_time = datetime.strptime('26/11/20 15:00:00', '%d/%m/%y %H:%M:%S') - timedelta(hours=3) #BRT=GMT-3
end_time = datetime.strptime('26/11/20 17:35:00', '%d/%m/%y %H:%M:%S') - timedelta(hours=3) #BRT=GMT-3


# lat_long_list = ["-23.545889,-46.733944","-23.508122801140846,-46.6896260551143","-23.5093793619657,-46.6658274385218","-23.516069505516327,-46.66750620864545","-23.513805260523746,-46.65334738595098","-23.516965771395327,-46.666784170819476","-23.455892102947654,-46.62799385849749","-23.52571074872409,-46.59556910991703","-23.52913300951429,-46.598004366258536","-23.528618281363837,-46.59687396568954"]
lat_long_list = ["-23.545889,-46.733944"]


local = False
if "-local" in sys.argv:
    local = True

def main(request):
    
    data_to_upload = data_generator(
        start_time=start_time,
        end_time=end_time,
        lat_long_list=lat_long_list,
        water_level_info=water_level_info_list[water_level_info_case],
        number_per_lat_long=number_per_lat_long
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