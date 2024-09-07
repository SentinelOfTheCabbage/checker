#pylint: disable=C0111, W0401,W0614
import json
import requests
import logging

from flask import Flask, make_response
from base64 import b64decode

from telebot        import TeleBot, logger
from Crypto.Cipher import AES

secret = "dubalalba"
logger.setLevel(logging.INFO)
app = Flask(__name__)
logging.info("service started")
token = "1236037835:AAGQQ7l9F3TJG7oVTEcCWcfqSl4HXdldI0c"
bot = TeleBot(token, threaded=False)
# admins = [-1002172216118]
admins = [295932236, ] #,231858927,332410475]


headers = {
    "accept": "application/json",
    "accept-language": "ru-RU",
    "content-type": "application/json",
    "origin": "https://iframeab-pre6751.intickets.ru",
    "priority": "u=1, i",
    "referer": "https://iframeab-pre6751.intickets.ru/",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "YaBrowser";v="24.7", "Yowser";v="2.5"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36",
    "x-client-version": "4.3.74",
    "x-frame-origin": "iframeab-pre6751.intickets.ru",
}

data = "oiCavGZiwJHW4FWN9haMEs/7n7Ou+lSs1cDFkSA5w4lgmR8YgrvjCyPQmkRSF53b:RlJ4bENqenNtODE2TVZEVA=="


def notify_admins(bot: TeleBot, message: str):
    try:
        for uid in admins:
            bot.send_message(uid, message)
    except:
        print(f"Can't send message to {uid} due to internel problmz =(")

def parse_response(response):
    message = response.text
    splitted_msg = message.split(":")

    text = b64decode(splitted_msg[0])
    iv = b64decode(splitted_msg[1])
    key = "6f8b30a279b55406".encode("utf-8")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(text)

    decrypted_message = decrypted.rstrip(b"\x00")

    decrypted_message_str = decrypted_message.decode("utf-8")
    decoded_response = json.loads(decrypted_message_str.strip("\x03"))
    try:
        assert len(decoded_response["Seances"]["Content"][0]) == 0
    except:
        msg = "БЛЭТ ЧЕКНИ АФИШУ КАЖЕТСЯ ПОРА ЗАКУПАСА - https://iframeab-pre6751.intickets.ru !!!"
        notify_admins(bot, msg)
        print(msg)

@app.route('/{}'.format(secret), methods=["GET"])
def webhook():
    try:
        response = requests.post(
            "https://api.intickets.ru/next/v2/?XDEBUG_SESSION_START&SESSI5d68f4e67c6f105b677163d3d95d137d=4ncaovttbk6mt3afiroudkvq5m",
            headers=headers,
            data=data,
        )
        parse_response(response)
    except Exception as ex:
        msg = "Чот сломалось, дядь =("
        notify_admins(bot, msg)
        print(msg, ex)

    return make_response("ok", 200)


app.run(port=443, debug=False)
