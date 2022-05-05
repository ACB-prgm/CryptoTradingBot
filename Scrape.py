import robin_stocks.robinhood as rh
import matplotlib.pyplot as plt
import pickle


SAVE_PATH = "TradingBot/hist.pickle"
MONEY = 1000.00
positions = {}


def main():
    money = MONEY

    hist = get_historical("DOGE", interval="day", span="3month")
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

        if change > 0.05 or change < -0.05:
            changes.append(change)
            prices.append(curr_price)

            line_pos = len(prices) - 1
            if change < -0.05: # BUY
                buy_lines.append(line_pos)
                money = buy(money, change, curr_price)
            elif change > 0.05: # SELL
                
                if positions:
                    sell_poss = []
                    for purchase_price in positions:
                        if purchase_price < curr_price: 
                            sell_lines.append(line_pos)
                            sell_poss.append(purchase_price)
                    for purchase_price in sell_poss:
                        # calculation is wrong
                        total_change = get_percent_change(curr_price, purchase_price)
                        position = positions.get(purchase_price)
                        del positions[purchase_price]

                        profit = position * total_change
                        sell_amount = profit + position
                        money += sell_amount
                        print(f"sold ${round(sell_amount, 2)} of DOGE at ${curr_price} for {round(profit, 2)} profit ({round(total_change*100, 2)}%). Money = {money}")
    
    for purchase_price in positions: # Cash out
        total_change = get_percent_change(curr_price, purchase_price)
        position = positions.get(purchase_price)
        sell_amount = (position * total_change) + position
        money += sell_amount
    
    print(f"final money = ${round(money, 2)} ({round(get_percent_change(money, MONEY)*100, 2)}%)")

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

    print(f"bought ${round(buy_amount, 2)} of DOGE at ${curr_price}. Money = {money}")

    return money


def get_current_price(symbol: str):
    QUOTE = rh.crypto.get_crypto_quote(symbol)
    ask = float(QUOTE.get("ask_price"))
    bid = float(QUOTE.get("bid_price"))
    spread = (bid+ask) / 2.0

    return spread


def get_historical(symbol: str, interval: str, span: str):
    args = set(locals().values())
    try: 
        with open(SAVE_PATH, 'rb') as file:
            hist = pickle.load(file)
            if not set(hist.get("args")).difference(args):
                return hist.get("data")
            else:
                pass
    except EOFError:
        pass
    
    # If can't load OR args are different, make new API call
    hist = {
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