from kiteconnect import KiteConnect

from config import API_KEY, API_SECRET

from playwright.sync_api import sync_playwright
import pyotp
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False  # Show browser window
    )

    page = browser.new_page()

    login_url = "https://kite.zerodha.com/connect/login?api_key=um3tq7abh2dcllfy&v=3"

    page.goto(login_url)
    page.fill("#userid", "EKY281")
    page.fill("#password", "meAswin@7890")

    page.wait_for_timeout(60000) 

# ---------------------------------
# INIT KITE
# ---------------------------------
kite = KiteConnect(api_key=API_KEY)


# ---------------------------------
# STEP 2: PASTE REQUEST TOKEN
# ---------------------------------
request_token = input("\nPaste request_token here: ")

# ---------------------------------
# STEP 3: GENERATE SESSION
# ---------------------------------
data = kite.generate_session(
    request_token,
    api_secret=API_SECRET
)

access_token = data["access_token"]

print("\n✅ ACCESS TOKEN GENERATED\n")

# ---------------------------------
# STEP 4: WRITE TO .ENV
# ---------------------------------
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
        pass

    if not updated:
        lines.append(f"{key}={value}\n")

    with open(file_path, "w") as f:
        f.writelines(lines)

# save token
update_env(KEY_NAME, access_token)

print("✅ ACCESS TOKEN SAVED TO .env")