import re, logging

from collections import defaultdict

from broker.kite_session import kite
from config import UNDERLYING

# ====================================
# FETCH NFO INSTRUMENTS
# ====================================
nfo_instruments = kite.instruments(
    "NFO"
)
# ====================================
# STORE STRIKES
# ====================================
strike_map = defaultdict(set)

# ====================================
# EXTRACT STRIKES
# ====================================
for i in nfo_instruments:
    symbol = i["tradingsymbol"]
    name = i['name']
    # if not symbol.startswith("INFY"):
    #     continue
    # print(i)
    print("SYMBOL", symbol)
    # break
    match = re.search(
        r'(\d+)(CE|PE)$',
        symbol
    )

    if not match:
        print("match not found")
        continue

    strike = int(
        match.group(1)
    )

    strike_map[name].add(
        strike
    )

# ====================================
# CALCULATE STEPS
# ====================================
strike_steps = {}
for stock, strikes in (
    strike_map.items()
):
    strikes = sorted(strikes)

    if len(strikes) < 2:
        print("strikes < 2")
        continue

    gaps = []

    for i in range(
        1,
        len(strikes)
    ):

        gap = (
            strikes[i]
            - strikes[i - 1]
        )

        if gap > 0:
            gaps.append(gap)

    if not gaps:
        print("not gaps < 2")
        continue

    strike_steps[stock] = min(gaps)

print("strike steps", strike_steps)
# ====================================
# GENERATE FILE
# ====================================
import json


with open(
    "utils/strike_gap.json",
    "w"
) as f:

    json.dump(
        strike_steps,
        f,
        indent=4
    )

print(
    "\n✅ strike_gap.json generated\n"
)

print("\n✅ strike_steps.py generated\n")

print(strike_steps)