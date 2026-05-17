from kiteconnect import KiteConnect

from config import (
    API_KEY,
    ACCESS_TOKEN
)

kite = KiteConnect(
    api_key=API_KEY
)

kite.set_access_token(
    ACCESS_TOKEN
)

