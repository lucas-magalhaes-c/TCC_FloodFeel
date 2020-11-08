
import os
import sys
import json

from datetime import datetime
from google.cloud import bigquery
import google.auth

# https://cloud.google.com/bigquery/docs/loading-data-local

class BigQueryHandler():
    def __init__(self, config):
        self.bq_project = config["bq_project"]
        self.dataset_id =  self.bq_project["dataset_id"]
        self.table_id_patterns = self.bq_project["table_id_patterns"]

        service_account_path = 'service_account.json'
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
    
    def insert_data(self, data, table_type):
        dateYYYYMMDD = datetime.today().strftime('%Y%m%d')

        # Table id in the format TABLE_YYYYMMDD
        self.table_id = self.table_id_patterns[table_type] + "20201106"

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
            return True
        except Exception as e:
            print("Failed to insert data into BigQuery\n",e)
            return False


    def _get_query(self,data,table,mode):
        queries = self.bq_project["queries"]
        
        try:
            path = queries[table][mode]+'.sql'
        except:
            print("Failed on getting query path")
            return None

        if "-local" in sys.argv:
            path = "queries/" + path
        
        fd = open(path, 'r')
        query = fd.read()
        fd.close()

        # setup query for location data
        if table == "location":
            query = self._setup_location_query(query,data)
        elif table == "photo":
            query = self._setup_photo_query(query,data)

        return query
    
    def _setup_location_query(query,data):
        # query.replace
        #TODO
        return
    
    def _getSchema(self,table_type):
        if table_type == "bot_data_fs":
            return [
                bigquery.SchemaField("location_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("user_id_hash", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("location_timestamp_ms", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("latitude", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("longitude", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("photo_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("photo_timestamp_ms", "INTEGER", mode="REQUIRED"),
                bigquery.SchemaField("file_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("file_unique_id", "STRING", mode="REQUIRED")
            ]
        else:
            print("Schema not found for the table type")
            None
    
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



class FirestoreHandler():
    def __init__(self):
        service_account_path = 'service_account.json'

        # open and load service account & project id
        sa_file = open(service_account_path)
        sa_json = json.loads(sa_file.read())
        project_id = sa_json['project_id']

        if "-local" not in sys.argv:
            # Use the application default credentials, in GCP
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
            'projectId': project_id,
            })

            self.db = firestore.client()
        else:
            # Testing locally
            # Use a service account
            cred = credentials.Certificate('service_account.json')
            firebase_admin.initialize_app(cred)

            self.db = firestore.client()
    
    def add_document_to_collection(self,collection,data,data_type):
        # doc_ref = db.collection(u'users').document(u'alovelace')
        # doc_ref.set({
        #     u'first': u'Ada',
        #     u'last': u'Lovelace',
        #     u'born': 1815
        # })
        doc_ref = self.db.collection(collection).document(data["user_id_hash"])

        if data_type == "photo":
            doc_ref.set({
                'photo_date': data["date"],
                'user_id_hash': data["user_id_hash"],
                'photo_timestamp_ms': data["timestamp_ms"],
                'file_id': data["file_id"],
                'file_unique_id': data["file_unique_id"],
                'set_to_bq': False
            },merge=True)
        elif data_type == "location":
            doc_ref.set({
                'location_date': data["date"],
                'user_id_hash': data["user_id_hash"],
                'location_timestamp_ms': data["timestamp_ms"],
                'latitude': data["latitude"],
                'longitude': data["longitude"],
            },merge=True)
        else:
            print(f"data_type not recognized {data_type}")
    
    def get_documents(self,collection,field,operator,field_value,sent_to_bq=False):

        # Create a reference to the bot data
        bot_data_ref = self.db.collection(collection)

        try:
            bot_data_ref = bot_data_ref.where(u'sent_to_bq', "==", sent_to_bq)
            bot_data_ref = bot_data_ref.where(field, operator, field_value)
            
        except Exception as e:
            print("Failed on getting documents\n",e)
            return None

        docs = bot_data_ref.stream()

        # for doc in docs:
        #     print(f'{doc.id} => {doc.to_dict()}')
        
        return docs
        
