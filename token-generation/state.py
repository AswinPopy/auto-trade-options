class AppState:

    token_generation_running = False

    waiting_for_app_code = False

    app_code = None
    request_token = None

state = AppState()

