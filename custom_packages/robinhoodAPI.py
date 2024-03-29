import robin_stocks.robinhood as rh
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from datetime import datetime
import pickle
import boto3
import io
import os


# DOCS: http://www.robin-stocks.com/en/latest/robinhood.html

DIR = "/".join(__file__.split("/")[:-1])
CACHE_DIR = os.path.join(DIR, "PicklesCache")
CACHE_MODE = "PICKLE"

with open(os.path.join(DIR, "aws_info.pickle"), "rb") as f: # pickled the info so that AWS wouldn't hold the account
    info = pickle.load(f)
    IAM_ID = info.get("IAM_ID")
    IAM_KEY = info.get("IAM_KEY")
    S3_BUCKET = "crypto-trading-bot-cache"

bucket = boto3.resource('s3', aws_access_key_id=IAM_ID, aws_secret_access_key=IAM_KEY).Bucket(S3_BUCKET)

class RHSimulation:

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.positions = {} # structured as "purchase_price" : "position" aka amount of crypto purchased
        self.LOD = None

    def simulate(self, interval: str, span: str, limit: float, starting_money: float, LOD: int = 1):
        self.LOD = LOD # 0 = outcome only, 1 += buy and sell reports, 2 += graph
        self.positions = {}
        money = starting_money

        hist = self.get_historical(interval, span)
        old_price = float(hist.pop(0).get("close_price"))

        # Variables for graphing and records
        changes = [0.0]
        prices = [old_price]
        buy_lines = []
        sell_lines = []

        for day in hist:
            curr_price = float(day.get("close_price"))
            change = self.get_percent_change(curr_price, old_price)
            old_price = curr_price

            if change > limit or change < -limit:
                changes.append(change)
                prices.append(curr_price)

                line_pos = len(prices) - 1
                if change < -limit: # BUY
                    buy_lines.append(line_pos)
                    money = self.sim_buy(money, change, curr_price)
                elif change > limit: # SELL
                    
                    if self.positions:
                        sells = []
                        for purchase_price in self.positions:
                            if purchase_price < curr_price: 
                                sell_lines.append(line_pos)
                                sells.append(purchase_price)
                        for purchase_price in sells:
                            total_change = self.get_percent_change(curr_price, purchase_price)
                            position = self.positions.get(purchase_price)
                            del self.positions[purchase_price]

                            profit = position * total_change # calc increase in value of position
                            sell_amount = profit + position # how much the crypto is now worth
                            money += sell_amount
                            if LOD > 1:
                                print(f"sold {round(position / curr_price, 2)} {self.symbol} (${round(sell_amount, 2)}) at ${curr_price} for {round(profit, 2)} profit ({round(total_change*100, 2)}%). Money = {money}")
        
        position, value = self.get_sim_position(hist)
        position = round(position, 2)
        value = round(value, 2)
        money = round(money, 2)
        position_change = round(self.get_percent_change(money+value, starting_money)*100, 2)
        if LOD > 0:
            print(f"FINAL ${money} + {position} {self.symbol} (${value}) = ${round(money + value, 2)} TOTAL | POSITION CHANGE = {position_change}%")

        if LOD > 2:
            # Graph performance
            plt.figure(figsize=(20,5))
            plt.plot(range(len(prices)), prices, "-bo")
            margin = self.get_avg(prices) * self.get_avg([abs(x) for x in changes])
            plt.vlines(buy_lines, [prices[y] - margin for y in buy_lines], [prices[y] + margin for y in buy_lines], colors="green")
            plt.vlines(sell_lines, [prices[y] - margin for y in sell_lines], [prices[y] + margin for y in sell_lines], colors="red")
            [plt.annotate("{} ({})".format(y, round(changes[prices.index(y)], 2)), (x,y + margin), ha="center") for y,x in zip(prices, range(len(prices)))]
            plt.title("{}-{}-{}".format(self.symbol, span, interval).upper(), fontweight= "bold")
            plt.xlabel(f"Changes > +/- {limit}", fontweight= "bold")
            plt.ylabel("Price", fontweight= "bold")
            plt.legend(handles=[Line2D([0], [0], color="green", lw=2, label='BUY'), Line2D([0], [0], color='red', lw=2, label='SELL')], loc='upper left')
            plt.show()
        
        return position_change


    def sim_buy(self, money, change, curr_price):
        buy_amount = abs(round(change * 3 * money, 2))
        self.positions[curr_price] = buy_amount
        money -= buy_amount
        if self.LOD > 1:
            print(f"bought {round(buy_amount / curr_price, 2)} {self.symbol} (${buy_amount}) at ${curr_price}. Money = {money}")

        return money


    def get_sim_position(self, hist):
        position = 0
        value = 0
        curr_price = self.sim_current_price(hist)

        for amount in self.positions:
            position += self.positions.get(amount) / curr_price
        value = position * curr_price

        return position, value


    def sim_current_price(self, hist):
        return float(hist[-1].get("close_price"))


    def get_historical(self, interval: str, span: str, stock: bool = False):
        args = "-".join([self.symbol, interval, span])
        SAVE_PATH = os.path.join(CACHE_DIR, f"{args}.pickle")
        NOW = datetime.now()
        log = pickle_log(args, NOW)

        if args in log and log.get(args) + 5 < NOW.hour + NOW.minute: # Load data
            if CACHE_MODE == "AWS":
                obj = io.BytesIO()
                bucket.download_fileobj(Key="hello.pickle", Fileobj=obj)
                obj.seek(0)
            else:
                with open(SAVE_PATH, "rb") as f:
                    obj = f
            hist = pickle.load(obj)
        else: # If no file or data is old: make new API call
            hist = {
                    "day" : NOW.day,
                    "args": args,
                }
            if stock:
                hist["data"] = rh.stocks.get_stock_historicals(self.symbol, interval=interval, span=span)
            else:
                hist["data"] = rh.crypto.get_crypto_historicals(self.symbol, interval=interval, span=span)
            
            if CACHE_MODE == "AWS":
                bucket.put_object(Body=pickle.dumps(hist), Key=args)
            else:
                with open(SAVE_PATH, "wb") as f:
                    pickle.dump(hist, f)

            return hist.get("data")


    def get_percent_change(self, curr_price, old_price):
        return (curr_price - old_price) / old_price
    
    
    def get_avg(self, array: list):
        return sum(array) / len(array)


def pickle_log(ids, NOW):
    SAVE_PATH = os.path.join(DIR, "log.pickle")

    if os.path.exists(SAVE_PATH): # if a log file exists, load it in
        with open(SAVE_PATH, "rb") as file:
            picklelog = pickle.load(file)

            if picklelog.get("last_accessed") != NOW.day: # empty bucket if > one day old
                s3 = boto3.resource('s3', aws_access_key_id=IAM_ID, aws_secret_access_key=IAM_KEY)
                s3.Bucket(S3_BUCKET).objects.delete()
                picklelog = {"last_accessed" : NOW.day} # reset picklelog
    else:
        picklelog = {"last_accessed" : NOW.day}

    new_log = picklelog
    new_log[ids] = NOW.time().hour + NOW.time().minute
    
    with open(SAVE_PATH, "wb") as file:
        pickle.dump(new_log, file)
    
    return picklelog


def get_current_price(symbol: str):
        QUOTE = rh.crypto.get_crypto_quote(symbol)
        ask = float(QUOTE.get("ask_price"))
        bid = float(QUOTE.get("bid_price"))
        avg_price = (bid + ask) / 2.0

        return avg_price


def login():
    try:
        rh.authentication.login()
    except:
        un = input("Enter Username: ")
        pw = input("Enter Password: ")
        rh.authentication.login(username=un, password=pw)


def logout():
    rh.authentication.logout()
