# TCC - FloodFeel

## Setup Google Cloud

É necessário criar um novo projeto na Google Cloud Platform. Para o bot do Telegram funcionar serveless, foi escolhido fazer o deploy do mesmo por meio de uma Cloud Funcion. Para ativar as Cloud Functions, o seguinte tutorial pode ser seguido: 
[Cloud functions Quickstart](https://cloud.google.com/functions/docs/quickstart)

## Criação do bot do Telegram

Para criar um bot no Telegram basta iniciar uma conversa com o BotFather e registrar um novo bot pelo comando \newbot.

## Setup do Webhook

Existem duas formas de obter novas mensagens que foram feitas para o bot: por meio do pooling de mensagens (perguntar para o Telegram se chegaram novas mensagens) ou recebendo a mensagem automaticamente quando ela for feita. Para isso, é necessário informar uma URL aos servidores do Telegram para que ele poste mensagens novas sempre que estas chegarem. Esse método é chamado de Webhook e para configurá-lo, de forma simples, basta acessar a url abaixo por qualquer navegador:

```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=<CLOUD_FUNCTION_URL>

Em que:
1. <TOKEN> é o token bot do Telegram.
2. <CLOUD_FUNCTION_URL> é a URL da Cloud Function que contém o bot
```
