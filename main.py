import json
import requests
import logging
import traceback

from flask import Flask, make_response
from base64 import b64decode

from telebot import TeleBot
from Crypto.Cipher import AES

secret = "dubalalba"
token = "1236037835:AAGQQ7l9F3TJG7oVTEcCWcfqSl4HXdldI0c"

app = Flask(__name__)
bot = TeleBot(token, threaded=False)

neil_id = 295932236
polinas_id = 387561850
chat_id = -1002172216118
valyas_id = 706265979
admins = [neil_id,] #, polinas_id, valyas_id]


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


def notify_admins(message: str):
    global bot
    try:
        for uid in admins:
            if len(message) < 2049:
                bot.send_message(uid, message)
            else:
                parts = [message[i:i+2048]  for i in range(0, len(message), 2048)]
                for part in parts:
                    bot.send_message(uid, part)
    except:
        print(f"Can't send message to {uid} due to internel problmz =(")


def notify_main_admin(message: str):
    global bot
    bot.send_message(neil_id, message)
    print(f"Can't send message to Meister Admin due to internel problmz =(")


def parse_response(response):
    message = response.text
    splitted_msg = message.split(":")

    text = b64decode(splitted_msg[0])
    iv = b64decode(splitted_msg[1])
    key = "87851f3bbdc755bf".encode("utf-8")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(text)

    decrypted_message = decrypted.rstrip(b"\x00")

    decrypted_message_str = decrypted_message.decode("utf-8")
    back = decrypted_message_str[-1]
    decoded_response = json.loads(decrypted_message_str.strip(back))

    try:
        assert len(decoded_response["Seances"]["Content"][0]) == 0
    except:
        msg = "БЛЭТ ЧЕКНИ АФИШУ КАЖЕТСЯ ПОРА ЗАКУПАСА - https://iframeab-pre6751.intickets.ru !!!"
        notify_admins(msg)
        notify_main_admin(str[decoded_response["Seances"]["Content"][0][0]])


@app.route("/{}".format(secret), methods=["GET"])
def check_intickets():
    try:
        response = requests.post(
            "https://api.intickets.ru/next/v2/?XDEBUG_SESSION_START&SESSI5d68f4e67c6f105b677163d3d95d137d=4ncaovttbk6mt3afiroudkvq5m",
            headers=headers,
            data=data,
        )
        content = parse_response(response)
        notify_main_admin(content[:4096])
    except json.JSONDecodeError as parse_error:
        msg = "На сайте появились какие-то данные, которые я не смог обработать... посмотри плез =/\n https://iframeab-pre6751.intickets.ru"
        notify_main_admin(msg)
        notify_main_admin(traceback.format_stack())
    except requests.RequestException:
        msg = "Не могу обратиться к сайту... чекни сам пж\n https://iframeab-pre6751.intickets.ru"
        notify_main_admin(msg)
    except Exception as e:
        print(e)

    return make_response("ok", 200)


@app.route("/is_working", methods=["GET"])
def is_working():
    msg = "ok"
    notify_main_admin(msg)
    return make_response(msg, 200)


notify_main_admin("Im ready!")
app.run(host="0.0.0.0", port=443, debug=False)
