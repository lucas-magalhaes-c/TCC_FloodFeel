
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


from datetime import datetime
from google.cloud import bigquery
import google.auth
import json

# https://cloud.google.com/bigquery/docs/loading-data-local

class BigQueryHandler():
    def __init__(self, config):
        self.bq_project = config["bq_project"]
        self.dataset_id =  self.bq_project["dataset_id"]
        self.table_id_patterns = self.bq_project["table_id_patterns"]

        service_account_path = 'service_account_local.json' if "-local" in sys.argv else 'service_account.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

        # open and load service account & project id
        sa_file = open(service_account_path)
        sa_json = json.loads(sa_file.read())
        self.project_id = sa_json['project_id']

        # Both APIs must be enabled for your project before running this code.
        # credentials, project = google.auth.default(
        #         scopes=[
        #             "https://www.googleapis.com/auth/bigquery",
        #         ]
        # )

        # Create a client
        self.client = bigquery.Client.from_service_account_json(service_account_path)
        # self.client = bigquery.Client(credentials=credentials, project=project_id)
    
    def get_latlong(self,table_date):
        dateYYYYMMDD = table_date.replace("-","")

        table_full_path = self.project_id+"."+self.dataset_id+"."+self.table_id_patterns["bot_data_fs"] + dateYYYYMMDD

        # Check if table exists
        try:
            table_exists = self.client.get_table(table_full_path)
        except:
            # Table doesnt exist, lets create it
            print("No flood detected at São Paulo")
            return []

        query = f"""
            SELECT lat_long
            FROM `{table_full_path}`
            WHERE is_flood = True
            GROUP BY lat_long
        """

        query_job = self.client.query(query)  # Make an API request.

        lat_long_list = []
        for row in query_job:
            # Row values can be accessed by field name or index.
            lat_long_list.append(row["lat_long"]) # also can use row[0]
        
        return lat_long_list

    def insert_data(self, data, table_type, table_date):
        
        dateYYYYMMDD = table_date.replace("-","")

        # Table id in the format TABLE_YYYYMMDD
        self.table_id = self.table_id_patterns[table_type] + dateYYYYMMDD

        table_full_path = self.project_id+"."+self.dataset_id+"."+self.table_id

        # Check if table already exists
        try:
            table_exists = self.client.get_table(table_full_path)
        except:
            # Table doesnt exist, lets create it

            schema = self._getSchema(table_type)

            new_table = bigquery.Table(table_full_path, schema=schema)
            new_table = self.client.create_table(new_table)  # Make an API request.
        
        if type(data) is not list: 
            data_aux = data
            data = []
            data.append(data_aux)

        try:
            status = self.client.insert_rows_json(table=table_full_path, json_rows=data) # Make an API request.
            if len(status) == 0:
                return True
            else:
                try:
                    print("One or more errors happened")
                    for item in status:
                        errors = item["errors"]
                        for error in errors:
                            print(f'Reason: {error["reason"]}, issue: {error["message"]}')
                except:
                    print("Failed in showing all the errors")
                return False
        except Exception as e:
            print("Failed to insert data into BigQuery\n",e)
            return False
    
    def _getSchema(self,table_type):
        if table_type == "bot_data_fs":
            return [
                bigquery.SchemaField("location_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("user_id_hash", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("location_timestamp_ms", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("lat_long", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("photo_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("photo_timestamp_ms", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("is_flood", "BOOLEAN", mode="REQUIRED")
            ]
        else:
            print("Schema not found for the table type")
            None