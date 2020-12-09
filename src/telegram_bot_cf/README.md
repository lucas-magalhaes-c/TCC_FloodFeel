# Telegram Bot

Este módulo é responsável por conter toda a lógica de operação do bot, para que funcione corretamente de forma serverless. 
Assim como o restante do projeto, ele foi desenvolvido em Python, na versão 3.8.

Caso não saiba instanciar uma Cloud Function, esse tutorial do Google pode ser seguido: [Cloud Functions Quickstart](https://cloud.google.com/functions/docs/quickstart)

## Funcionamento

O arquivo principal é o main.py, que receberá o request. Nele é inciado o MessageHandle, objeto que extrai os conteúdos da mensagem, verifica se há dados para enviar para o Firestore e avalia se a mensagem é válida. Caso seja e existam dados para serem enviados para o Firestore, o objeto FirestoreHandler é instanciado para realizar o envio.

Após isso, é definida a resposta adequada a ser enviada para o usuário, com base no dado recebido anteriormente. Para isso o MessageHandler obtém o reply keyboard adequado, utilizando o objeto FloodFeel_Keyboards, que contém todas as respostas que o bot é capaz de retornar. Por fim, a mensagem de resposta é enviada.

O MessageHandler, o FirestoreHandler e o FloodFeel_Keyboard estão presentes no arquivo **utils.py**.

## Modo de teste

Para executar o modo de teste localmente basta utilizar a flag **-local**
```py
python3 main.py -local
```
Esse modo aceita um arquivo json como payload, simulando um recebimento de dado pelo bot do Telegram. Um exemplo pode ser observado em **debug/payload_example.json**. Para adquirir um novo payload, basta instanciar a Cloud Function e imprimir o corpo inteiro de uma mensagem obtida (basicamente descomente o trecho **print(request_json)** na função main, envie alguma solicitação pelo bot e veja o log da cloud function - o payload estará lá para ser copiado).

Para executar outras mensagens, basta adicionar novos arquivos json na pasta debug com payloads distintos. Sugestão de payloads a serem testados:
* callback
* location
* photo

Para executar outros payloads, basta adicionar -payload <nome_do_arquivo> na execução da função. Abaixo, um exemplo para o payload callback, que acessa o arquivo payload_callback.json:
```py
python3 main.py -local -payload callback
```

## Arquivo bot_config.json

Os dados sensíveis da aplicação estão contidos nesse arquivo. O significado de cada campo será apresentado a seguir:
* **bot_name** - É o nome do bot escolhido ao criá-lo utilizando o BotFather.
* **bot_id** - É o identificador do bot nos servidores do Telegram. O bot token contém o bot_id, é a primeira parte antes dos dois pontos (bot_token = <bot_id>:<bot_hash>).
* **bot_token** - Para obter o token do bot criado basta enviar o comando /mybots para o BotFather, selecionar o bot e clicar no botão API Token.
* **hash_salt** - É uma string utilizada como sal ao calcular a hash do user_id para salvar no servidor. Dessa forma, não é guardado o user_id para preservar a privacidade do usuário e ainda é possível descobrir se um novo foco de enchente foi inserido por um mesmo usuário, no banco de dados.
* **setTelegramWebhook_url** - Como indicado no README do projeto, é o link para ativar o Weebhook na cloud funcion do bot.
* **getFilePath_url** - Serve para obter a localização de uma foto (path da foto) enviada ao servidor do Telegram [Não é usado por esse módulo].
* **getFile_url** - Serve para realizar o download de uma foto enviada ao servidor do Telegram [Não é usado por esse módulo].
* **storage_bucket_name** - É o nome do bucket no Google Storage onde os mapas gerados pelo Maps Static API estão armazenados.
* **maps_zone_ids** - Contém o nome das imagens que representam cada região.
* **dashboard_url** - URL do dashboard, apresentada na função "Acessar dashboard".

Para realizar debugs locais basta criar um arquivo chamado **bot_config_local.json** com as informações do bot. Observe que ao fazer o deploy da função, deve-se colocar as informações no arquivo bot_config.json.

## Arquivo service_account.json

Esse arquivo representa as credenciais que a Cloud Function irá utilizar para acessar os serviços presentes na GCP. Para isso é necessário criar uma *service account* na aba **IAM & Admin** com as seguintes funções: 
* BigQuery Admin
* BigQuery Data Editor
* Cloud Functions Invoker
* Cloud Scheduler Admin
* Firebase Admin SDK Administrator Service Agent

Essa *service account* poderá ser usada para os demais módulos enquanto os testes estiverem sendo feitos, porém recomenda-se utilizar uma service_account diferente para cada módulo, para garantir apenas as funções necessárias que cada módulo precisa para operar. Assim a implementação estará mais segura.

## Arquivo requirements.txt

Basicamente esse arquivo é necessário para indicar à Cloud Function todas as dependências que são necessárias para que ela funcione. No caso do Telegram Bot, as seguintes bibliotecas são utilizadas, juntamente com suas versões:
* requests==2.24.0
* python-telegram-bot==13.0
* firebase-admin==4.4.0
* google-cloud-bigquery==2.2.0
* google-cloud-firestore==1.9.0
* google-cloud-storage==1.32.0
