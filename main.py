import custom_packages.robinhoodAPI as RH
import custom_packages.analyze as anal
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd


RH_cryptos = [
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
RH_intervals = ["5min", "10min", "hour", "day", "week"]
RH_spans = ["day", "week", "month", "3month", "year",  "5year"]


SYMBOL = "ETH"
INTERVAL = "week"
SPAN = "year"
MONEY = 100.00
LIMIT = 0.05

def main():
    print("start")
    RH.login()

    # crypto = SYMBOL
    sp500 = anal.get_y_ticker("VOO") # because they have a negative correlation for some reason
    vix = anal.get_y_ticker("^VIX")
    success = 0
    for crypto in RH_cryptos:
        other = RH.RHSimulation(crypto)

        df2 = anal.get_volatility_scores(other, span=SPAN, score_interval=INTERVAL)
        crypto_hist = anal.DT_formatted_hist(pd.DataFrame(other.get_historical(INTERVAL, SPAN)))["close_price"].pct_change().abs()
        
        if INTERVAL != "day":
            crypto_hist = anal.DT_formatted_hist(pd.DataFrame(other.get_historical(INTERVAL, SPAN)))["close_price"].pct_change().abs().resample(anal.RH_timestring_to_pd(INTERVAL), closed="left").std()

        
        custom = stats.spearmanr(crypto_hist, df2.loc[crypto_hist.index])
        SP500 = stats.spearmanr(crypto_hist, sp500.loc[crypto_hist.index])
        VIX = stats.spearmanr(crypto_hist, vix.loc[crypto_hist.index])

        # print(crypto)
        # print(f"Custom : {custom} \nSP500 : {SP500} \nVIX {VIX}")

        custom = abs(custom[0] / custom[1])
        SP500 = abs(SP500[0] / SP500[1])
        VIX = abs(VIX[0] / VIX[1])
        
        # print(f" Custom > SP500: {custom > SP500} \n Custom > VIX: {custom > VIX}\n")
        if custom > VIX or custom > SP500:
            success += 1
        # quit()

        PLOT = False
        if PLOT:
            fig, ax1 = plt.subplots(figsize=(20,5))

            color = 'tab:red'
            ax1.plot(df2, color=color)
            ax1.set_ylabel("Volatility", color=color)
            ax1.tick_params(axis='y', labelcolor=color)

            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

            color = 'tab:blue'
            ax2.plot(crypto_hist, color=color)
            ax2.set_ylabel(f"{crypto} %∆", color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            plt.title(f"{crypto}-{INTERVAL}-{SPAN}")
            plt.show()

            PLOT = False

    print(f"betas success {success}")
    # RH.logout()


if __name__ == "__main__":
    main()


# https://robinhood.com