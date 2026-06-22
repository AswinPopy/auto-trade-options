from broker.kite_session import kite
orders = kite.orders()

for order in orders:
    print(f"order : {order}")
    if order["order_id"] == 260622191137389:
        print(order["status"])
        print(order.get("status_message"))