from datetime import timedelta, date, datetime
from operator import itemgetter
import os

import requests
import telebot

from db import save_rates, check_loaded_rates
from utils import build_graph
from flask import Flask, request
from credentials import TOKEN, HEROKU_URL

from pprint import pprint

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["list"])
def get_rates_list(message):
    chat_id = message.from_user.id
    rates_data = check_loaded_rates()

    if not rates_data:
        rates_data = requests.get(
            "https://api.exchangeratesapi.io/latest?base=USD"
        ).json()["rates"]

        save_rates(rates_data)

    rates = ""
    for k, v in rates_data.items():
        rates += f"*{k}*: {round(v, 2)} \n"

    bot.send_message(chat_id, rates, parse_mode="Markdown")


@bot.message_handler(commands=["exchange"])
def get_exchange_rate(message):
    chat_id = message.from_user.id
    message_args = message.text.split()

    try:
        quan = int(message_args[1])
        currency = message_args[2].upper()

        currency_rate = requests.get(
            f"https://api.exchangeratesapi.io/latest?base=USD&symbols=USD,{currency}"
        ).json()["rates"][currency]

        conversion = round(quan * currency_rate, 2)

        bot.send_message(chat_id, f"{quan} USD = {conversion} {currency}")
    except Exception:
        bot.send_message(chat_id, "Wrong command format")


@bot.message_handler(commands=["history"])
def get_rates_history(message):
    chat_id = message.from_user.id
    message_args = message.text.split()

    try:
        currency = message_args[1].upper()
        days_quan = int(message_args[2])

        start_date = date.today() - timedelta(days=days_quan)
        end_date = date.today()

        rates_data = requests.get(
            "https://api.exchangeratesapi.io/history"
            f"?start_at={start_date}&end_at={end_date}&base=USD&symbols={currency}"
        ).json()["rates"]

        if rates_data:
            history = []

            for k, v in sorted(rates_data.items(), key=itemgetter(0)):
                history_dict = {
                    "date": datetime.strptime(k, "%Y-%m-%d").strftime("%d.%m.%Y"),
                    "exchange_rate": v[currency],
                }
                history.append(history_dict)

            build_graph(history, currency, days_quan)

            bot.send_photo(chat_id, photo=open(f"/tmp/{currency}{days_quan}.png", "rb"))
        else:
            bot.send_message(
                chat_id,
                "No exchange rate data is available for the selected currency",
            )
    except Exception:
        bot.send_message(chat_id, "Wrong command format")


@bot.message_handler(commands=["help"])
def show_help(message):
    bot.send_message(
        message.from_user.id,
        "*list* - get list of all available rates\n"
        "*exchange* <USD quantity> <currency> - convert currencies\n"
        "*history* <currency> <days quantity> - get exchange rate graph",
        parse_mode="Markdown",
    )


# server = Flask(__name__)


# @server.route(f"/{TOKEN}", methods=["POST"])
# def get_messages():
#     updates = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
#     bot.process_new_updates([updates])
#     return "Ok", 200


# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url=f"{HEROKU_URL}{TOKEN}")
#     return "Webhook was set", 200


if __name__ == "__main__":
    # server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    bot.polling(none_stop=True, interval=0)
