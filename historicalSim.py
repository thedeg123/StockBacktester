#!/usr/bin/env python3
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
from numpy import round
from dateutil.relativedelta import relativedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
import pandas as pd
import sys
import matplotlib as plt
COMPVAL = 'spx'

def scrubDate(date):
    '''
    Accounting for user data on weekends or holidays. IE, dates when markets are not open.
    If the given day is one of the above, days are stripped off until mkts were open.
    '''
    today=datetime.now()
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start=(today - relativedelta(years=5)), end=today).to_pydatetime()
    today=datetime.today().strftime('%Y-%m-%d')
    uDate = date if not pd.isnull(date) else \
    datetime.strptime(today, '%Y-%m-%d')
    while(uDate in holidays):
        #print("Date:", uDate.strftime('%Y-%m-%d'), "was a holiday. Instead using ", end="")
        uDate= uDate - timedelta(days=1)
        #print(uDate)
    if uDate.weekday()>4:
        #print("Date:", uDate.strftime('%Y-%m-%d'), "was a weekend. Instead using ", end="")
        uDate = uDate - timedelta(days=(uDate.weekday()-4))
        #print(uDate)
    return uDate
def __fixDates__(data):
    '''
    Updates each date to be not a weekend or Holiday
    '''
    for (i,buy) in enumerate(data['Buy']):
        data.ix[i,'Buy']= scrubDate(buy)
    for (i,sell) in enumerate(data['Sell']):
        data.ix[i,'Sell']= scrubDate(sell)
    return data

def __printBeta__(data, userData):
    netChange = 0;
    lowd = datetime.today();
    newd = datetime(1000,1,1)
    for (ticker,data) in data:
        startd= scrubDate(userData.ix[ticker, "Buy"])
        endd = scrubDate(userData.ix[ticker, "Sell"])
        change = ((data.ix[1,"close"] - data.ix[0,"close"] -0) * userData.ix[ticker, "Shares"]).round(3)
        netChange+=change
        lowd = min(lowd,startd)
        newd = max(newd,endd)
        print(ticker, "Change of: ", change, "over", (endd - startd).days, "days with",\
        userData.ix[ticker, "Shares"], "shares.")
    print("Net change of:",netChange, "over", (newd-lowd).days, "days.")
def genBeta(file,comp):
    fin = pd.read_excel("CurrentPortfolio.xlsx")
    userData = __fixDates__(pd.DataFrame(fin, columns=fin.keys()))
    panel_data=dict()
    for index,stock in userData.iterrows():
        endv = "\n" if (index==userData.iloc[-1:].index[0]) else "\r"
        print("Retreaving data for:",stock.name,end=endv)
        try:
            dates = [pdr.DataReader(stock.name,'iex', start=stock.Buy, end=stock.Buy), \
            pdr.DataReader(stock.name,'iex', start=stock.Sell, end=stock.Sell)]
            panel_data[stock.name] = pd.concat(dates)
        except ValueError:
            print("The data for \"", stock.name, "\" are incomplete. Continuing without.")
            continue;
    __printBeta__(panel_data.items(), userData)
    #print(panel_data, userData.head())
if __name__=='__main__':
    genBeta(sys.argv[1:], COMPVAL)
