import hashlib
import json
import requests

from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

from flask import Flask, make_response
from telebot import TeleBot

secret = "dubalalba"
token = "1236037835:AAGQQ7l9F3TJG7oVTEcCWcfqSl4HXdldI0c"

app = Flask(__name__)
bot = TeleBot(token, threaded=False)
is_silent_mode = False

neil_id = 295932236
polinas_id = 387561850
chat_id = -1002172216118
valyas_id = 706265979

lovlya = -1002414641124

admins = [
    neil_id, lovlya
]


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
    "x-client-version": "4.3.97",
    "x-frame-origin": "iframeab-pre6751.intickets.ru",
}

data = "Nkf7/ED1KdfAy5RGPHoEJmUAyPbizpywhEfAEwVLyeh5SiMtoRZfDyrrmdZWlZJE:QmhBbERvMHBhS1E4M0p0cQ=="


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


def notify_main_admin(message: str, prioritized=False):
    global bot
    global is_silent_mode

    if not prioritized and is_silent_mode:
        return

    bot.send_message(neil_id, message)


def get_key(version: str):
    return hashlib.md5(version.encode()).hexdigest()[8:][:16].encode("utf-8")


def encrypt_request(request_body, version="4.3.97"):
    request_body_str = json.dumps(request_body)
    base_cipher_key = get_key(version)

    iv = get_random_bytes(16)

    cipher = AES.new(base_cipher_key, AES.MODE_CBC, iv)

    padded_request = pad(request_body_str.encode("utf-8"), AES.block_size)
    encrypted_text = cipher.encrypt(padded_request)

    encrypted_text_base64 = b64encode(encrypted_text).decode("utf-8")
    random_string_base64 = b64encode(iv).decode("utf-8")

    return f"{encrypted_text_base64}:{random_string_base64}"


def decrypt_response(response, version="4.3.97"):
    message = response.text
    splitted_msg = message.split(":")

    text = b64decode(splitted_msg[0])
    iv = b64decode(splitted_msg[1])
    key = get_key(version)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(text)

    decrypted_message = decrypted.rstrip(b"\x00")

    decrypted_message_str = decrypted_message.decode("utf-8")
    back = decrypted_message_str[-1]
    decrypted_response = json.loads(decrypted_message_str.strip(back))
    return decrypted_response


def check_session_availability():
    website_url = "https://iframeab-pre6751.intickets.ru"
    enrich_msg = lambda msg: f"{msg}\n{website_url}"

    response = requests.post(
        "https://api.intickets.ru/next/v2/?XDEBUG_SESSION_START&SESSI5d68f4e67c6f105b677163d3d95d137d=4ncaovttbk6mt3afiroudkvq5m",
        headers=headers,
        data=data,
    )
    decrypted_response = decrypt_response(response)
    try:
        seances = decrypted_response["Seances"]["Content"][0][0][12]
        some_is_open = any(map(lambda seance: seance[8] == "open", seances))
        some_is_buyable = any(map(lambda seance: seance[9] == "enable", seances))

        seance = seances[0]
        is_open = seance[8] == "open"
        is_buyable = seance[9] == "enable"

        if is_buyable:
            msg = "Tickets are available for buying now (sry for spam, ye...)!"
            notify_admins(enrich_msg(msg))
        elif is_open:
            msg = "Event opened but still unavailable for buying"
            notify_main_admin(enrich_msg(msg), prioritized=False)
        elif some_is_open or some_is_buyable:
            msg = "Some of events is available?! Check it, meister"
            notify_main_admin(enrich_msg(msg), prioritized=False)

    except Exception as e:
        msg = "Не смог распарситься - чекни плиз"
        notify_main_admin(enrich_msg(msg), prioritized=True)
        notify_main_admin(e, prioritized=True)



@app.route("/{}".format(secret), methods=["GET"])
def check_intickets():
    try:
        check_session_availability()
        return make_response("ok", 200)
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


@app.route("/silence", methods=["GET"])
def switch_silence():
    global is_silent_mode
    is_silent_mode = False if is_silent_mode else True
    msg = f"Silent mode switched to is_silent_mode={is_silent_mode}"
    notify_main_admin(msg, prioritized=True)
    return make_response(msg, 200)


notify_main_admin("Im ready!")
app.run(host="0.0.0.0", port=443, debug=False)
