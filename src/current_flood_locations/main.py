import requests
import sys
import json
from utils import StorageHandler, BigQueryHandler
from datetime import datetime

date = datetime.today().strftime('%Y-%m-%d')

# lat_long_list = ["-23.545889,-46.733944"]
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
    return '', 201


if "-local" in sys.argv:
    main(None)