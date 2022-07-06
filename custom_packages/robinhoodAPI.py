import robin_stocks.robinhood as rh
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from datetime import date
import pickle
import shutil
import boto3
import os


# DOCS: http://www.robin-stocks.com/en/latest/robinhood.html

SAVE_DIR = os.path.join("/".join(__file__.split("/")[:-1]), "Pickles")
AWS_ID = "AKIAVVWQARCLO5TB6SNQ",
AWS_KEY = "Bd9aIiVS0fCgDLiRZcNq6Lo91iVhoI2WUAygdXvp"


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
        args = [self.symbol, interval, span]
        pickel_log()

        SAVE_PATH = os.path.join(SAVE_DIR, f"{'-'.join(args)}.pickle")

        if os.path.exists(SAVE_PATH): # Load data
            with open(SAVE_PATH, 'rb') as file:
                hist = pickle.load(file)
                if hist.get("data"):
                    return hist.get("data")
        else: # If no file or data is old: make new API call
            hist = {
                    "day" : date.today().day,
                    "args": args,
                }
            if stock:
                hist["data"] = rh.stocks.get_stock_historicals(self.symbol, interval=interval, span=span)
            else:
                hist["data"] = rh.crypto.get_crypto_historicals(self.symbol, interval=interval, span=span)

            with open(SAVE_PATH, 'wb') as file:
                pickle.dump(hist, file)
            
            return hist.get("data")


    def get_percent_change(self, curr_price, old_price):
        return (curr_price - old_price) / old_price
    
    
    def get_avg(self, array: list):
        return sum(array) / len(array)



def pickel_log():
    SAVE_PATH = os.path.join(SAVE_DIR, "log.pickle")
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "rb") as file:
            picklelog = pickle.load(file)
            if picklelog.get("last_accessed") != date.today().day:
                shutil.rmtree(SAVE_DIR)
    
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)     

    picklelog = {
        "last_accessed" : date.today().day
    }
    with open(SAVE_PATH, "wb") as file:
        pickle.dump(picklelog, file)


def get_current_price(symbol: str):
        QUOTE = rh.crypto.get_crypto_quote(symbol)
        ask = float(QUOTE.get("ask_price"))
        bid = float(QUOTE.get("bid_price"))
        avg_price = (bid+ask) / 2.0

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

s3_client = boto3.client("s3", aws_access_key_id=AWS_ID, aws_secret_access_key=AWS_KEY)