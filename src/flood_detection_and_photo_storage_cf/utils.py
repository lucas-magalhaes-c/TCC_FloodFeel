from google.cloud import storage
import os
import sys

class StorageHandler():

    def __init__(self, bucket_name):
        service_account_path = 'service_account_local.json' if "-local" in sys.argv else 'service_account.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
        
        # Instantiates a storage client
        self.storage_client = storage.Client()

        try:
            self.bucket = self.storage_client.get_bucket(bucket_name)
        except:
            print("Bucket not found. Try grant access to storage bucket for the service account")
            raise Exception("Bucket not found") 
    
    def get_image(self,file_path,type="jpg"):
        try:
            blob = self.bucket.get_blob(file_path)
        except:
            print("Blob not found. Verify bucket folder and filename")
            raise Exception("Blob not found") 

        downloaded_blob = blob.download_as_string()
        # query = downloaded_blob.decode("utf-8") 
        return downloaded_blob
    
    def upload_image(self,image_data,storage_file_path,img_type="jpg"):

        if img_type == "jpg":
            try:
                # Name of the object to be stored in the bucket
                blob = self.bucket.blob(storage_file_path+'.jpg')

                # Uploading string of text
                blob.upload_from_string(image_data)
            except Exception as e:
                print("Failed on image upload to Storage. Error:\n",e)
        else:
            print(f"Image type not recognized: {img_type}. File was not uploaded") 
        return


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

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
                    'file_unique_id': data["file_unique_id"]
                },merge=True)
                print("Photo data sent to fs")
            elif data_type == "location":
                doc_ref.set({
                    'location_date': data["date"],
                    'user_id_hash': data["user_id_hash"],
                    'location_timestamp_ms': data["timestamp_ms"],
                    'lat_long': str(data["latitude"])+","+str(data["longitude"]),
                },merge=True)
                print("Location data sent to fs")
            elif data_type == "water_level":
                doc_ref.set({
                    'water_level': data["water_level"],
                    'water_level_case': data["water_level_case"],
                    'fs_state': 1
                },merge=True)
                print("Water level data sent to fs")
            elif data_type == "flood_detection":
                doc_ref.set({
                    'is_flood': data["is_flood"],
                    'fs_state': 2
                },merge=True)
                print("Flood validation data sent to fs")
            else:
                print(f"data_type not recognized {data_type}")
        except:
            print("Failed to send data. Data:",data)
    
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
    
    def get_documents_waiting_for_flood_detection(self,collection):
        
        # Create a reference to the bot data
        bot_data_ref = self.db.collection(collection)

        try:
            bot_data_ref = bot_data_ref.where(u'fs_state', u'==', 1)
            
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