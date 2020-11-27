
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import os
import sys
import json
import io


class FloodFeel_Keyboards():

    def __init__(self,callback_data=None,message=None):
        self.callback_data = callback_data
        self.message_text = None
        self.has_location = False
        self.is_photo = False
        self.photo_to_send = None

        if message != None and "location" in message:
            self.has_location = True
        
        if message != None and "photo" in message:
            self.is_photo = True
        
        if message != None and "text" in message:
            self.message_text = message["text"]

        if self.callback_data == None and self.message_text == None and self.has_location == False and self.is_photo == False:
            print("Failed to get callback data or message text")
    
    def _start_long(self):
        self.text = "Olá, seja bem vindo(a) ao EnchentesBot! 🤖\nAqui você será informado(a) sobre os pontos de enchente na cidade de São Paulo e poderá contribuir informando novos locais de enchente.\n\nO que deseja fazer?"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Consultar enchentes em São Paulo", callback_data='start_opt_1')],
            [InlineKeyboardButton(text="Inserir novo foco de enchente", callback_data='start_opt_2')],
            [InlineKeyboardButton(text="Cadastrar", callback_data='start_opt_3')],
            [InlineKeyboardButton(text="Compartilhar", callback_data='start_opt_4')]
        ])
    
    def _start_short(self):
        self.text = "Olá! O que deseja fazer? Por favor escolha um dos botões abaixo"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Consultar enchentes em São Paulo", callback_data='start_opt_1')],
            [InlineKeyboardButton(text="Inserir novo foco de enchente", callback_data='start_opt_2')],
            [InlineKeyboardButton(text="Cadastrar", callback_data='start_opt_3')],
            [InlineKeyboardButton(text="Compartilhar", callback_data='start_opt_4')]
        ])

    def _start_opt_1(self):

        self.text = "Escolha uma região de São Paulo para consultar"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Centro", callback_data='start_opt_1_1-SPCE')],
            [InlineKeyboardButton(text="Zona Norte", callback_data='start_opt_1_1-SPZN')],
            [InlineKeyboardButton(text="Zona Sul", callback_data='start_opt_1_1-SPZS')],
            [InlineKeyboardButton(text="Zona Leste", callback_data='start_opt_1_1-SPZL')],
            [InlineKeyboardButton(text="Zona Oeste", callback_data='start_opt_1_1-SPZO')],
            [InlineKeyboardButton(text="Todas as regiões", callback_data='start_opt_1_1-SP')],
            [InlineKeyboardButton(text="Voltar ao inicio", callback_data='start_short')]
        ])

    def _start_opt_1_1(self):
        zone_id = self.callback_data.split("-")[1] # gets the zone part of start_opt_1_1-<zone>

        config = json.loads(open("bot_config_local.json").read()) if "-local" in sys.argv else json.loads(open("bot_config.json").read())

        SH = StorageHandler(config["storage_bucket_name"])
        image = SH.get_image(f"sao_paulo/{config['maps_zone_ids'][zone_id]}.jpg")
        
        # with open(f'download_test.jpg', 'wb') as f:
        #     f.write(image)

        self.photo_to_send = io.BytesIO(image)

        self.text = f"Olhe o estado atual das enchentes nessa região. Se possível, evite passar pelas regiões afetadas, para sua segurança :)"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Voltar ao inicio", callback_data='start_short')],
        ])
    
    def _start_opt_2(self):
        self.text = "Você está no local da enchente?"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Sim", callback_data='start_opt_2_1')],
            [InlineKeyboardButton(text="Não", callback_data='start_opt_2_2')]
        ])
    
    def _start_opt_2_1(self):
        self.text = "Por favor, compartilhe a localização para sabermos o local da enchente"
        print("onetime")
        self.keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(text="Enviar localização", callback_data='start_opt_2_1_1',request_location=True)],
            [KeyboardButton(text="Cancelar", callback_data='start_short')]
        ],one_time_keyboard=True)
    
    def _start_opt_2_1_1(self):
        self.text = "Localização recebida! \n\nAgora por favor nos envie uma foto da enchente. Tente mostrar bem a situação.\n\nCaso não seja possível, você pode cancelar o envio"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Cancelar envio", callback_data='start_short')]
        ])
    
    def _start_opt_2_1_1_1(self):
        self.text = "Foto recebida! Conseguiria nos indicar a gravidade da enchente informando o nível da água conforme indicado na imagem?"

        config = json.loads(open("bot_config_local.json").read()) if "-local" in sys.argv else json.loads(open("bot_config.json").read())
        SH = StorageHandler(config["storage_bucket_name"])
        image = SH.get_image("gravidade/gravidade_EnchentesBot.jpg")

        self.photo_to_send = io.BytesIO(image)
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="1- Água abaixo da linha verde", callback_data='start_opt_2_1_1_1_1-1')],
            [InlineKeyboardButton(text="2- Entre as linhas verde e amarela", callback_data='start_opt_2_1_1_1_1-2')],
            [InlineKeyboardButton(text="3- Entre as linhas amarela e vermelha", callback_data='start_opt_2_1_1_1_1-3')],
            [InlineKeyboardButton(text="4- Acima da linha vermelha", callback_data='start_opt_2_1_1_1_1-4')],
            [InlineKeyboardButton(text="Não sei informar", callback_data='start_opt_2_1_1_1_1-0')]
        ])
    
    def _start_opt_2_1_1_1_1(self):
        self.text = "Muito obrigado por contribuir! \n\nJuntos somos mais fortes para atenuar os efeitos das enchentes 😊"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Voltar ao inicio", callback_data='start_short')]
        ])
    
    def _start_opt_2_2(self):
        self.text = "Desculpa, é necessário que você esteja no local da enchente para inserir um novo foco.\n\nCaso tenha errado e esteja no local, inicie novamente o envio"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Voltar ao inicio", callback_data='start_short')]
        ])
    
    def _failed(self):
        self.text = "Perdão, não entendi o seu pedido. Use os botões que aparecem para navegar."
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Voltar ao inicio", callback_data='start_short')]
        ])

    def get_reply(self,custom=None):
        switcher = {
            "start_long": self._start_long,
            "start_short": self._start_short,
            "start_opt_1": self._start_opt_1,
            "start_opt_1_1": self._start_opt_1_1,
            "start_opt_2": self._start_opt_2,
            "start_opt_2_1": self._start_opt_2_1,
            "start_opt_2_1_1": self._start_opt_2_1_1,
            "start_opt_2_1_1_1": self._start_opt_2_1_1_1,
            "start_opt_2_1_1_1_1": self._start_opt_2_1_1_1_1,
            "start_opt_2_2": self._start_opt_2_2,
            "start_opt_3": None,
            "start_opt_4": None,
            "failed": self._failed
        }

        if self.callback_data != None:
            if "start_opt_1_1" in self.callback_data:
                chosen_keyboard_func = switcher["start_opt_1_1"]
            elif "start_opt_2_1_1_1_1" in self.callback_data:
                chosen_keyboard_func = switcher["start_opt_2_1_1_1_1"]
            else:
                # Get the function from switcher dictionary
                chosen_keyboard_func = switcher.get(self.callback_data, lambda: "Invalid callback data")
        elif self.message_text == "/start":
            chosen_keyboard_func = switcher.get("start_long", lambda: "Invalid keyboard function 1")
        elif self.has_location == True:
            chosen_keyboard_func = switcher.get("start_opt_2_1_1", lambda: "Invalid keyboard function 2")
        elif self.is_photo == True:
            chosen_keyboard_func = switcher.get("start_opt_2_1_1_1", lambda: "Invalid keyboard function 3")
        else:
            chosen_keyboard_func = switcher.get("start_short", lambda: "Invalid keyboard function 4")
        
        if chosen_keyboard_func is not None:
            # executes the method defined from switcher
            chosen_keyboard_func()

            try:
                return self.text, self.keyboard, self.photo_to_send
            except:
                print("Failed on getting keyboard. ")
                self._failed()
                return self.text, self.keyboard, self.photo_to_send
        
        else:
            print("Failed on getting keyboard, method is None")
            self._failed()
            return self.text, self.keyboard


import hashlib
def hashText(text,salt=None):
    """
        Basic hashing function for a text
            text -> Str
            salt -> (optional) Str   
    """
    if salt != None:
        return hashlib.sha256(salt.encode() + text.encode()).hexdigest()
    else:
        return hashlib.sha256(text.encode()).hexdigest()


from datetime import datetime
import time 
date = datetime.today().strftime('%Y-%m-%d')
timestamp_ms = round(time.time() * 1000)

class MessageHandle():
    def __init__(self,request_json,config):
        self.location = None
        self.photo_data = None
        self.message_text = None
        self.message = None
        self.callback_data = None
        self.data_to_store = {}
        self.data_type = None
        self.hash_salt = config["hash_salt"]
        self.water_level = None
        self.water_level_case = None

        try:
            request_json["callback_query"]
            self.is_callback_query = True
        except: 
            self.is_callback_query = False

        self.bot_id = config["bot_id"]
        self.bot_name = config["bot_name"]

        # configure from request json
        self._configure(request_json)

        # check if request is valid
        self._validate()

        # configure data to be inserted on Big Query
        if self.location != None or self.photo_data != None or self.water_level != None:
            self._configure_data_to_store()

    def get_reply_keyboard(self):
        FFKeyboards = FloodFeel_Keyboards(callback_data=self.callback_data,message=self.message)
        
        return FFKeyboards.get_reply()

    def _configure(self,request_json):
        message = None

        if self.is_callback_query == True:
            message = request_json["callback_query"]["message"]
            
            try:
                self.callback_data = request_json["callback_query"]["data"]

                # water level info
                if "start_opt_2_1_1_1_1" in self.callback_data:
                    
                    self.water_level = int(self.callback_data.split("-")[1])
                    if self.water_level == 0:
                        self.water_level_case = "Não soube informar"
                    else:
                        self.water_level_case = f"Nível {str(self.water_level)}"
            except:
                self.callback_data = None
                print("Failed to configure requested callback")
        else: 
            message = request_json["message"]
            self.message = message
            try:
                self.message_text = request_json["message"]["text"]
            except:
                self.message_text = None

        # chat info
        try:
            self.chat = message["chat"]
        except:
            print("Failed on extracting chat")
            self.chat = None
        
        # request from info
        try:
            self.request_from = message["from"]
        except:
            print("Failed on extracting request from data")
            self.request_from = None

        # geolocation info
        if "location" in message:
            self.location = message["location"]

        # photo info
        if "photo" in message:
            self.photo_data = message["photo"]
        
    def _validate(self):
        if self.is_callback_query:
            try:
                if self.bot_id == self.request_from["id"] and self.bot_name == self.request_from["first_name"]:
                    self.is_valid = True
                else:
                    self.is_valid = False
                    print("Failed on validation: bot id doesnt match")
            except:
                print("Failed on callback query validation")
        else:
            if self.request_from["is_bot"] == True:
                self.is_valid = False
                print("Failed: request from bot")
            else:
                self.is_valid = True
            
    def get_user_id(self):
        return self.chat["id"]
    
    def get_username(self):
        return self.chat["first_name"]

    def _configure_data_to_store(self):
        self.data_to_store["user_id_hash"] = hashText(text=str(self.get_user_id()), salt=self.hash_salt)

        if self.location != None:
            self.data_to_store["date"] = date
            self.data_to_store["timestamp_ms"] = timestamp_ms

            # type of data to be uploaded
            self.data_type = "location"

            self.data_to_store["latitude"] = self.location["latitude"]
            self.data_to_store["longitude"] = self.location["longitude"]

        elif self.photo_data != None:
            self.data_to_store["date"] = date
            self.data_to_store["timestamp_ms"] = timestamp_ms

            # type of data to be uploaded
            self.data_type = "photo"

            # pick the best quality photo in the list (the last element is the best)
            best_photo = self.photo_data[-1]

            self.data_to_store["file_id"] = best_photo["file_id"]
            self.data_to_store["file_unique_id"] = best_photo["file_unique_id"]

        elif self.water_level != None:

            # type of data to be uploaded
            self.data_type = "water_level"

            self.data_to_store["water_level"] = self.water_level
            self.data_to_store["water_level_case"] = self.water_level_case

    
    def infos(self):
        print(" **** INFOS ****\nchat_id:",self.chat["id"],"\nfirst_name:",self.chat["first_name"],"\nis_callback:",
        self.callback_data != None,"\nis_location:",self.location != None,"\nis_photo:",self.photo_data != None)

    
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
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
            'projectId': project_id,
            })

            self.db = firestore.client()
        else:
            # Testing locally
            # Use a service account
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)

            self.db = firestore.client()
    
    def add_document_to_collection(self,collection,data,data_type):

        doc_ref = self.db.collection(collection).document(data["user_id_hash"])

        if data_type == "photo":
            doc_ref.set({
                'photo_date': data["date"],
                'user_id_hash': data["user_id_hash"],
                'photo_timestamp_ms': data["timestamp_ms"],
                'file_id': data["file_id"],
                'file_unique_id': data["file_unique_id"]
            },merge=True)
        elif data_type == "location":
            doc_ref.set({
                'location_date': data["date"],
                'user_id_hash': data["user_id_hash"],
                'location_timestamp_ms': data["timestamp_ms"],
                'lat_long': str(data["latitude"])+","+str(data["longitude"]),
            },merge=True)
        elif data_type == "water_level":
            doc_ref.set({
                'water_level': data["water_level"],
                'water_level_case': data["water_level_case"],
                'fs_state': 1
            },merge=True)
        else:
            print(f"data_type not recognized {data_type}")
    
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
        
        
from google.cloud import storage

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

        return downloaded_blob
        # query = downloaded_blob.decode("utf-8") 
    
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