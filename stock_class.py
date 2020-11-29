"""Stock_Class."""

import json, datetime, math

import pandas as pd
import numpy as np

from matplotlib import pyplot  as plt
from pandas_datareader import data as wb

from concurrent import futures
from itertools import repeat

import FinanceFunctions as finance
import fin_statements as stmt

'''
"""    """

Stock Analysis Program - Quick Overview
    
    # Defines a Stock and Portfolio Class that provide
        analysis functions built on top of free APIs and web scraped pages
        
    #    Stock('ticker') initializes a Stock object which also accepts a date 
                range for its data. The object provides rolling avgs, returns
                over different periods, beta calcs, summary information and stats,
                financial statements and company valuation.
            
    #    Portfolio([['ticker', weight], ['ticker', weight], ['ticker', weight] ...])
                this initializes a Portfolio object that creates a list of Stock objects
                to manage portfolio analysis easily. It is a work in progress.

""""   """
'''

# Initialize Some Practice START and END dates
START = (datetime.date.today() - datetime.timedelta(days=30 * 6)).strftime('%Y-%m-%d')
END = datetime.date.today().strftime('%Y-%m-%d')


########### STOCK ############
# Defines the Stock class that gives you access to many technical analysis functions
#
class Stock():
    """Stock Analysis Object."""    
    
    # Initializes the class, assigns the ticker and the date range for the data
    #  
    def __init__(self, ticker, startdate='1970-01-01', enddate=datetime.date.today().strftime('%Y-%m-%d')):

        # Init ticker and daterange
        self.ticker = ticker
        self.start_date = startdate
        self.end_date = enddate
        
        #Init beta and covariance with benchmark (S&P)
        self.alpha = None
        self._beta = None
        self.covariance = 0

        # Init dataframes to hold data
        self._data = wb.DataReader(ticker, data_source="yahoo", start=startdate, end=enddate)
        self._returns = {}
        
        self.rolling_avg = pd.DataFrame()
        self.weekly_returns = pd.DataFrame()
        self.income_stmt = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cashflow = pd.DataFrame()
        self.valuation = pd.DataFrame()
        
        # Init a dictionary to hold stock info
        self._info = {}
     
     
    # Defines the representation of the object for the intepreter   
    def __repr__(self):
        return "Stock('%s')" % (self.ticker)
    
    def __getitem__(self, key):
        return self.data[key]

    
    #  Fetches the stocks Open, High, Low, Close, Adj Close data for the given time period
    #        is done on initialization, but can be recalled for new ranges of data
    #
    @property
    def data(self, start_date='not given', end_date='not given'):    
        
        if not(start_date == 'not given' and  end_date == 'not given'):
            self._data = wb.DataReader(self.ticker, data_source="yahoo", start=start_date, end=end_date)
            
        return self._data
        

    # Calculates the 5, 10, 20, 30, and 50 day rolling average for the stock price
    #
    @property
    def rolling(self): 
        '''Property that pulls the rolling averages of a stock'''
        
        if self.rolling_avg.empty:  

            self.rolling_avg = pd.DataFrame()
            self.rolling_avg['5' ] = self.data['Adj Close'].rolling(window=5,  min_periods=1).mean()
            self.rolling_avg['10'] = self.data['Adj Close'].rolling(window=10, min_periods=1).mean()
            self.rolling_avg['20'] = self.data['Adj Close'].rolling(window=20, min_periods=1).mean()
            self.rolling_avg['30'] = self.data['Adj Close'].rolling(window=30, min_periods=1).mean()
            self.rolling_avg['50'] = self.data['Adj Close'].rolling(window=50, min_periods=1).mean()
        
        return self.rolling_avg
        
        
    # Fetches the weekly returns for a stock on a given interval
    #
    @property
    def returns(self, period='W', start_date='not given', end_date='not given'):
        '''Calculates Daily, Weekly, Monthly, and Yearly Returns'''
        
        skip = (start_date == 'not given' and  end_date == 'not given')
            
        if not(self._returns) or not(skip):
            if skip:
                start_date, end_date = self.start_date, self.end_date
            else:
                _ = self.data(start_date, end_date)
            # Uses Pandas function to pull percent returns for different time periods, cleans the date, and standardizes the index/column names
            self._returns['D'] = pd.DataFrame((self.data['Adj Close'].pct_change(freq='D')[1:] * 100).dropna()).rename(columns={'Adj Close': 'Returns'})
            #self._returns['W'] = finance.get_weekly_returns(self, start_date, end_date).set_index('Date')
            self._returns['M'] = pd.DataFrame((self.data['Adj Close'].pct_change(freq='M')[1:] * 100).dropna()).rename(columns={'Adj Close': 'Returns'})
            self._returns['Y'] = pd.DataFrame((self.data['Adj Close'].pct_change(freq='Y')[1:] * 100).dropna()).rename(columns={'Adj Close': 'Returns'})
        
        return self._returns
    
    
    # Calculate Summary Statistics on Price and Returns
    #
    def summary_stats(self, console=False):
        
        def warning_remove(x): return x
            
        # Price Stats
        if not(self._info):
            info = self.info
            warning_remove(info)
            
        self._info['Price Std Dev'  ] = float('{0:.2f}'.format(self.data['Adj Close'].std()))       
        self._info['Price Variation'] = float('{0:.2f}'.format(self.data['Adj Close'].var())) 
        
        if not self._returns:
                returns = self.returns
                warning_remove(returns)
                
        # Returns Stats
        strings = [('Daily', 'D'), ('Weekly', 'W'), ('Monthly', 'M'), ('Yearly', 'Y')]
        for name, identifier in strings:
            self._info[name + 'Returns Mean'     ] = float('{0:.2f}'.format(self.returns[identifier]['returns'].mean()))
            self._info[name + 'Returns Median'   ] = float('{0:.2f}'.format(self._returns[identifier]['returns'].median()))
            self._info[name + 'Returns Std Dev'  ] = float('{0:.2f}'.format(self._returns[identifier]['returns'].std()))
            self._info[name + 'Returns Variation'] = float('{0:.2f}'.format(self._returns[identifier]['returns'].var()))
        
        # Prints the JSON data
        if console:
            print(json.dumps(self._info, indent=4))
        
        return self._info
    
    
    # Gets some Basic Company Information
    #
    @property
    def info(self):
        
        if not(self._info):
            
            self._info = {'Ticker': self.ticker, 'Current Price': float('{0:.2f}'.format(self.data['Adj Close'][self.data.index[-1].strftime('%Y-%m-%d')]))}
            self._info['Start Date Price'] = float('{0:.2f}'.format(self.data['Adj Close'][self.data.index[0].strftime('%Y-%m-%d')])) 
        
            import yfinance as yf
        
            stock = yf.Ticker(self.ticker)
        
            if stock.info['quoteType'] == 'ETF':
                self._info['Type'] = 'ETF'
            else:
                self._info['Type'] = 'Stock'
                summary = ['longName', 'sector', 'industry', 'city', 'state', 'country', 'website']
                information = {}

                for info in summary:
                    try: information[info] = stock.info[info]
                    except: print('key missing: ', info)

                self._info.update(information)
            
        return self._info
    
    
    #  Plots different graphs of stock date using Matplotlib like:
    #        weekly returns, price over time, rolling avg, and candlestick ohlc
    #
    def graph(self, plot_type='price', start_date='not given', end_date='not given', period='20'):
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        if plot_type == 'weekly returns':
            finance.plot_weekly_returns(self.returns['W'], self.ticker)
        
        if plot_type == 'price':
            finance.plot_price(self.data['Adj Close'], self.ticker)
        
        if plot_type == 'rolling':
            finance.rolling_plot(self.ticker, self.data, self.rolling[period], period)
        
        if plot_type == 'candlestick':
            finance.get_candlestick_data(self.ticker, self.data, start_date, end_date)
        
        
    # Calculates and graphs a Geometric Brownian Motion Monte Carlo Price Simulator
    #
    def monte_carlo(self, start_date='not given', end_date='not given', years=5):
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date

        finance.get_monte_carlo(self.ticker, start_date, end_date, years)


    # Converts Stock Data to and from JSON files
    #
    @property
    def json(self, mode='w', filename='stock_info.json'):
         
        # Writes Data to JSON File
        if mode == 'w':
            with open(filename, 'w') as json_file:
                json.dump(self.info, json_file, indent=4)
                
        # Reads Data from JSON File (really shouldn't be used) 
        if mode == 'r':
            with open(filename, 'r') as json_file:
                self.info = json.load(json_file)
                
        # Print self.json_dict in JSON format
        if mode == 'p':
            dump = json.dumps(self.info, indent=4)
            print(dump)
            
        return json.dumps(self.info, indent=4)
            
    # Pulls the different financial statements from the Yahoo Finance webpages, this can be inconsistent sometimes
    #
    def statement(self, statement='income'):

        if not self.info['Type'] == 'Stock':
            return "Error: Cannot Retrieve statements for ETF"
        # Pulls the data for each type of statement
        if statement == 'income':
            self.income_stmt = stmt.get_income(self.ticker)
            return self.income_stmt
        if statement == 'balance':
            self.balance_sheet = stmt.get_balance(self.ticker)
            return self.balance_sheet
        if statement == 'cashflow':
            self.cashflow = stmt.get_cashflow(self.ticker)
            return self.cashflow
        if statement == 'valuation':
            self.valuation = stmt.get_valuation(self.ticker)
            return self.valuation
        if statement == 'all':
            self.income_stmt = stmt.get_income(self.ticker)
            self.balance_sheet = stmt.get_balance(self.ticker)
            self.cashflow = stmt.get_cashflow(self.ticker)
            self.valuation = stmt.get_valuation(self.ticker)
            
    # Pull financial statements if they haven't been already and save the files to a csv.
    #
    def stmts_to_csv(self, filename="fin_statements.csv"):
        
        # Pull statement data if it doesn't exist
        if self.balance_sheet.empty:
            self.balance_sheet = stmt.get_balance(self.ticker)
        if self.cashflow.empty:
            self.cashflow = stmt.get_cashflow(self.ticker)
        if self.income_stmt.empty:
            self.income_stmt = stmt.get_income(self.ticker)
        if self.valuation.empty:
            self.valuation = stmt.get_valuation(self.ticker)
        
        # Writes data to a CSV with headers
        with open(filename, 'w') as file:
            file.write("\nIncome Statement\n")
            self.income_stmt.to_csv(file) 
            file.write("\n\nBalance Sheet\n")
            self.balance_sheet.to_csv(file)  
            file.write("\n\nStatement of Cash Flows\n")
            self.cashflow.to_csv(file)
            file.write("\n\nBasic Valuation\n")
            self.valuation.to_csv(file)


    # Gets 5 Year Beta Value against SPY using a Monthly Returns Interval, uses Econometric Regression Coefficients not CAPM Model
    #
    @property
    def beta(self, start_date=(datetime.date.today() - datetime.timedelta(days=1825)).strftime('%Y-%m-%d'), 
                 end_date=datetime.date.today().strftime('%Y-%m-%d'), freq='M', plot=False, benchmark='SPY'):
        
        # Returns the Beta number if no change is being made to the date range and it aleady exists
        if (self._beta != None) and benchmark == 'SPY' and start_date == (datetime.date.today() - datetime.timedelta(days=1825)).strftime('%Y-%m-%d') and end_date == datetime.date.today().strftime('%Y-%m-%d'):
            return self._beta
        
        # Pulls Stock Data for the Period
        if start_date != self.start_date or end_date != self.end_date:
            stock_data = wb.DataReader(self.ticker, data_source="yahoo", start=start_date, end=end_date)
        else:
            stock_data = self.data

        benchmark_data = wb.DataReader(benchmark, data_source="yahoo", start=start_date, end=end_date)
            
        
        # Calculates Returns over certain period of time
        stock_returns = stock_data['Adj Close'].pct_change(freq='M')[1:] * 100
        benchmark_returns = benchmark_data['Adj Close'].pct_change(freq='M')[1:] * 100

        # Cleans out the list of any NaN values
        stock_ls = []
        benchmark_ls = []
        for data in range(0, len(stock_returns)):
            if not(math.isnan(stock_returns[data])):
                stock_ls.append(stock_returns[data])
            if not(math.isnan(benchmark_returns[data])):
                benchmark_ls.append(benchmark_returns[data])
        return_arrary = np.stack((stock_ls, benchmark_ls), axis=0)
        
        # Calculates Variance of the Stock, Covariance of the Stock and a Benchmark, beta, alpha, and an error term
        variance = float('{0:.2f}'.format(stock_returns.var()))
        self.covariance = float('{0:.2f}'.format(np.cov(return_arrary)[0][1]))
        self._beta = float('{0:.4f}'.format(self.covariance / variance))
        self.alpha = benchmark_returns.mean() - (self._beta * stock_returns.mean())
        def warning_remove(x): return x
        if not(self._info):
            info = self.info
            warning_remove(info)
        self._info['Beta (OLS Regression)'] = self.beta
        self._info['Covariance with Benchmark'] = self.covariance
        
        # Plot the Stock Returns over the benchmark Returns with the regression line
        if plot == True:
            
            # Define variables for the linear regression
            x = np.linspace(min(list(stock_ls)), max(list(stock_ls)), 5)
            y = self.alpha + self._beta * x

            # Plot, Label, and Show Graph
            plt.figure(figsize=(10,7))
            plt.scatter(stock_ls, benchmark_ls, label='Beta: ' + str(self._beta), alpha=0.3)
            plt.legend(loc='upper left')
            plt.plot(x, y, '-b', alpha=0.9)
            plt.axhline(y=0, xmin=-200, xmax=200, c="purple", linewidth=0.5, zorder=0) 
            plt.axvline(x=0, ymin=-200, ymax=200, c="purple", linewidth=0.5, zorder=0) 
            plt.xlabel('SPY Monthly Returns')
            plt.ylabel(str(self.ticker) + ' Monthly Returns')
            plt.title("Monthly Returns Regression: " + self.ticker + " over " + benchmark + "      ---------      From: " + start_date + " to " + end_date)
            plt.show()

        return self._beta
        

##########  PORTFOLIO ###########
# This is an object that defines a portfolio of stocks, you can add and subtract stocks, readjust their weightings, or run calculations on the data        
#
class Portfolio():
    
    def __init__(self, ticker_list, startdate='1970-01-01', enddate=datetime.date.today().strftime('%Y-%m-%d'), init_balance=0):
        
        # Init tickers. Ticker list needs to have the ticker and proportion together [ ['SPY', 0.5] , ['VTI' , 0.3] , ['MSFT', 0.2] ]
        self.stock_objects = []
        tickers = [ticker[0] for ticker in ticker_list]
        weights = [float(ticker[1]) for ticker in ticker_list]
        objects = self.pull_stocks(tickers, startdate, enddate)
        
        # This is the main Portfolio variable, it holds a list with rows of the format: [ ticker, portfolio_weight, Stock Object ]  
        self.portfolio = np.array(list(zip(tickers, weights, objects)))
        
        # Initializes private variables for the portfolio data and returns
        self._data = pd.DataFrame()
        self._returns = {}
        self.rolling_avg = pd.DataFrame()
        
        # Start and End Dates, Beta, and Balance Init
        self.start_date = startdate
        self.end_date = enddate
        self._beta = None
        self.balance = init_balance

        if not self.check_weighting():
            raise 'Weightings Do Not Add Up To 1.00'
    
    # Defines the representation for the Object to the interpreter
    def __repr__(self):
        return "Portfolio('Balance: $%r', 'Number Of Stocks: %r')" % (self.balance, len(self))
    
    # Allows the object to be used as a iterable
    def __getitem__(self, position):
        return self.portfolio[position, 2]
    
    # Gives the number of stocks in the portfolio
    def __len__(self):
        return self.portfolio.shape[0]
    
    # A function to pull portfolio data concurrently using futures to speed up processing time
    #
    def pull_stocks(self, tickers, START, END):
    
            def create(ticker, startdate, enddate):
                return Stock(ticker, startdate=startdate, enddate=enddate)

            executer = futures.ThreadPoolExecutor(max_workers=5)
            results = executer.map(create, tickers, repeat(START), repeat(END))
            stock_list = [result for i, result in enumerate(results)]
    
            return stock_list
        
    # This method will take a vertical list of the same number of stocks as your portfolio, and adds it to the right of the portfolio
    def add_category_to_portfolio (self, list_item):
        self.portfolio = np.concatenate([self.portfolio, list_item], axis=1)

    # Returns a value of true if the weighting adds up to 100%
    def check_weighting(self):
        total = 0.0000
        for row in self.portfolio:
            total += float(row[1])
        return np.isclose(1.0, total)
    
    # Fetches the data from each stock and compiles it together into one Portfolio df
    #
    @property
    def data(self, start_date='not given', end_date='not given'):
        
        if self._data.empty or (start_date == 'not given' and end_date == 'not given'):
             
            self._data = self[0].data * self.portfolio[0, 1]
            for position in range(1, len(self)):
                self._data += self[position].data * self.portfolio[position, 1]
    
            self._data = self._data.dropna()

        return self._data
    
    # Calculates periods of Returns for the Portfolio
    #
    @property
    def returns(self, period='W', start_date='not given', end_date='not given'):
        '''Calculates Daily, Weekly, Monthly, and Yearly Returns'''
        
        skip = (start_date == 'not given' and  end_date == 'not given')
            
        if not(self._returns) or not(skip):
            if skip:
                start_date, end_date = self.start_date, self.end_date
            else:
                _ = self.data(start_date, end_date)
            # Uses Pandas function to pull percent returns for different time periods, cleans the date, and standardizes the index/column names
            self._returns['D'] = pd.DataFrame((self.data['Adj Close'].pct_change(freq='D')[1:] * 100).dropna()).rename(columns={'Adj Close': 'Returns'})
            self._returns['W'] = finance.get_weekly_returns(self, start_date, end_date).set_index('Date')
            self._returns['M'] = pd.DataFrame((self.data['Adj Close'].pct_change(freq='M')[1:] * 100).dropna()).rename(columns={'Adj Close': 'Returns'})
            self._returns['Y'] = pd.DataFrame((self.data['Adj Close'].pct_change(freq='Y')[1:] * 100).dropna()).rename(columns={'Adj Close': 'Returns'})
        
        return self._returns
    
    # Calculates rolling averages from the portfolio data
    @property
    def rolling(self): 
        '''Property that pulls the rolling averages of a stock'''
        
        if self.rolling_avg.empy:  
            self.rolling_avg['5' ] = self.data['Adj Close'].rolling(window=5,  min_periods=1).mean()
            self.rolling_avg['10'] = self.data['Adj Close'].rolling(window=10, min_periods=1).mean()
            self.rolling_avg['20'] = self.data['Adj Close'].rolling(window=20, min_periods=1).mean()
            self.rolling_avg['30'] = self.data['Adj Close'].rolling(window=30, min_periods=1).mean()
            self.rolling_avg['50'] = self.data['Adj Close'].rolling(window=50, min_periods=1).mean()
        
        return self.rolling_avg
    
    @property
    def beta(self):
        
        if self._beta == None:
            
            def get_beta(self, position):
                    return self[position].beta * self.portfolio[position, 1]
                
            executer = futures.ThreadPoolExecutor(max_workers=5)
            results = executer.map(get_beta, repeat(self), range(len(self)))
            beta_list = [result for i, result in enumerate(results)]
            self._beta = sum(beta_list)
            
        return self._beta
    
    # Graphs Portfolio Data
    #
    def graph(self, plot_type='price', start_date='not given', end_date='not given', period='20'):
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        if plot_type == 'weekly returns':
            finance.plot_weekly_returns(self.returns['W'], 'Weekly')
            
        if plot_type == 'daily returns':
            finance.plot_port_returns(self.returns['D'], 'Daily')
        
        if plot_type == 'monthly returns':
            finance.plot_port_returns(self.returns['M'], 'Monthly')
            
        if plot_type == 'yearly returns':
            finance.plot_port_returns(self.returns['Y'], 'Yearly')
        
        if plot_type == 'price':
            finance.plot_price(self.data['Adj Close'], 'Portfolio')
        
        if plot_type == 'rolling':
            finance.rolling_plot('Portfolio', self.data, self.rolling[period], period)
        
        #if plot_type == 'candlestick':
            #finance.get_candlestick_data(self.ticker, self.data, start_date, end_date)
 
    
# Test Code
if __name__ == "__main__":
    portfolio_list = [ ['SPY', 0.5] , ['VTI' , 0.3] , ['MSFT', 0.2] ]

    port_1 = Portfolio(portfolio_list)
    print(port_1.portfolio)

