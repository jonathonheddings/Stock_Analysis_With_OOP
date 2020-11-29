import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as ur

#########################

# Uses Yahoo Finance free webpages to pull basic financial statements and format the data into Pandas Dataframes
#        It is possible issues may arise in the future when the number of columns change as that is not acccounted for

#########################

# Pulls data from a given URL, formats it to lxml and saves it to a variable
#
def pull_data(url):
    
    # Opens a URL and saves the lxml data to a variable for processing
    webpage = ur.urlopen(url).read() 
    soup = BeautifulSoup(webpage,'lxml')

    # Finds all the lines with the div class and saves them to a list for further processing
    sort_divs = []
    for line in soup.find_all('div'): 
        sort_divs.append(line.string) 

    # Cleans out Empty rows and returns the result
    return list(filter(None, sort_divs))


# Reindex and transpose the data to flip the rows and columns
#
def transpose_df(data):

    df = pd.DataFrame(data)
    df.columns = df.iloc[0]
    df = df.iloc[1:,]
    
    df = df.T
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)
    
    return df
    
# Pull Income Statement from Yahoo Finance
#
def get_income(ticker):
    
    # Opens a URL for an income statement and saves the lxml data to a variable for processing
    income_st_url = 'https://finance.yahoo.com/quote/' + ticker + '/financials?p='
    new_ls = pull_data(income_st_url)
    
    # Searches for the start of the data to slice out the rest
    slicer = 0
    for div in new_ls:   
        if 'ttm' == div:
            break
        slicer += 1

    # Isolate the data and add extra entries for missing Categories caused by drop down menus
    statement = new_ls[slicer:]
    statement.insert(0,  'Annual')
    statement.insert(6,  'Total Revenue')
    statement.insert(24, 'Operating Expense')
    statement.insert(36, 'Net Non Operating Interest Income Expense')
    statement.insert(42, 'Other Income Expense')
    statement.insert(60, 'Net Income Common Stockholders')

    # Reorganizes the data in 6 columns and import into a pandas df, remove some useless rows, and name it
    df_buffer = list(zip(*[iter(statement)]*6))
    income_statement = transpose_df(df_buffer)
    income_statement = income_statement[income_statement.columns[:-5]]
    income_statement.name = "Income Statement"

    return income_statement

# Pulls Balance Sheet from Yahoo Finance
#
def get_balance(ticker):
    
    # Opens a URL for a balance sheet and saves the lxml data to a variable for processing
    balance_sheet_url = 'https://finance.yahoo.com/quote/' + ticker + '/balance-sheet?'
    new_ls = pull_data(balance_sheet_url)
    
    # Searches for the start of the data to slice out the rest
    slicer = 0
    for div in new_ls:   
        if 'Expand All' == div:
            break
        slicer += 1
        
    # Isolate the data and add extra entries for missing Categories caused by drop down menus
    statement = new_ls[slicer + 1:]
    statement.insert(0,  'Annual')
    statement.insert(5,  'Total Assets')
    statement.insert(10, 'Total Liabilities')
    statement.insert(15, 'Total Equity')

    # Reorganizes the data in 5 columns and import into a pandas df, remove some useless rows, and name it; 
    df_buffer = list(zip(*[iter(statement)]*5))
    balance_sheet = transpose_df(df_buffer)
    balance_sheet = balance_sheet[balance_sheet.columns[:-1]]
    balance_sheet.name = "Balance Sheet"

    return balance_sheet

# Pulls Statement of Cash Flows from Yahoo Finance
#
def get_cashflow(ticker):
    
    # Opens a URL for a balance sheet and saves the lxml data to a variable for processing
    cashflow_url = 'https://finance.yahoo.com/quote/' + ticker + '/cash-flow?p='
    new_ls = pull_data(cashflow_url)
    
    # Searches for the start of the data to slice out the rest
    slicer = 0
    for div in new_ls:   
        if 'ttm' == div:
            break
        slicer += 1
    
    # Isolate the data and add extra entries for missing Categories caused by drop down menus
    statement = new_ls[slicer:]
    statement.insert(0,  'Annual')
    statement.insert(6,  'Operating Cash Flow')
    statement.insert(12, 'Investing Cash Flow')
    statement.insert(18, 'Financing Cash Flow')
    statement.insert(24, 'End Cash Position')

    # Reorganizes the data in 5 columns and import into a pandas df, remove some useless rows, and name it; 
    df_buffer = list(zip(*[iter(statement)]*6))
    cashflows = transpose_df(df_buffer)
    cashflows.name = "Statement of Cash Flows"

    return cashflows

def get_valuation(ticker):
    
    # Pulls the reformatted webpage data and assigns it to a variable
    url = 'https://finance.yahoo.com/quote/' + ticker + '/key-statistics?p=' + ticker  
    webpage = ur.urlopen(url).read() 
    soup = BeautifulSoup(webpage,'lxml')
    
    # Finds the numerical data entries in the table
    sort_divs = []
    for line in soup.find_all('div'): 
        for data in line.find_all('td'):
            sort_divs.append(data.string)
    
    # Cleans out Empty rows, organizes data into rows, and returns the result for the numerical values in the table
    new_list = list(filter(None, sort_divs))
    new_list = new_list[:54]
    table_data = list(zip(*[iter(new_list)]*5))
    
    # Find all the indexes for the table of financial data
    sort_divs = []
    for line in soup.find_all('div'): 
        for data in line.find_all('span'):
            sort_divs.append(data.string)
    
    
    # Two for loops that find the start and the end of the Indexes for Dates and Financial Data Categories
    slicer_begin = 0
    for div in sort_divs:   
        if 'Current' == div:
            break
        slicer_begin += 1
        
    slicer_end = slicer_begin + 1
    for div in sort_divs[slicer_begin:]:
        if 'Enterprise Value/EBITDA' == div:
            break
        slicer_end += 1
        
    # Isolate the dates and categories
    isolated_data = sort_divs[slicer_begin:slicer_end]

    dates = isolated_data[0:5]
    dates.insert(0, 'Quarterly')
    categories = isolated_data[5:]
    
    # Sew all three lists together
    final_list = []
    final_list.append(dates)
    
    for i in range(0, len(table_data)-1):
        row = list(table_data[i])
        row.insert(0, categories[i])
        final_list.append(row)
        
    # Reformat into Pandas DF
    valuation = transpose_df(final_list)
    
    return valuation