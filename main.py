import custom_packages.robinhoodAPI as RH


SYMBOL = "DOGE"
INTERVAL = "day"
SPAN = "3month"
MONEY = 1000.00
LIMIT = 0.05


def main():
    RH.login()
    bch = RH.RHSimulation(SYMBOL, LIMIT, MONEY)
    bch.simulate(INTERVAL, SPAN, graph=True)
    RH.logout()


if __name__ == "__main__":
    main()