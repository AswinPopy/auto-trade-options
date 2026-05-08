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
request_token = input(
    "\nPaste request_token here: "
)


# ---------------------------------
# STEP 3: GENERATE SESSION
# ---------------------------------
data = kite.generate_session(
    request_token,
    api_secret=API_SECRET
)


# ---------------------------------
# ACCESS TOKEN
# ---------------------------------
access_token = data["access_token"]

print("\n✅ ACCESS TOKEN:\n")

print(access_token)