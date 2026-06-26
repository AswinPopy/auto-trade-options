import requests
import time

from dotenv import load_dotenv
import os

from state import state
from kite_worker import start_generation
from telegram_utils import send_message

load_dotenv()

BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

ALLOWED_CHAT_ID = int(
    os.getenv(
        "TELEGRAM_CHAT_ID"
    )
)

offset = None


def process_message(text):

    global offset

    if text == "/kite":

        start_generation()

        return

    if text == "/status":

        if state.waiting_for_app_code:

            send_message(
                "Waiting for app code"
            )

        elif state.token_generation_running:

            send_message(
                "Generating token"
            )

        else:

            send_message(
                "Idle"
            )

        return

    if text.startswith(
        "/code "
    ):

        code = (
            text
            .replace("/code", "")
            .strip()
        )

        state.app_code = code

        send_message(
            "App code received"
        )

        return


while True:

    try:

        params = {}

        if offset:
            params["offset"] = offset

        resp = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
            params=params,
            timeout=30,
        ).json()

        for update in resp["result"]:

            offset = (
                update["update_id"]
                + 1
            )

            message = update.get(
                "message"
            )

            if not message:
                continue

            chat_id = (
                message["chat"]["id"]
            )

            if (
                chat_id
                != ALLOWED_CHAT_ID
            ):
                continue

            text = message.get(
                "text",
                "",
            )

            process_message(text)

    except Exception as e:

        print(e)

    time.sleep(2)

    