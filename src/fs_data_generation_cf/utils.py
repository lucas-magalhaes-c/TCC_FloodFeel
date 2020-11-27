
import os
import sys
import json

import numpy as np
from datetime import datetime
import google.auth

def data_generator(start_time, end_time, lat_long_list, water_level_info, number_per_lat_long=10):
    # 300000 ms is 5 minutes, 60000 ms is 1 minute
    data_generated = []

    if not isinstance(start_time,datetime) or not isinstance(end_time,datetime):
        print("Start time and end_time must be instance of datetime")
        return []

    if end_time < start_time:
        print("End time must be less than start time")
        return []

    end_timestamp_ms = end_time.timestamp() * 1000
    start_timestamp_ms = start_time.timestamp() * 1000

    for lat_long in lat_long_list:
        n = 0
        number_per_lat_long_custom = number_per_lat_long + np.random.randint(-int(number_per_lat_long*0.5), int(number_per_lat_long*0.5)+1)
        number_per_lat_long_custom = number_per_lat_long_custom if number_per_lat_long_custom > 0 else 1 # at least one

        while n < number_per_lat_long_custom:

            location_timestamp_ms = np.random.randint(start_timestamp_ms, end_timestamp_ms + 1)

            data = {}

            splited = lat_long.split(",")
            custom_lat_long = str(round(float(splited[0])+np.random.randint(-500,501)/1000000,6))+","+str(round(float(splited[1])+np.random.randint(-500,501)/1000000,6))

            data["file_id"] = "1"
            data["file_unique_id"] = "1"
            data["location_date"] = datetime.fromtimestamp(location_timestamp_ms/1000).strftime('%Y-%m-%d')
            data["location_timestamp_ms"] = location_timestamp_ms
            data["lat_long"] = custom_lat_long
            data["photo_date"] = datetime.fromtimestamp(location_timestamp_ms/1000+30).strftime('%Y-%m-%d')
            data["photo_timestamp_ms"] = location_timestamp_ms + 30000 # 30 seconds
            data["user_id_hash"] = str(np.random.randint(0,3000000))
            data["is_flood"] = True
            data["water_level"] = water_level_info["water_level"]
            data["water_level_case"] = water_level_info["water_level_case"]

            data_generated.append(data)
            n = n + 1

    return data_generated



import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class FirestoreHandler():
    def __init__(self):
        
        # firestore document state (fs_state)
        self.fs_state = {
            1: "Waiting for flood prediction",
            2: "Flood prediction check, waiting to send to BQ",
            3: "Flood prediction check, sent to BQ"
        }

        service_account_path = 'service_account_local.json' if "-local" in sys.argv else 'service_account.json'

        # open and load service account & project id
        sa_file = open(service_account_path)
        sa_json = json.loads(sa_file.read())
        project_id = sa_json['project_id']

        if "-local" not in sys.argv:
            # Use the application default credentials, in GCP
            if (not len(firebase_admin._apps)):
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id})

        else:
            # Testing locally
            # Use a service account
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()
    
    def add_document_to_collection(self,collection,data,data_type):

        doc_ref = self.db.collection(collection).document(data["user_id_hash"])

        try:
            if data_type == "photo":
                doc_ref.set({
                    'photo_date': data["date"],
                    'user_id_hash': data["user_id_hash"],
                    'photo_timestamp_ms': data["timestamp_ms"],
                    'file_id': data["file_id"],
                    'file_unique_id': data["file_unique_id"],
                    'fs_state': 1
                },merge=True)
            elif data_type == "location":
                doc_ref.set({
                    'location_date': data["date"],
                    'user_id_hash': data["user_id_hash"],
                    'location_timestamp_ms': data["timestamp_ms"],
                    'lat_long': str(data["latitude"])+","+str(data["longitude"]),
                },merge=True)
            elif data_type == "generated":
                doc_ref.set({
                    'photo_date': data["photo_date"],
                    'user_id_hash': data["user_id_hash"],
                    'photo_timestamp_ms': data["photo_timestamp_ms"],
                    'file_id': data["file_id"],
                    'file_unique_id': data["file_unique_id"],
                    'fs_state': 2,
                    'location_date': data["location_date"],
                    'location_timestamp_ms': data["location_timestamp_ms"],
                    'lat_long': data['lat_long'],
                    'is_flood': data['is_flood'],
                    'water_level': data['water_level'],
                    'water_level_case': data['water_level_case'],
                },merge=True)
            else:
                print(f"data_type not recognized {data_type}")
        except:
            print("Failed to upload. Data:",data)
    
    def get_documents(self,collection):
        
        # Create a reference to the bot data
        bot_data_ref = self.db.collection(collection)

        try:
            bot_data_ref = bot_data_ref.where(u'fs_state', u'==', 2)
            
        except Exception as e:
            print("Failed on getting documents\n",e)
            return None

        docs = bot_data_ref.stream()

        # for doc in docs:
        #     print(f'{doc.id} => {doc.to_dict()}')
        
        return docs
    
    def set_sent_to_bq_fs_state(self, collection, doc_ids):

        for doc_id in doc_ids:
            doc_ref = self.db.collection(collection).document(doc_id)

            doc_ref.set({
                'fs_state': 3
            },merge=True)
    
    def delete_documents(self, collection, doc_ids):

        for doc_id in doc_ids:
            doc_ref = self.db.collection(collection).document(doc_id)

            doc_ref.delete()
        
