import json
import requests
import logging
import traceback

from flask import Flask, make_response
from base64 import b64decode, b64encode

from telebot import TeleBot
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

secret = "dubalalba"
token = "1236037835:AAGQQ7l9F3TJG7oVTEcCWcfqSl4HXdldI0c"

app = Flask(__name__)
bot = TeleBot(token, threaded=False)

neil_id = 295932236
polinas_id = 387561850
chat_id = -1002172216118
valyas_id = 706265979
admins = [
    neil_id,
]  # , polinas_id, valyas_id]


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
    'x-client-version': '4.3.97',
    "x-frame-origin": "iframeab-pre6751.intickets.ru",
}

data = 'Nkf7/ED1KdfAy5RGPHoEJmUAyPbizpywhEfAEwVLyeh5SiMtoRZfDyrrmdZWlZJE:QmhBbERvMHBhS1E4M0p0cQ=='


def notify_admins(message: str):
    global bot
    try:
        for uid in admins:
            if len(message) < 2049:
                bot.send_message(uid, message)
            else:
                parts = [message[i : i + 2048] for i in range(0, len(message), 2048)]
                for part in parts:
                    bot.send_message(uid, part)
    except Exception as ex:
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
    print(decoded_response)

    try:
        assert len(decoded_response["Seances"]["Content"][0]) == 0
    except:
        msg = "БЛЭТ ЧЕКНИ АФИШУ КАЖЕТСЯ ПОРА ЗАКУПАСА - https://iframeab-pre6751.intickets.ru !!!"
        notify_admins(msg)
        notify_main_admin(str(decoded_response["Seances"]["Content"]))
    return decoded_response

def generate_message(response):
    response_str = json.dumps(response)

    key = "87851f3bbdc755bf".encode("utf-8")
    iv = get_random_bytes(16)

    pad_len = AES.block_size - (len(response_str) % AES.block_size)
    pad_char = chr(pad_len)
    padded_response = response_str + pad_char * pad_len

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_text = cipher.encrypt(padded_response.encode('utf-8'))

    encoded_encrypted_text = b64encode(encrypted_text).decode('utf-8')
    encoded_iv = b64encode(iv).decode('utf-8')
    encrypted_message = f"{encoded_encrypted_text}:{encoded_iv}"

    return encrypted_message

@app.route("/{}".format(secret), methods=["GET"])
def check_intickets():
    try:
        response = requests.post(
            "https://api.intickets.ru/next/v2/?XDEBUG_SESSION_START&SESSI5d68f4e67c6f105b677163d3d95d137d=4ncaovttbk6mt3afiroudkvq5m",
            headers=headers,
            data=data,
        )
        parse_response(response)
    except json.JSONDecodeError as parse_error:
        msg = "На сайте появились какие-то данные, которые я не смог обработать... посмотри плез =/\n https://iframeab-pre6751.intickets.ru"
        notify_main_admin(msg)
        notify_main_admin(parse_error)
    except requests.RequestException as request_exception:
        msg = "Не могу обратиться к сайту... чекни сам пж\n https://iframeab-pre6751.intickets.ru"
        notify_main_admin(msg)
        notify_main_admin(request_exception)
    except Exception as exception:
        notify_main_admin(exception)

    return make_response("ok", 200)


@app.route("/is_working", methods=["GET"])
def is_working():
    msg = "ok"
    notify_main_admin(msg)
    return make_response(msg, 200)


notify_main_admin("Im ready!")
app.run(host="0.0.0.0", port=443, debug=False)
