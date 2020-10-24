import streamlit as st
import numpy as np
import pandas as pd
import stock_class

START, END = '2020-01-01', '2020-06-01'

## The following functions are defined for different modules that can be added and removed for tailor made reports
##
def price_over_time(stock, start=START, end=END, show=True):
    
    st.write(
        """ ## Historical Price Chart
        """)
    
    if stock.weekly_returns.empty:
        stock.get_rolling()
        
    col1, col2 = st.beta_columns([7,1])

    period = col2.radio(label='Trailing Avg', options=['5', '20', '30'], index=0)
    chart_data = pd.merge(stock.data['Adj Close'], stock.rolling_avg[period], left_index=True, right_index=True)
    col1.line_chart(chart_data)
    
    col1.select_slider("Date Range (Currently Does Nothing)", ["Max", "5Y", "3Y", "1Y", "6M", "3M", "1M", "Week"], value="6M")
    
    st.write("""Sample Text: This Stock has hit - lows and - highs during the - period
            The overall trend during this period has been positive/negative with a return of -%""")

    if show:
        st.write(stock.data.tail())


def weekly_returns(stock, start=START, end=END, show=True):
    
    st.write(
        """ ## Weekly Returns
        """)
    st.line_chart(stock.get_returns())

    if show:
        st.write(stock.weekly_returns.tail())

def show_graphs(graphs_multiselect, stock, show_df):
    
    if ("Price/Time" in graphs_multiselect):
        price_over_time(stock, show=show_df)
    
    if ("Weekly Returns" in graphs_multiselect):
        weekly_returns(stock, show=show_df)
    
        
def income_stmt(stock):
    
    st.write(
        """ ## Income Statement
        """)
    st.write("""This is the profit and loss statement, 
        it focuses on the company’s revenues and expenses 
        during a particular period.""")
    
    st.write(stock.statement('income').T)

def balance_sheet(stock):
    
    st.write(
        """ ## Balance Sheet
        """)
    st.write("""This reports a company's assets, liabilities, and shareholders' equity
                at a specific point in time, and provides a basis for computing fundamental ratios.""")
    
    st.write(stock.statement('balance').T)

    
def cash_flows(stock):
    
    st.write(
        """ ## Statement of Cash Flows
        """)
    st.write("""This is the net amount of cash and equivalents transferred 
             into and out of the business. A company’s ability 
             to create value for shareholders can be seen through its ability to generate positive cash flows.""")
    
    st.write(stock.statement('cashflow').T)


def show_fin_stmts(stmt_multiselect, stock, show_explanations):
    
    if ("Income Statement" in stmt_multiselect):
        income_stmt(stock)
    
    if ("Balance Sheet" in stmt_multiselect):
        balance_sheet(stock)
    
    if ("Statement of Cash Flows" in stmt_multiselect):
        cash_flows(stock)
    