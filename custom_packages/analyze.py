import matplotlib.pyplot as plt
import robinhoodAPI as RH
import pandas as pd
import numpy as np




def main():
    crypto = RH.RHSimulation("DOGE", 5.0, 100)
    hist = crypto.get_historical("day", "year")

    df = pd.DataFrame().from_dict(hist).drop(columns=["volume"]).apply(pd.to_numeric, errors='coerce')
    # print(df.describe())
    changes = df["close_price"].pct_change()
    bins = freedman_diaconis(changes)
    changes.hist(bins=bins)
    std = changes.std()
    print(f"Limit for {crypto.symbol} is %{round(std*100, 2)}")
    plt.vlines([std, -std], 0.0, changes.value_counts(bins=bins).iloc[0], color="red")
    plt.show()



def freedman_diaconis(data):
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    
    bin_width = (2 * iqr) / (len(data) ** (1 / 3))

    return int(np.ceil((data.max() - data.min()) / bin_width))
    




if __name__ == "__main__":
    RH.login()
    main()
    RH.logout()



