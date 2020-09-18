# Defines a Stock and Portfolio Class with many Technical Analysis Functions

This is a package made up of Stock and Portfolio Objects, that give you access to many stock data manipulating functions, making technical and fundamental analysis a breeze.

## So Far For Stocks It Includes:
* Graphing (Also Pulls Data That Can Be Accessed)
    * Price Over Time
    * Weekly Returns
    * GBM Monte Carlo Price Simulation Over Time
    * Rolling Averages
* Income Statement, Balance Sheet, Statement of Cash Flows, and Valuation Analysis
    ----  These are webscraped from Yahoo Finance and can be exported to CSV
* OLS Regression Against S&P / Beta Calculation Using Covariance Over Variance
* Convert Summary Statistics and Basic Info to JSON variable, export it, save it, print it
  
## So Far For Portfolios It Includes:
* Creating a Portfolio Object full of Stock Objects, from a list of tickers and portfolio weights
   * It loads Stock Objects based on all tickers given, and holds an overall balance
* All functions that come with the stock object can be used on individual stocks within the portfolio

stock_class.py holds the Stock and Portfolio Objects
fin_statements.py is a header file for the stock_class object file, that provides the financial statement webscraping for fundamental analysis
FinancialFunctions.py is a header file for the stock_class object file that provides a variety of Finance functions that manipulate stock data, from weekly returns and graphing, to monte carlos and rolling averages.
