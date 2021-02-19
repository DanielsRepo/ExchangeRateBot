from datetime import datetime
from pymongo import MongoClient

from credentials import MONGODB_URI


client = MongoClient(MONGODB_URI)

db = client.exchange_rates_db
exchange_rates = db.exchange_rates


def check_loaded_rates():
    rates = exchange_rates.find_one({"_id": 1})

    if rates:
        if (datetime.now() - rates["requested_datetime"]).total_seconds() / 60.0 < 10:
            return rates["rates"]


def save_rates(rates):
    exchange_rates.update_one(
        {"_id": 1},
        {"$set": {"rates": rates, "requested_datetime": datetime.now()}},
        upsert=True,
    )
