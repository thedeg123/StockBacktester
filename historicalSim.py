#!/usr/bin/env python3
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
from numpy import round
from dateutil.relativedelta import relativedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
import pandas as pd
import sys
import matplotlib as plt
COMPVAL = 'SPY'

def scrubDate(date):
    '''
    Accounting for user data on weekends or holidays. IE, dates when markets are not open.
    If the given day is one of the above, days are stripped off until mkts were open.
    '''
    today=datetime.now()
    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start=(today - relativedelta(years=5)), end=today).to_pydatetime()
    today=datetime.today().strftime('%Y-%m-%d')
    uDate = date if isinstance(date,datetime) else datetime.strptime(today, '%Y-%m-%d')
    while(uDate in holidays):
        #If date was a holiday
        uDate = uDate - timedelta(days=1)
    if uDate.weekday()>4:
        #If date was a weekend
        uDate = uDate - timedelta(days=(uDate.weekday()-4))
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
def __getMetrics__(userData, data):
    '''
    Takes in a dataframe and gets metrics for it. Helper program for __calculateMetrics__
    '''
    ticker = userData.index[0]
    userData["purchaseVal"] = data.ix[0,"close"] * userData["Shares"]
    userData["currentVal"] = data.ix[1,"close"] * userData["Shares"]
    #Getting the beta
    userData["Beta"] = (userData["currentVal"] - userData["purchaseVal"]).round(3)
    userData["pBeta"] = userData["Beta"] / data.ix[0,"close"]
    return userData
def __calculateMetrics__(data, userData):
    '''
    Prints portfolio metrics.
    '''
    for (ticker,data) in data:
        print(userData)
        userData.update(__getMetrics__(userData, data))
        startd = userData.ix[ticker, "Buy"]
        endd = userData.ix[ticker, "Sell"]
        print(ticker, "Change of: ", userData.ix[ticker, "Beta"] , "over", (endd - startd).days, "days with",\
        userData.ix[ticker, "Shares"], "shares.")

    print("Net change of:",userData["Beta"].sum(), "over", (userData['Sell'].max()-userData['Buy'].min()).days, "days.")

def stockRetrace(file):
    '''
    Finds portfolio change. comp is for alpha.
    '''
    fin = pd.read_excel("CurrentPortfolio.xlsx")
    userData = __fixDates__(pd.DataFrame(fin, columns=fin.keys()))
    panel_data=dict()
    for index,stock in userData.iterrows():
        endv = "\n" if (index==userData.iloc[-1:].index[0]) else "\n"
        print("Retreaving data for:",stock.name,end=endv)
        try:
            dates = [pdr.DataReader(stock.name,'iex', start=stock.Buy, end=stock.Buy), \
            pdr.DataReader(stock.name,'iex', start=stock.Sell, end=stock.Sell)]
            panel_data[stock.name] = pd.concat(dates)
        except ValueError:
            print("The data for \"", stock.name, "\" are incomplete. Continuing without.")
            continue;
    __calculateMetrics__(panel_data.items(), userData)
    #Generating alpha based off spy (s&p index) and when first stock was bought and last was sold.
    print(userData)

    compalph = pdr.DataReader(COMPVAL,'iex', start=userData['Buy'].min(), end=userData['Sell'].max())
    #print(panel_data, userData.head())
if __name__=='__main__':
    stockRetrace(sys.argv[1:])
