import os.path
import json
from datetime import datetime

import aiohttp
from dataclasses import dataclass
import pytz

tz = pytz.timezone("Asia/Dushanbe")

@dataclass(frozen=True)
class Currency:
    RUB_TO_TJK: float

RATES_URL = "https://alif.tj/api/rates"
filename = "rates_history.json"


async def get_actual_currency() -> Currency:
    api_data = await get_api_json(RATES_URL)
    if not api_data:
        exit("API data not found")
    rub_to_tjk = float(api_data["localRates"][2]["moneyTransferBuyValue"])
    return Currency(RUB_TO_TJK=rub_to_tjk)


async def get_api_json(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data


def save_result(rate: float):
    data = {}
    if os.path.exists(filename):
        data = json.load(open(filename))
    data[datetime.now(tz).strftime('%d.%m.%Y %H:%M')] = rate
    with open(filename, "w") as file:
        file.write(json.dumps(data))


def get_last_rate() -> float | None:
    if not os.path.exists(filename):
        return None
    data = json.load(open(filename))
    if not data:
        return None
    last_key = list(data.keys())[-1]
    return data[last_key]
