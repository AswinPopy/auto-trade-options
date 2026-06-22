from broker.kite_session import kite

symbol = "TRENT26JUL3220PE"
quote = kite.quote(f"NFO:{symbol}")
quote_data = quote.get(f"NFO:{symbol}", {})
price = quote_data.get("last_price")
if price is None:
    price = quote_data.get("last_price")

print(f"symbol : {symbol} --- price : {price}")

