
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

class FloodFeel_Keyboards():

    def __init__(self,callback_data=None,message=None):
        self.callback_data = callback_data
        self.message_text = None
        self.has_location = False
        self.is_photo = False

        if "location" in message:
            self.has_location = True
        
        if "photo" in message:
            self.is_photo = True
        
        if "text" in message:
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
        self.text = "Olhe o estado atual das enchentes em São Paulo. Se possível, evite passar pelas regiões afetadas, para sua segurança :)"
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
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Enviar localização", callback_data='start_short',request_location=True)]
        ])
    
    def _start_opt_2_1_1(self):
        self.text = "Localização recebida! \n\nAgora por favor nos envie uma foto da enchente. Tente mostrar bem a situação.\n\nCaso não seja possível, você pode cancelar o envio"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Cancelar envio", callback_data='start_short')]
        ])
    
    def _start_opt_2_1_1_1(self):
        self.text = "Foto recebida, muito obrigado por contribuir! \n\nJuntos somos mais fortes para atenuar os efeitos das enchentes 😊"
        self.keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Cancelar envio", callback_data='start_short')]
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
            "start_opt_2": self._start_opt_2,
            "start_opt_2_1": self._start_opt_2_1,
            "start_opt_2_1_1": self._start_opt_2_1_1,
            "start_opt_2_1_1_1": self._start_opt_2_1_1_1,
            "start_opt_2_2": self._start_opt_2_2,
            "start_opt_3": None,
            "start_opt_4": None,
            "failed": self._failed
        }

        if self.callback_data != None:
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
                return self.text, self.keyboard
            except:
                print("Failed on getting keyboard. ")
                self._failed()
                return self.text, self.keyboard
        
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


 
 
