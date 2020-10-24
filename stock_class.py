import timeit, json, datetime, math, random, datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas_datareader import data as wb
import FinanceFunctions as finance
import fin_statements as stmt
 
# Initialize Some Practice START and END dates
START = '2015-09-17'
END = '2020-09-17'


########### STOCK ############
# Defines the Stock class that gives you access to many technical analysis functions
#
class Stock():
    
    # Initializes the class, assigns the ticker and the date range for the data
    #  
    def __init__(self, ticker, startdate='1970-01-01', enddate=datetime.date.today().strftime('%Y-%m-%d')):

        # Init ticker, beta, covariance with S&P, and daterange
        self.ticker = ticker
        self.info = self.company_info()
        self.start_date = startdate
        self.end_date = enddate
        self.alpha = 0
        self.beta = 0
        self.covariance = 0

        # Init dataframes to hold data
        self.data = self.get_data(self.start_date, self.end_date)
        self.stock_returns = pd.DataFrame()
        self.rolling_avg = pd.DataFrame()
        self.weekly_returns = pd.DataFrame()
        self.income_stmt = pd.DataFrame()
        self.balance_sheet = pd.DataFrame()
        self.cashflow = pd.DataFrame()
        self.valuation = pd.DataFrame()
        
        # Init the json dictionary to hold data
        self.json_dict = {'Ticker': self.ticker, 'Current Price': float('{0:.2f}'.format(self.data['Adj Close'][self.data.index[-1].strftime('%Y-%m-%d')]))}
        self.json_dict['Start Date Price'] = float('{0:.2f}'.format(self.data['Adj Close'][self.data.index[0].strftime('%Y-%m-%d')])) 
     
     
    # Defines the representation of the object for the intepreter   
    def __repr__(self):
        return "Stock('%s')" % (self.ticker)

    
    #  Fetches the stocks Open, High, Low, Close, Adj Close data for the given time period
    #        is done on initialization, but can be recalled for new ranges of data
    #
    def get_data(self, start_date='not given', end_date='not given'):    
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        self.data = wb.DataReader(self.ticker, data_source="yahoo", start=start_date, end=end_date)
            
        return self.data
        

    # Calculates the 5, 10, 20, 30, and 50 day rolling average for the stock price
    #
    def get_rolling(self): 
            
        self.rolling_avg['5' ] = self.data['Adj Close'].rolling(window=5,  min_periods=1).mean()
        self.rolling_avg['10'] = self.data['Adj Close'].rolling(window=10, min_periods=1).mean()
        self.rolling_avg['20'] = self.data['Adj Close'].rolling(window=20, min_periods=1).mean()
        self.rolling_avg['30'] = self.data['Adj Close'].rolling(window=30, min_periods=1).mean()
        self.rolling_avg['50'] = self.data['Adj Close'].rolling(window=50, min_periods=1).mean()
        
        return self.rolling_avg
        
        
    # Fetches the weekly returns for a stock on a given interval
    #
    def get_returns(self, start_date='not given', end_date='not given'):
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        self.weekly_returns = finance.get_weekly_returns(self.ticker, start_date, end_date)
            
        return self.weekly_returns
    
    
    # Run Summary Statistics
    #
    def sum_stats(self, console=True):
        
        # Price Stats
        self.json_dict['Price Std Dev'  ] = float('{0:.2f}'.format(self.data['Adj Close'].std()))       
        self.json_dict['Price Variation'] = float('{0:.2f}'.format(self.data['Adj Close'].var())) 
        
        if self.weekly_returns.empty:
                self.get_returns(self.start_date, self.end_date)
                
        # Weekly Returns Stats
        self.json_dict['Weekly Returns Mean'     ] = float('{0:.2f}'.format(self.weekly_returns['returns'].mean()))
        self.json_dict['Weekly Returns Median'   ] = float('{0:.2f}'.format(self.weekly_returns['returns'].median()))
        self.json_dict['Weekly Returns Std Dev'  ] = float('{0:.2f}'.format(self.weekly_returns['returns'].std()))
        self.json_dict['Weekly Returns Variation'] = float('{0:.2f}'.format(self.weekly_returns['returns'].var()))
        
        # Prints the JSON data
        if console:
            print(json.dumps(self.json_dict, indent=4))
        
        return self.json_dict
    
    
    # Gets some Basic Company Information
    #
    def company_info(self):
        import yfinance as yf
    
        stock = yf.Ticker(self.ticker)
        summary = ['longName', 'sector', 'industry', 'city', 'state', 'country', 'website']
        information = {'ticker': self.ticker}
    
        for info in summary:
            try: information[info] = stock.info[info]
            except: print('key missing: ', info)
            
        return information
    
    
    #  Plots different graphs of stock date using Matplotlib like:
    #        weekly returns, price over time, rolling avg, and candlestick ohlc
    #
    def graph(self, plot_type, start_date='not given', end_date='not given', period='20'):
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        if plot_type == 'weekly returns':
            if self.weekly_returns.empty:
                self.get_returns(start_date, end_date)
                
            finance.plot_weekly_returns(self.weekly_returns, self.ticker)
        
        if plot_type == 'price/time':
            finance.plot_price(self.data['Adj Close'], self.ticker)
        
        if plot_type == 'rolling avg':
            if self.rolling_avg.empty:
                self.get_rolling()
            finance.rolling_plot(self.ticker, self.data, self.rolling_avg[period], period)
        
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
    def json(self, mode='w', filename='stock_info.json'):
        
        # Writes Data to JSON File
        if mode == 'w':
            with open(filename, 'w') as json_file:
                json.dump(self.json_dict, json_file, indent=4)
                
        # Reads Data from JSON File
        if mode == 'r':
            with open(filename, 'r') as json_file:
                self.json_dict = json.load(json_file)
                
        # Print self.json_dict in JSON format
        if mode == 'p':
            dump = json.dumps(self.json_dict, indent=4)
            print(dump)
            
    # Pulls the different financial statements from the Yahoo Finance webpages, this can be inconsistent sometimes
    #
    def statement(self, statement):

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
    def statement_csv(self, filename="fin_statements.csv"):
        
        # Pull statement data if it doesn't exist
        if self.balance_sheet.empty or self.income_stmt.empty or self.cashflow.empty or self.valuation.empty:
            self.balance_sheet = stmt.get_balance(self.ticker)
            self.cashflow = stmt.get_cashflow(self.ticker)
            self.income_stmt = stmt.get_income(self.ticker)
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
    def get_beta(self, start_date=(datetime.date.today() - datetime.timedelta(days=1825)).strftime('%Y-%m-%d'), 
                 end_date=datetime.date.today().strftime('%Y-%m-%d'), freq='M', plot=False, benchmark='SPY'):
        
        # Pulls Stock Data for the Period: Even if you've already pulled data, it does it again in case the dates aren't the same
        stock_data = wb.DataReader(self.ticker, data_source="yahoo", start=start_date, end=end_date)
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
        self.beta = float('{0:.4f}'.format(self.covariance / variance))
        self.alpha = benchmark_returns.mean() - (self.beta * stock_returns.mean())
        self.json_dict['Beta (OLS Regression)'] = self.beta
        self.json_dict['Covariance with Benchmark'] = self.covariance
        
        # Plot the Stock Returns over the benchmark Returns with the regression line
        if plot == True:
            
            # Define variables for the linear regression
            x = np.linspace(min(list(stock_ls)), max(list(stock_ls)), 5)
            y = self.alpha + self.beta * x

            # Plot, Label, and Show Graph
            plt.figure(figsize=(10,7))
            plt.scatter(stock_ls, benchmark_ls, label='Beta: ' + str(self.beta), alpha=0.3)
            plt.legend(loc='upper left')
            plt.plot(x, y, '-b', alpha=0.9)
            plt.axhline(y=0, xmin=-200, xmax=200, c="purple", linewidth=0.5, zorder=0) 
            plt.axvline(x=0, ymin=-200, ymax=200, c="purple", linewidth=0.5, zorder=0) 
            plt.xlabel('SPY Monthly Returns')
            plt.ylabel(str(self.ticker) + ' Monthly Returns')
            plt.title("Monthly Returns Regression: " + self.ticker + " over " + benchmark + "      ---------      From: " + start_date + " to " + end_date)
            plt.show()

        return self.beta
        

##########  PORTFOLIO ###########
# This is an object that defines a portfolio of stocks, you can add and subtract stocks, readjust their weightings, or run calculations on the data        
#
class Portfolio():
    
    def __init__(self, ticker_list, startdate='1970-01-01', enddate=datetime.date.today().strftime('%Y-%m-%d'), init_balance=0):
        
        # Init tickers. Ticker list needs to have the ticker and proportion together [ ['SPY', 0.5] , ['VTI' , 0.3] , ['MSFT', 0.2] ]
        self.stock_objects = []
        for stock in ticker_list:
            self.buffer_list = []
            self.buffer_list.append(Stock(str(stock[0]), START, END))
            self.stock_objects.append(self.buffer_list)
        
        # This is the main Portfolio variable, it holds a list with rows of the format: [ ticker, portfolio_weight, Stock Object ]  
        self.portfolio = np.concatenate([ticker_list, self.stock_objects], axis=1)
        self.stock_count = self.portfolio.shape[1]
        
        # Start and End Dates, Beta, and Balance Init
        self.start_date = startdate
        self.end_date = enddate
        self.beta = 0
        self.balance = init_balance
        
        # Init dataframes to hold data
        self.weekly_returns = pd.DataFrame()
        self.rolling_avg = pd.DataFrame()
        self.yearly_returns = pd.DataFrame()
        if not self.check_weighting():
            print("ERROR: The given weightings does not add to 100%")
            print(self.portfolio[:,1]) # Prints Weights
    
    # Defines the representation for the Object to the interpreter
    def __repr__(self):
        return "Portfolio('Balance: $%r', 'Number Of Stocks: %r')" % (self.balance, self.stock_count)
    
    # Allows the object to be used as a iterable
    def __getitem__(self, position):
        return self.portfolio[position, 2]
    
    # Gives the number of stocks in the portfolio
    def __len__(self):
        return self.portfolio.shape[1]
    
    
    # Just updates the count, for internal methods
    def update_num_stocks(self):
        self.stock_count = len(self)
        
    # This method will take a vertical list of the same number of stocks as your portfolio, and adds it to the right of the portfolio
    def add_category_to_portfolio (self, list_item):
        self.portfolio = np.concatenate([self.portfolio, list_item], axis=1)

    # Returns a value of true if the weighting adds up to 100%
    def check_weighting(self):
        total = 0.0000
        for row in self.portfolio:
            total += float(row[1])
        return np.isclose(1.0, total)
 
    
    # These function is used to add a stock onto the portfolio, it accepts a ticker and a weighting, 
    #                   currently only around 10 stocks can be added due to floating point error of the weightings (This will be updated)
    def add_stock(self, stock_ticker, weight, mode='equal'):
        
        buffer_list = [stock_ticker, float('{0:.12f}'.format(weight)), Stock(stock_ticker, self.start_date, self.end_date)]
        self.add_weight(buffer_list[1], mode)

        self.portfolio = np.vstack([self.portfolio, buffer_list])
        if not self.check_weighting():
            print("Error: Weights Do Not Add to 100%") 

            
    # This method is used to readjust the weights for when a stock is added, it is a work in progress and cannot currently handle more than a few stocks
    #                                                                                                                       due to floating point error
    def add_weight(self, weight, mode="equal"):
        
        factor = 10000000.0
        
        if mode == 'equal':
            
            # Creates a New List adding the new value and scaling down proportionally the old values and then scaling
            #                   all numbers up by a factor of ten for floating point issues
            new_list = [round(float(val) * float(factor - (factor * weight))) for val in self.portfolio[:,1]]
            new_list.append(round(float(weight) * factor))
            counter = len(new_list) - 1
            
            # Calculates the error difference of the expected and actual totals
            difference = sum(new_list) - factor


            # This section is designed to adjust for rounding errors by making sure everything adds up to 100% evenly. It definitely needs some attention
            #       The if block checks to see if the difference can be evenly spread to all the other members of the list, it also checks if the difference
            #                 is zero. The else block handles an uneven division using floor division and randomly assigned remainder
            #
            if difference != 0:
                if difference % (counter) == 0:
                    for num in range(0, len(new_list) - 1):
                        new_list[num] -= difference / (counter)
                else:

                    floor_div = difference // counter
                    diff_of_difference = difference - (counter * floor_div)

                    for num in range(0, len(new_list) - 1):
                        new_list[num] -= floor_div
                        new_list[num] = float('{0:.12f}'.format(float(new_list[num])))

                    rand_int = random.randint(0, counter - 1)
                    new_list[rand_int] -= float('{0:.12f}'.format(float(diff_of_difference)))
                    new_list[rand_int] = float('{0:.12f}'.format(new_list[rand_int]))

            # Divides out the factor of 10 from the weights so the output is a decimal
            counter = 0
            for weights in self.portfolio[:,1]: 
                self.portfolio[counter, 1] = float('{0:.12f}'.format(float(new_list[counter]) / factor))
                counter += 1
    
    
    # This function is used to subtract a stock from a portfolio, it accepts either a ticker or a stock object
    #
    def subtract_stock(self, stock, mode="equal"):
        if stock == str(stock):
            ticker = stock
        else:
            ticker = stock.ticker
                    
                
    # A function to subtract a weight and readjust the other weights proportionally
    def subtract_weight(self, mode, weight):
        print("Coming Soon")


# Test Code
if __name__ == "__main__":
    msft = Stock('MSFT', START, END)
    msft.get_beta(plot=False)

    print(msft.statement('income'))
    portfolio_list = [ ['SPY', 0.5] , ['VTI' , 0.3] , ['MSFT', 0.2] ]

    port_1 = Portfolio(portfolio_list)
    port_1.balance = 500100
    port_1.add_stock('SPY', 0.2)
    print(port_1.portfolio)

