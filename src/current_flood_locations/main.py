import requests
import sys
import json
from utils import StorageHandler, BigQueryHandler
from datetime import datetime

date = datetime.today().strftime('%Y-%m-%d')

# lat_long_list = ["-23.545889,-46.733944","-23.508122801140846,-46.6896260551143","-23.5093793619657,-46.6658274385218","-23.516069505516327,-46.66750620864545","-23.513805260523746,-46.65334738595098","-23.516965771395327,-46.666784170819476","-23.455892102947654,-46.62799385849749","-23.52571074872409,-46.59556910991703","-23.52913300951429,-46.598004366258536","-23.528618281363837,-46.59687396568954"]
delimiter = "%7C"

def main(request):
    config = json.loads(open("config_local.json").read()) if "-local" in sys.argv else json.loads(open("config.json").read())
    
    # Query BQ to get all the current flood locations
    BQH = BigQueryHandler(config=config)
    lat_long_list = BQH.get_latlong(table_date=date)

    url_list = []

    # get url and insert token
    url_base = config["url"].replace("<maps_api_token>",config["maps_api_token"])
    
    
    for parameter in config["parameters"]:
        url = url_base

        # insert center and zoom
        url = url.replace("<center>",parameter["center"]).replace("<zoom>",str(parameter["zoom"]))
        
        # get markers template, insert color and insert size
        markers = config["markers_template"].replace("<markers_color>",parameter["markers_color"]).replace("<markers_size>",parameter["markers_size"])
        
        # format coordinates
        markers_coordinates = ""
        for lat_long in lat_long_list:
            markers_coordinates = markers_coordinates + delimiter + lat_long

        # insert coordinates
        markers = markers.replace("<markers_coordinates>",markers_coordinates)

        # insert markers
        url = url.replace("<markers>",markers)
        
        url_list.append({"url":url,"type":parameter["type"]})
    

    SH = StorageHandler(config["storage_bucket_name"])

    # upload images to storage
    for url_info in url_list:
        filedata = requests.get(url_info["url"])

        # local debug
        if "-local" in sys.argv:
            with open(f'debug_maps/{url_info["type"]}.jpg', 'wb') as f:
                f.write(filedata.content)
        
        SH.upload_image(
            storage_file_path=f'sao_paulo/{url_info["type"]}',
            image_data=filedata.content,
            img_type='jpg'
        )

    print(f"Current flood locations per region refreshed: {len(url_list)} images")



if "-local" in sys.argv:
    main(None)