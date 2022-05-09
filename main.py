import custom_packages.robinhoodAPI as RH
import custom_packages.analyze as anal
import pandas as pd


RH_Cryptos = [
    "DOGE",
    "BTC",
    "ETH",
    "SOL",
    "SHIB",
    "MATIC",
    "LTC",
    "BCH",
    "ETC",
    "BSV",
    "COMP",
]

SYMBOL = "BTC"
INTERVAL = "day"
SPAN = "month"
MONEY = 100.00
LIMIT = 0.05


def main():
    RH.login()
    count = 0
    for crypto in RH_Cryptos:
        # print(f"####### {crypto} #######")
        crypto = RH.RHSimulation(crypto)

        control = crypto.simulate(INTERVAL, SPAN, LIMIT, MONEY, LOD=0)

        history = crypto.get_historical(INTERVAL, SPAN)
        limit = round(anal.get_limit(history, 3), 4)
        experiment = crypto.simulate(INTERVAL, SPAN, limit, MONEY, LOD=0)
        # print( f"Control (lim {LIMIT}): {control}% | Experiment (lim {limit}) {experiment}% | Experiment better? {experiment > control}")
        # print(pd.DataFrame(history)["close_price"].apply(pd.to_numeric, errors='coerce').pct_change().mean())

        if experiment > control:
            count += 1
        # anal.describe(history)
        # print("\n")
    
    print(count)
    # RH.logout()


if __name__ == "__main__":
    main()