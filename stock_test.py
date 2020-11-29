"""Test."""

import datetime
import stock_class as stock

ticker_list = [['SPY', 0.2], ['VTI', 0.3], ['MSFT', 0.3],
               ['GOOG', 0.1], ['BAC', 0.05], ['AMZN', 0.05]]
START = (datetime.date.today() - datetime.timedelta(days=30 * 6)).strftime('%Y-%m-%d')
END = datetime.date.today().strftime('%Y-%m-%d')

test = stock.Portfolio(ticker_list)
print(test.data)
