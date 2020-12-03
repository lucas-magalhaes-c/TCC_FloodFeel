# Telegram Bot

Este módulo é responsável por conter toda a lógica de operação do bot, para que funcione corretamente de forma serverless. 
Assim como o restante do projeto, ele foi desenvolvido em Python, na versão 3.8.

# Arquivo bot_config.json

Os dados sensíveis da aplicação estão contidos nesse arquivo. O significado de cada campo será apresentado a seguir:
* bot_name - É o nome do bot escolhido ao criá-lo utilizando o BotFather.
* bot_id - É o identificador do bot nos servidores do Telegram. Quando o Weebhook for feito e estiver funcionando corretamente, basta receber um payload vindo de uma função de callback (todos os botões que o bot apresenta para ser clicado retorna uma função de callback) e encontrar o bot_id nele.
* bot_token - Para obter o token do bot criado basta enviar o comando /mybots para o BotFather, selecionar o bot e clicar no botão API Token.
* hash_salt - É uma string utilizada como sal ao calcular a hash do user_id para salvar no servidor. Dessa forma, não é guardado o user_id para preservar a privacidade do usuário e ainda é possível descobrir se um novo foco de enchente foi inserido por um mesmo usuário, no banco de dados.
* setTelegramWebhook_url - Como indicado no README do projeto, é o link para ativar o Weebhook na cloud funcion do bot.
* getFilePath_url - Serve para obter a localização de uma foto (path da foto) enviada ao servidor do Telegram [Não é usado por esse módulo]
* getFile_url - Serve para realizar o download de uma foto enviada ao servidor do Telegram [Não é usado por esse módulo]
* storage_bucket_name - É o nome do bucket no Google Storage onde os mapas gerados pelo Maps Static API estão armazenados.
* maps_zone_ids - Contém o nome das imagens que representam cada região
* dashboard_url - URL do dashboard, apresentada na função "Acessar dashboard"

