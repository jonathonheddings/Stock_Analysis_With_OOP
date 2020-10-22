import streamlit as st
import time
import numpy as np
import pandas as pd
import stock_class

START, END = '2020-01-01', '2020-06-01'


def price_over_time(stock, start=START, end=END, show=True):

    st.write(
        """ ## Price Over Time
        """)
    st.line_chart(stock.data['Adj Close'])

    if show:
        st.write(stock.data.tail())


def rolling_avg(stock, start=START, end=END, period='20', show=True):
    
    if stock.weekly_returns.empty:
        stock.get_rolling()
    
    st.write(
        """ ## Rolling Avg
        """)
    st.line_chart(stock.rolling_avg[period])

    if show:
        st.write(stock.rolling_avg[period].tail())


def weekly_returns(stock, start=START, end=END, show=True):
    
    st.write(
        """ ## Price Over Time
        """)
    st.line_chart(stock.data['Adj Close'])

    if show:
        st.write(stock.data.tail())

def show_graphs(graphs_multiselect):
    
    if ("Price/Time" in graphs_multiselect):
        price_over_time(stock, show=show_df)
    
    if ("Weekly Returns" in graphs_multiselect):
        weekly_returns(stock, show=show_df)
    
    if ("Rolling Avg" in graphs_multiselect):
        rolling_avg(stock, show=show_df)
        
def income_stmt(stock):
    
    st.write(
        """ ## Income Statement
        """)
    
    st.write(stock.statement('income'))

def balance_sheet(stock):
    
    st.write(
        """ ## Balance Sheet
        """)
    
    st.write(stock.statement('balance'))

    
def cash_flows(stock):
    
    st.write(
        """ ## Statement of Cash Flows
        """)
    
    st.write(stock.statement('cashflow'))


def show_fin_stmts(stmt_multiselect):
    
    if ("Income Statement" in stmt_multiselect):
        income_stmt(stock)
    
    if ("Balance Sheet" in stmt_multiselect):
        balance_sheet(stock)
    
    if ("Statement of Cash Flows" in stmt_multiselect):
        cash_flows(stock)
    

ticker = st.sidebar.text_input("Enter Stock Ticker", value='SPY')

stock = stock_class.Stock(ticker, START, END)

st.title("Stock Analysis - " + str(stock.ticker))

st.sidebar.title("Create Your Stock Report")
graphs_multiselect = st.sidebar.multiselect(
    "Graph A Relationship",
    ("Price/Time", "Rolling Avg"))

show_df = st.sidebar.checkbox('Show dataframes')

stmt_multiselect = st.sidebar.multiselect(
    "Pull Financial Statement Information",
    ("Income Statement", "Balance Sheet", "Statement of Cash Flows", "Valuation"))

show_graphs(graphs_multiselect)

show_fin_stmts(stmt_multiselect)
    
st.button("Re-run")
