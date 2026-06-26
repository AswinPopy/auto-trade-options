import threading

from state import state
from playwright_login import run_playwright
from telegram_utils import send_message


def generate_token():

    if state.token_generation_running:
        return

    state.token_generation_running = True

    try:

        send_message(
            "Starting Kite login..."
        )

        run_playwright()

        send_message(
            "✅ Token generated"
        )

    except Exception as e:

        send_message(
            f"❌ Token generation failed\n{e}"
        )

    finally:

        state.token_generation_running = False
        state.waiting_for_app_code = False
        state.app_code = None


def start_generation():

    threading.Thread(
        target=generate_token,
        daemon=True
    ).start()

    