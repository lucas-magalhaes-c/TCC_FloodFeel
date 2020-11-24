
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
        query = downloaded_blob.decode("utf-8") 
    
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