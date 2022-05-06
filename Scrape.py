import robin_stocks.robinhood as rh
import matplotlib.pyplot as plt
from datetime import date
import pickle


SAVE_PATH = "TradingBot/hist.pickle"
SYMBOL = "DOGE"
INTERVAL = "day"
SPAN = "3month"
MONEY = 1000.00
LIMIT = 0.05
positions = {} # structured as "purchase_price" : "position" aka amount of crypto purchased


def main():
    money = MONEY

    hist = get_historical(SYMBOL, interval=INTERVAL, span=SPAN)
    old_price = float(hist.pop(0).get("close_price"))

    # Variables for graphing and records
    changes = [0.0]
    prices = [old_price]
    buy_lines = []
    sell_lines = []

    for day in hist:
        curr_price = float(day.get("close_price"))
        change = get_percent_change(curr_price, old_price)
        old_price = curr_price

        if change > LIMIT or change < -LIMIT:
            changes.append(change)
            prices.append(curr_price)

            line_pos = len(prices) - 1
            if change < -LIMIT: # BUY
                buy_lines.append(line_pos)
                money = buy(money, change, curr_price)
            elif change > LIMIT: # SELL
                
                if positions:
                    sells = []
                    for purchase_price in positions:
                        if purchase_price < curr_price: 
                            sell_lines.append(line_pos)
                            sells.append(purchase_price)
                    for purchase_price in sells:
                        total_change = get_percent_change(curr_price, purchase_price)
                        position = positions.get(purchase_price)
                        del positions[purchase_price]

                        profit = position * total_change # calc increase in value of position
                        sell_amount = profit + position # how much the crypto is now worth
                        money += sell_amount
                        print(f"sold {position / curr_price} {SYMBOL} (${round(sell_amount, 2)}) at ${curr_price} for {round(profit, 2)} profit ({round(total_change*100, 2)}%). Money = {money}")
    
    position, value = get_position(SYMBOL)
    
    print(f"\nfinal ${round(money, 2)} and {position} {SYMBOL} ({value}) | ({round(get_percent_change(money+value, MONEY)*100, 2)}%)")

    # Graph performance
    plt.plot(range(len(prices)), prices, "-bo")
    margin = 0.01
    plt.vlines(buy_lines, [prices[y] - margin for y in buy_lines], [prices[y] + margin for y in buy_lines], colors="green")
    plt.vlines(sell_lines, [prices[y] - margin for y in sell_lines], [prices[y] + margin for y in sell_lines], colors="red")
    [plt.annotate("{} ({})".format(y, round(changes[prices.index(y)], 2)), (x,y+.01), ha="center") for y,x in zip(prices, range(len(prices)))]
    plt.show()


def buy(money, change, curr_price):
    buy_amount = abs(round(change * 3 * money, 2))
    positions[curr_price] = buy_amount
    money -= buy_amount

    print(f"bought {buy_amount / curr_price} {SYMBOL} (${buy_amount}) at ${curr_price}. Money = {money}")

    return money


def get_position(symbol: str):
    position = 0
    value = 0
    curr_price = get_current_price(symbol)

    for amount in positions:
        position += positions.get(amount) / curr_price
    value = position * curr_price

    return position, value


def get_current_price(symbol: str):
    QUOTE = rh.crypto.get_crypto_quote(symbol)
    ask = float(QUOTE.get("ask_price"))
    bid = float(QUOTE.get("bid_price"))
    avg_price = (bid+ask) / 2.0

    return avg_price


def get_historical(symbol: str, interval: str, span: str):
    args = set(locals().values())
    try: 
        with open(SAVE_PATH, 'rb') as file:
            hist = pickle.load(file)
            if not set(hist.get("args")).difference(args): # check if args differ
                if hist.get("day") == date.today().day: # check if data is more than a day old
                    return hist.get("data")
            else:
                pass
    except EOFError:
        pass
    
    # If can't load pickle, data is old, OR args are different: make new API call
    hist = {
        "day" : date.today().day,
        "args": args,
        "data" : rh.crypto.get_crypto_historicals(symbol, interval=interval, span=span)
    }
    with open(SAVE_PATH, 'wb') as file:
        pickle.dump(hist, file)
    return hist.get("data")


def get_percent_change(curr_price, old_price):
    return (curr_price - old_price) / old_price


def rh_login():
    try:
        rh.authentication.login()
    except:
        un = input("Enter Username: ")
        pw = input("Enter Password: ")
        rh.authentication.login(username=un, password=pw)


def rh_logout():
    rh.authentication.logout()


if __name__ == "__main__":
    rh_login()
    main()
    rh_logout()



# https://robinhood.com/crypto/DOGE