import pandas as pd
import numpy as np
from pandas_datareader import data as wb
import matplotlib.pyplot as plt
import datetime
import pandas_market_calendars as mcal
import timeit
from scipy.stats import norm
import plotly.graph_objects as go
import io
import matplotlib as mpl


#   Pull Data for candlestick
def get_candlestick_data(ticker, stock_data, startdate, enddate):  
    
    candlestick = go.Candlestick(
                            x=stock_data.index,
                            open=stock_data['Open'],
                            high=stock_data['High'],
                            low=stock_data['Low'],
                            close=stock_data['Close']
                            )
    #save_fig(candlestick, ticker)
    
    plot_candle(candlestick, ticker)
    
# save candlestick
def save_candle(data, ticker):
    fig = go.Figure(data=[data])
    
    fig.update_layout(
        title='Open High Low Close Candle Stick Graphs',
        yaxis_title= ticker + ' Price $',
        xaxis_rangeslider_visible=False)
    
    fig.write_image("temp.png")

# Plot Candlestick
def plot_candle(data, ticker):
    fig = go.Figure(data=[data])
    
    fig.update_layout(
        title='Open High Low Close Candle Stick Graphs',
        yaxis_title= ticker + ' Price $')
    fig.show()

# Plot Rolling Averages
def rolling_plot(ticker, data, rolling_data, period):
    
    plt.style.use('ggplot')    
    plt.figure(figsize=(10,6))
    
    plt.title("Stock Price Over Time")
    plt.ylabel("Price of Stock ($)")
    plt.xlabel("Time (Trading Days)")
    
    plt.plot(data['Adj Close'])
    plt.plot(rolling_data, 'r:')
    plt.legend([ticker, str(period) + " Day Rolling Average"], loc=0)
    plt.show()
    
# Calculate Monte Carlo Simulations for Future Price Estimations

def get_monte_carlo(ticker, startdate, enddate, years):  
    
    # Pull Stock data and Compute the logreturns
    stock_data = pd.DataFrame()
    stock_data[ticker] = wb.DataReader(ticker, data_source="yahoo", start=startdate, end=enddate)['Adj Close']
       
    log_returns = np.log(1 + stock_data.pct_change())
    
    mean = log_returns.mean()
    var = log_returns.var()  
    stdev = log_returns.std()  
    drift = mean - (0.5 * var)
    
    # Initialize Simulation Variables
    intervals = 252 * years
    iterations = 10
    
    # Do the stats math Future Returns = drift + shock
    daily_returns = np.exp(drift.values + stdev.values * norm.ppf(np.random.rand(intervals, iterations)))
    
    S0 = stock_data.iloc[-1]
    
    # Set up future stock values array starting with the last value of the known prices
    price_list = np.zeros_like(daily_returns)
    price_list[0] = S0
    
    for t in range(1, intervals):
        price_list[t] = price_list[t-1] * daily_returns[t]
    
    # Plot Graph
    plot_MonteCarlo(price_list)
    
    # Save Graph
    #save_MonteCarlo(price_list)

    
# Function to plot monte carlo graph
def plot_MonteCarlo(price_list):
    
    plt.style.use('seaborn-ticks')    
    plt.figure(figsize=(10,6))
    
    plt.title(" Geometric Brownian Motion Monte Carlo Price Simulation")
    plt.ylabel("Price of Stock ($)")
    plt.xlabel("Time (Trading Days)")
    
    plt.plot(price_list)
    plt.show()

# Plot Price/Time
def plot_price(price_list, ticker):
    
    plt.style.use('seaborn-ticks')     
    plt.figure(figsize=(10,6))
    
    plt.title("Stock Price Over Time")
    plt.ylabel("Price of Stock ($)")
    plt.xlabel("Time (Trading Days)")
    
    plt.plot(price_list)
    plt.legend([ticker], loc=4)
    plt.show()
 
# Plot Portfolio Returns   
def plot_port_returns(returns, period):
    
    plt.style.use('seaborn-ticks')     
    plt.figure(figsize=(10,6))
    
    plt.title(period + " Portfolio Returns")
    plt.ylabel("Return of Stock (%)")
    plt.xlabel("Date (" + period + ")")

    plt.plot(returns)
    plt.axhline(y=0,xmin=0,xmax=200,c="red",linewidth=1,zorder=0) 
    plt.legend(['Portfolio'], loc=4)
    plt.show()

#    Converts Y-M-D value to datetime object
def ymd_to_dt(ymd_date):
    year, month, day = (int(x) for x in ymd_date.split('-'))    
    return datetime.date(year, month, day)

#     Accepts Y-M-D value and outputs day of the week
#                 in integer form Mon = 0; Sunday = 6
def weekday(date):
    return datetime.datetime.weekday(ymd_to_dt(date))

#    Find the closest Adj Close date to a closed date
def next_opened_date(stock_data, closed_date, rewind, nyse):
    rewind += 1
    if market_closed((closed_date - datetime.timedelta(days=rewind)).strftime('%Y-%m-%d'), nyse):                               
        week_begin = next_opened_date(stock_data, closed_date, rewind, nyse)                    
    else:
        week_begin = stock_data[closed_date - datetime.timedelta(days=rewind)]     
    return week_begin        

#   Retrieves a list of open market days in a range of dates
def get_business_days_list(startdate, enddate):   
    nyse = mcal.get_calendar('NYSE')
    business_days = nyse.valid_days(start_date=startdate, end_date=enddate).strftime('%Y-%m-%d')
    date_list = []
    for date in range(0, len(business_days) - 1):
        date_list.append(business_days[date])  
    return date_list

#   Tests to see if the date is in the list of valid business days
def market_closed(date, nyse):
    try:
        nyse.index(date)
        return False
    except: 
        return True
    
# Calculate Weekly Stock Returns
def get_weekly_returns(stock_, startdate, enddate):  

    # Initialize Variables For Weekly Return Loop
    week_begin = 0
    week_end = 0
    week = 0
    first_week = 0    
    
    # Lists for Dates and Returns
    y = []
    x = []
    
    # Datetime dates and business day list
    start_date = ymd_to_dt((stock_.data['Adj Close'].index[0]).strftime('%Y-%m-%d'))
    end_date = ymd_to_dt(enddate)
    nyse = get_business_days_list(startdate, enddate)

    # Time Delta
    delta = datetime.timedelta(days=1)

    #   Loops through a date range, finds all the Mondays and Fridays, makes sure they are
    #        opened  business days, and calculates the weekly return
    while start_date <= end_date:              
        
        #  Checks to see if the date is a Monday
        if datetime.datetime.weekday(start_date) == 0:   
            if market_closed(start_date.strftime('%Y-%m-%d'), nyse) and (first_week == 1):
                week_begin = next_opened_date(stock_.data['Adj Close'], start_date, 2, nyse)                  
            if not(market_closed(start_date.strftime('%Y-%m-%d'), nyse)): 
                try:
                    
                    week_begin = stock_.data['Adj Close'][start_date.strftime('%Y-%m-%d')]               
                    first_week = 1
                except:
                    print('Error: ' + start_date.strftime('%Y-%m-%d'))
            if(start_date + (delta * 4)) <= end_date:
                start_date += delta * 4
            
        
        if (first_week == 1) and (datetime.datetime.weekday(start_date) == 4):
            if market_closed(start_date.strftime('%Y-%m-%d'), nyse):
                week_end = next_opened_date(stock_.data['Adj Close'], start_date, 0, nyse)            
            else:
                week_end = stock_.data['Adj Close'][start_date.strftime('%Y-%m-%d')]             
            y.append((week_end - week_begin) / week_begin * 100)
            x.append(start_date.strftime('%Y-%m-%d'))
            
            week += 1
            start_date += delta * 2
           
        start_date += delta

    max_value = int(max(y))
    min_value = int(min(y))


    # Output Return Data  
    # Show Graph  
    #plot_Graph(x, y, ticker, max_value, min_value)              

    # Save Graph
    #save_Graph(x, y, ticker, max_value, min_value)
    
    # Returns a list of weekly returns and the end dates corresponding with them
    returns_list = [x,y]
    rows = []
    for i in range(0, len(returns_list[0])):
        rows.append([returns_list[0][i], returns_list[1][i]])
     
    weekly_returns = pd.DataFrame(rows, columns=['Date','Returns'])
    
    return weekly_returns

def get_y_count(daterange, begin_range, end_range):   
    if (daterange >= begin_range) and (daterange <=end_range):
        return 1
    else:
        begin_range += 5
        end_range += 5     
        return 1 + get_y_count(daterange, begin_range, end_range)

#     Graph Weekly Return Data         
def plot_weekly_returns(weekly_returns, ticker):
    
    daterange = list(weekly_returns.index)
    graph_Data = list(weekly_returns['Returns'])
    max_value, min_value = int(max(graph_Data)), int(min(graph_Data))
    
    y_count = get_y_count(len(daterange), 0, 5)
    
    plt.style.use('seaborn-ticks')    
    plt.figure(figsize=(10,6))
    
    axes = plt.axes()
    axes.set_ylim(min_value - 2, max_value + 2)
    axes.set_xticks(np.arange(0, len(daterange), y_count))
    axes.set_yticks(np.arange(min_value, max_value + 2, 2))
    
    plt.title("Weekly Stock Returns")
    plt.ylabel("Weekly Return %")
    plt.xlabel("Trading Weeks")
    
    plt.axhline(y=0,xmin=0,xmax=200,c="red",linewidth=1,zorder=0) 
    plt.plot (daterange, graph_Data, label=ticker)
    plt.legend(framealpha=1, frameon=True)
    plt.show()
    
def save_Graph(daterange, graph_Data, ticker, max_value, min_value):
    
    y_count = get_y_count(len(daterange), 0, 5)
    
    plt.style.use('seaborn-ticks')    
    plt.figure(figsize=(10,6))
    
    axes = plt.axes()
    axes.set_ylim([min_value - 2, max_value + 2])
    axes.set_xticks(np.arange(0, len(daterange), y_count))
    axes.set_yticks(np.arange(min_value, max_value + 2, 2))
    
    plt.title("Weekly Stock Returns")
    plt.ylabel("Weekly Return %")
    plt.xlabel("Trading Weeks")
    
    plt.axhline(y=0,xmin=0,xmax=200,c="red",linewidth=1,zorder=0) 
    plt.plot (daterange, graph_Data, label=ticker)
    plt.legend(framealpha=1, frameon=True)
    plt.savefig("temp_returns.png")
    plt.close()