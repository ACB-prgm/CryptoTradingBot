from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np


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
    # print(f"Limit is %{round(std*100, 2)}")
    return std


def weighted_avg(array: list, weights: list):
    return avg([num * wght for num, wght in zip(array, weights)])


def avg(array: list):
    return sum(array) / len(array)


def get_y_ticker(ticker: str):
    hist = yf.Ticker(ticker).history("5Y")["Close"].apply(pd.to_numeric, errors="coerce")
    return hist.reindex(pd.date_range(start=hist.index.min(), end=hist.index.max(), freq='1D')).interpolate("pad")


def get_volatility_scores(crypto_object, span: str, score_interval: str = "week", current: bool = False):
    crypto = DT_formatted_hist(pd.DataFrame(crypto_object.get_historical("day", span=span)))["close_price"].pct_change()
    index = get_y_ticker("VOO").pct_change().loc[crypto.index]
    vix = get_y_ticker("^VIX")

    score_interval = RH_timestring_to_pd(score_interval)
    if current:
        today = datetime.today().date
    elif score_interval == "D": # daily does not work for some reason
        crypto = crypto.rolling(7).std()
        index = index.rolling(7).std()
        betas = crypto / index
        excl = betas.quantile(0.75) - betas.quantile(0.25)
        betas.clip(upper=excl, inplace=True)
    else:
        crypto = crypto.resample(score_interval, closed="left").std()
        index = index.resample(score_interval, closed="left").std()
        betas = crypto / index
        vix = vix.resample(score_interval, closed="left").mean()

    vix = vix.loc[betas.index] / 10.0
    
    scores = (vix + betas) / 2.0

    return betas


def DT_formatted_hist(historical, fill_dates: bool = True):
    df = historical.drop(columns=["volume", "session", "interpolated", "symbol"]).apply(pd.to_numeric, errors="ignore")
    df['begins_at'] = pd.to_datetime(df['begins_at']).dt.date
    df['begins_at'] = pd.to_datetime(df['begins_at'])
    df = df.set_index("begins_at")

    if fill_dates:
        df = df.reindex(pd.date_range(start=df.index.min(), end=df.index.max(), freq='1D'))
        df = df.interpolate("pad")
    
    return df


def RH_timestring_to_pd(interval: str):
    try:
        num = str(int(interval[0]))
        if "min" in interval:
            return interval
        elif num:
            return num + interval[1].upper()
    except ValueError:
        return interval[0].upper()


def num_points_from_interval(interval: str):

    # get num days in interval (approx)
    if interval == "week":
        interval = 7
    elif interval == "month":
        interval = 30
    elif interval == "3month":
        interval = 90
    elif interval == "year":
        interval == 253
    elif interval == "5year":
        interval = 253 * 5
    else:
        interval = 1