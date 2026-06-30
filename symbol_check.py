from broker.kite_session import kite

symbol = "NIFTY26JUN24000PE"
quote = kite.quote(f"NFO:{symbol}")
quote_data = quote.get(f"NFO:{symbol}", {})
print(quote_data)
# if price is None:
#     price = quote_data.get("last_price")

# print(f"symbol : {symbol} --- price : {price}")

