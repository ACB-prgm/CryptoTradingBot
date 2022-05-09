import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# LEARNED
#  FALSE! : The smaller the LIMIT, the greater the return to a point.
#       Sometimes a larger limit has greater returns, thus there may be a confounding variable, such as volatility
#       Antother possibility is that the sell and buy limits need to be different


def describe(history):
    df = pd.DataFrame().from_dict(history).drop(columns=["volume"]).apply(pd.to_numeric, errors='coerce')
    changes = df["close_price"].pct_change()

    pos_changes = pd.Series([x for x in changes if x > 0.0])
    neg_changes = pd.Series([x for x in changes if x < 0.0])

    print("POSITIVE\n", pos_changes.describe())
    print("NEGATIVE\n", neg_changes.describe())


def freedman_diaconis(data): # determines how many bins to use in a histogram for a set of data
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    bin_width = (2 * iqr) / (len(data) ** (1 / 3))

    return int(np.ceil((data.max() - data.min()) / bin_width))
    

def get_limit(data, _type: int = 0):
    df = pd.DataFrame().from_dict(data).drop(columns=["volume"]).apply(pd.to_numeric, errors='coerce')
    changes = df["close_price"].pct_change()
    std = changes.std()
    if _type == 1:
        neg_changes = pd.Series([x for x in changes if x < 0.0])
        std = neg_changes.std()
    elif _type == 2:
        pos_changes = pd.Series([x for x in changes if x > 0.0])
        std = pos_changes.std()
    elif _type == 3:
        neg_changes = pd.Series([x for x in changes if x < 0.0])
        pos_changes = pd.Series([x for x in changes if x > 0.0])
        arr = [neg_changes, pos_changes]
        w = weighted_avg([x.std() for x in arr], [len(x) for x in arr])
    # print(f"Limit is %{round(std*100, 2)}")
    return std


def weighted_avg(array: list, weights: list):
    return avg([num * wght for num, wght in zip(array, weights)])


def avg(array: list):
        return sum(array) / len(array)