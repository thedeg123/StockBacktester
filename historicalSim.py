#!/usr/bin/env python3
from pandas_datareader import data as pdr
import datetime
import pandas as pd
import matplotlib as plt
import fix_yahoo_finance as yf
#KEY = 'A8UQVM3NHRW3MNR9'
today_date=datetime.datetime.today().strftime('%Y-%m-%d')
odl = pd.read_excel("CurrentPortfolio.xlsx")
userData = pd.DataFrame(odl, columns=odl.keys())
panel_data=dict()
for index,stock in userData.iterrows():
    endv = "\n" if (index==userData.iloc[-1:].index[0]) else "\r"
    print("Retreaving data for:",stock.name,end=endv)
    try:
        panel_data[stock.name]=pdr.get_data_yahoo(stock.name, start=stock.Buy, end=today_date)
    except ValueError:
        print("The data for \"", stock.name, "\" are incomplete. Continuing without.")
        continue;
print(panel_data["BABA"].ix["2018-01-02","High"].round(3))
