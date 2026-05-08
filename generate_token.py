from kiteconnect import KiteConnect

from config import API_KEY, API_SECRET

# ---------------------------------
# INIT KITE
# ---------------------------------
kite = KiteConnect(api_key=API_KEY)

# ---------------------------------
# STEP 1: LOGIN URL
# ---------------------------------
print("\nOpen this URL in browser:\n")
print(kite.login_url())

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