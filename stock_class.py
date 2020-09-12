import timeit
import datetime
import pandas as pd
import numpy as np
import matplotlib as mpl
from scipy.stats import norm
import matplotlib.pyplot as plt
import pandas_market_calendars as mcal
from pandas_datareader import data as wb
from pandas.util.testing import assert_frame_equal
import FinanceFunctions as finance

# Initialize Some Practice START and END dates
START = '1990-01-01'
END = '2020-06-01'

# Defines the Stock class that gives you access to many technical analysis functions
#
class Stock():
    
    # Initializes the class, assigns the ticker and the date range for the data
    #
    def __init__(self, ticker, start_date='1970-01-01', end_date=datetime.date.today().strftime('%Y-%m-%d')):
        
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        
        self.data = self.get_data(start_date, end_date)
        self.stock_returns = pd.DataFrame()
        self.rolling_avg = pd.DataFrame()
        self.weekly_returns = pd.DataFrame()
        
        
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
    def get_rolling(self, start_date='not given', end_date='not given'): 
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        self.rolling_avg['5'] = self.data['Adj Close'].rolling(window=5, min_periods=1).mean()
        self.rolling_avg['10'] = self.data['Adj Close'].rolling(window=10, min_periods=1).mean()
        self.rolling_avg['20'] = self.data['Adj Close'].rolling(window=20, min_periods=1).mean()
        self.rolling_avg['30'] = self.data['Adj Close'].rolling(window=30, min_periods=1).mean()
        self.rolling_avg['50'] = self.data['Adj Close'].rolling(window=50, min_periods=1).mean()
        
        return self.rolling_avg
        
        
    # Fetches the weekly returns for a stock on a given interval
    #
    def get_weekly_returns(self, start_date='not given', end_date='not given'):
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        self.weekly_returns = finance.get_weekly_returns(self.ticker, start_date, end_date)
        return self.weekly_returns
    
    
    #  Plots different graphs of stock date using Matplotlib like:
    #        weekly returns, price over time, rolling avg, and candlestick ohlc
    #
    def plot_data(self, plot_type, start_date='not given', end_date='not given', period='20'):
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        if plot_type == 'weekly returns':
            if self.weekly_returns.empty:
                self.get_weekly_returns(start_date, end_date)
            x = list(self.weekly_returns['Date'])
            y = list(self.weekly_returns['Returns'])
            finance.plot_Graph(x, y, self.ticker, int(max(y)), int(min(y)))
        
        if plot_type == 'price/time':
            finance.plot_price(self.data['Adj Close'], self.ticker)
        
        if plot_type == 'rolling avg':
            if self.rolling_avg.empty:
                self.get_rolling(start_date, end_date)
            finance.rolling_plot(self.ticker, self.data, self.rolling_avg[period], period)
        
        if plot_type == 'candlestick':
            finance.get_candlestick_data(self.ticker, self.data, start_date, end_date)
        
        
    # Calculates and graphs a Geometric Brownian Motion Monte Carlo Price Simulator
    #
    def monte_carlo(self, start_date='not given', end_date='not given', years=5):
        
        if start_date == 'not given' and  end_date == 'not given':
            start_date, end_date = self.start_date, self.end_date
            
        if self.data.empty:
            print("Initialize the Data for Stock: " + self.ticker)
            return
        finance.get_monte_carlo(self.ticker, start_date, end_date, years)


# Test Variables
spy = Stock('SPY')
print(spy.get_weekly_returns())