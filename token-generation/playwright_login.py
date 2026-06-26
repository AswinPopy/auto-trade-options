import time
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv

from state import state
from telegram_utils import send_message

from kiteconnect import KiteConnect

from config import API_KEY, API_SECRET

from playwright.sync_api import sync_playwright

load_dotenv()


import callback

def save_access_token(token):

    env_path = ".env"

    lines = []

    with open(env_path, "r") as f:
        lines = f.readlines()

    updated = False

    for i, line in enumerate(lines):

        if line.startswith(
            "KITE_ACCESS_TOKEN="
        ):
            lines[i] = (
                f"KITE_ACCESS_TOKEN={token}\n"
            )
            updated = True

    if not updated:

        lines.append(
            f"KITE_ACCESS_TOKEN={token}\n"
        )

    with open(env_path, "w") as f:
        f.writelines(lines)


def wait_for_app_code():

    state.waiting_for_app_code = True

    send_message(
        "Waiting for app code.\n"
        "Reply:\n"
        "/code 123456"
    )

    while state.app_code is None:
        time.sleep(1)

    code = state.app_code

    state.app_code = None

    state.waiting_for_app_code = False

    return code


def run_playwright():

    callback.start_callback_server()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        login_url = "https://kite.zerodha.com/connect/login?api_key=um3tq7abh2dcllfy&v=3"
        page.goto(login_url)

        page.fill("#userid", "EKY281")
        page.fill("#password", "meAswin@7890")

        page.click('button[type="submit"]')

        app_code = wait_for_app_code()

        page.locator('input[type="number"]').fill(app_code)
        print("About to get req token")
        while state.request_token is None:
            print("4")
            time.sleep(0.5)
        print("5")
        request_token = state.request_token
        page.wait_for_timeout(5000)
        print("6")
        browser.close()
    print("Reached here --")
    kite = KiteConnect(api_key=API_KEY)

    data = kite.generate_session(
        request_token,
        api_secret=API_SECRET
    )

    access_token = data["access_token"]
    print(f"Access token is now : {access_token}")
    update_env(KEY_NAME, access_token)

    send_message("✅ Token generated successfully")


from urllib.parse import urlparse, parse_qs

def get_request_token(page):
    parsed = urlparse(page.url)
    print(f"parsed :{parsed}")
    return parse_qs(parsed.query)["request_token"][0]


ENV_FILE = ".env"
KEY_NAME = "KITE_ACCESS_TOKEN"

def update_env(key, value, file_path=ENV_FILE):
    lines = []
    updated = False

    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    updated = True
                else:
                    lines.append(line)
    except FileNotFoundError:
        print("File not found aan")
        pass

    if not updated:
        print("Not updated aan")
        lines.append(f"{key}={value}\n")

    with open(file_path, "w") as f:
        f.writelines(lines)


