from broker.kite_session import kite

symbol = "DIVISLAB26JUL6550CE"
quote = kite.quote(f"NFO:{symbol}")
quote_data = quote.get(f"NFO:{symbol}", {})
depth = quote_data.get("depth")
print(quote_data)
# if price is None:
#     price = quote_data.get("last_price")

# print(f"symbol : {symbol} --- price : {price}")

