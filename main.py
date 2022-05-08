import custom_packages.robinhoodAPI as RH


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
SPAN = "3month"
MONEY = 1000.00
LIMIT = 0.05


def main():
    RH.login()
    for crypto in RH_Cryptos:
        x = RH.RHSimulation(crypto, LIMIT, MONEY)
        x.simulate(INTERVAL, SPAN, LOD=0)
    
    RH.logout()


if __name__ == "__main__":
    main()