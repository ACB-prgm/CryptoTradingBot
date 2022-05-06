# CryptoTradingBot
A work-in-progress trading bot to trade crypto at a daily rate using the robinhood API.

Currently, this works on a simple buy low, sell high strategy where all price changes greater than the LIMIT are considered for a trade.  The amount of crypto purchased at each event is currently determined by the magnitude of the change as a percent of the user's available buying power.  The script keeps track of each purchase seperately so that it will only sell once a price change event exceeds its purchase price.  

### IDEAS
- The LIMIT is currently arbitrary, so I would like to make an algorithm that analyzes a 5 year history and can determine the optimal LIMIT.  
- Make safeguards for crashes and volatility changes, as this strategy only works for typical market fluctuations over medium to long periods.  
- Potentially alter the trading frequency and LIMIT based upon the volatility of the market.
- Integrate analyst ratings, news articles, and correlated stock changes. (These are farther away)


## SIMULATION
Here is an simulation of the bot's trading patterns for DOGE over the last 3 months:
### PARAMETERS
```
SYMBOL = "DOGE"
INTERVAL = "day"
SPAN = "3month"
MONEY = 1000.00
LIMIT = 0.05
```

### FIG
![Figure_1](https://user-images.githubusercontent.com/63984796/167147167-d6d6db1b-afc0-492b-987c-1131e26847b3.png)
For clarification, the x-axis is showing all events where the price change was more than 5.0% in either direction over time.  The distance between points does NOT correlate with the amount of time between the events.  IE, the distance between p1 and p2 could represent one month, where the distance between p2 and p3 could represent 5 days.

### TRADES MADE:
```
bought 1511.76 DOGE ($209.22) at $0.138395. Money = 790.78
bought 1139.24 DOGE ($146.13) at $0.12827. Money = 644.65
sold 1094.52 DOGE ($152.1) at $0.13351 for 5.97 profit (4.09%). Money = 796.7496047400016
bought 1064.48 DOGE ($130.5) at $0.122595. Money = 666.2496047400016
sold 1004.62 DOGE ($138.28) at $0.1299 for 7.78 profit (5.96%). Money = 804.525635573233
sold 1445.14 DOGE ($218.87) at $0.144775 for 9.65 profit (4.61%). Money = 1023.3906632115147
bought 3639.88 DOGE ($521.65) at $0.143315. Money = 501.74066321151474
bought 1068.67 DOGE ($143.33) at $0.13412. Money = 358.4106632115147
sold 3298.56 DOGE ($575.63) at $0.158145 for 53.98 profit (10.35%). Money = 934.0401454708734
sold 906.32 DOGE ($169.0) at $0.158145 for 25.67 profit (17.91%). Money = 1103.0449385666086
bought 3129.53 DOGE ($430.53) at $0.13757. Money = 672.5149385666086
bought 871.41 DOGE ($111.11) at $0.127506175. Money = 561.4049385666086
sold 817.44 DOGE ($118.45) at $0.135924875 for 7.34 profit (6.6%). Money = 679.851067636436
bought 916.22 DOGE ($117.37) at $0.12810285. Money = 562.481067636436
```

### FINAL (start with $1000)
`$562.48 + 4266.29 DOGE ($547.9) = 1110.38 TOTAL | POSITION CHANGE = 11.04`

### ASSUMPTIONS
- No trading fees (which is possible with crypto)
- The DOGE will sell for the median of the bid and ask price
