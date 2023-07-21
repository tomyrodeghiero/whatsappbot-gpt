import os
from flask import Flask, request
import openai
import sett
import services

app = Flask(__name__)


@app.route('/welcome', methods=['GET'])
def welcome():
    return 'Hi! Run API from Flask'


@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e, 403


@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        body = request.get_json()
        print("body", body)
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = replace_start(str(message['from']))
        messageId = message['id']
        timestamp = int(message['timestamp'])
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)
        print('mensaje usuario: ', text)
        # services.administrar_chatbot(text, number,messageId,name)

        if 'es todo' in text:
            services.guardar_conversacion(
                messageId, number, name, text, timestamp, 'pedido realizado')
            jsonPedido = services.generar_respuesta_chatgpt(text, number, True)
            services.guardar_pedido(jsonPedido, number)
            data = services.text_Message(number, 'Pedido Confirmado, gracias!')
        else:
            respuestabot = services.generar_respuesta_chatgpt(
                text, number, False)
            services.guardar_conversacion(
                messageId, number, name, text, timestamp, respuestabot)
            data = services.text_Message(number, respuestabot)

            print("DATASA", data)
            services.enviar_Mensaje_whatsapp(data)
        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)


def replace_start(s):
    if s.startswith("549"):
        return "54" + s[3:]
    else:
        return s


if __name__ == '__main__':
    app.run(port=7000)
