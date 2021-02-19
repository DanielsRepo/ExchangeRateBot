import pandas as pd
import matplotlib.pyplot as plt


def build_graph(hist_data, currency, days_quan):
    df = pd.DataFrame(hist_data)
    x = df["date"]
    y = df["exchange_rate"]

    plt.figure(figsize=(10, 5))
    plt.title(f"USD/{currency} {days_quan} days exchange rate history")
    plt.xticks(rotation=45)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Exchange rate", fontsize=12)
    plt.grid(linestyle="--")
    plt.plot(x, y)
    plt.tight_layout()

    plt.savefig(f"/tmp/{currency}{days_quan}.png")
