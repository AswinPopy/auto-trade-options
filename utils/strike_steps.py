import json


with open(
    "utils/strike_gap.json",
    "r"
) as f:

    STRIKE_STEPS = json.load(f)


def get_strike_step(symbol):

    return STRIKE_STEPS.get(
        symbol
    )