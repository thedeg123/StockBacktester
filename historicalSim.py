#!/usr/bin/env python3
from pandas_datareader import data as pdr
from datetime import datetime, timedelta
from numpy import round, arange, where, array
from dateutil.relativedelta import relativedelta
from pandas.tseries.holiday import USFederalHolidayCalendar
import pandas as pd
import sys
import matplotlib.pyplot as plt
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
def __getMetric__(userData, data):
    '''
    Takes in a dataframe and gets metrics for it. Helper program for __calculateMetrics__
    '''
    userData["purchasePrice"] = data.ix[0,"close"]
    userData["sellPrice"] = data.ix[-1,"close"]
    userData["purchaseVal"] = data.ix[0,"close"] * userData["Shares"]
    userData["currentVal"] = data.ix[-1,"close"] * userData["Shares"]
    #Getting the beta
    userData["Beta"] = round((userData["currentVal"] - userData["purchaseVal"]), 2)
    userData["pBeta"] = userData["Beta"] / userData["purchaseVal"]
    return userData
def __calculateMetrics__(data, userData):
    '''
    Prints portfolio metrics.
    '''
    for (ticker,sdata) in data:
        ndat = __getMetric__(userData.loc[ticker].copy(), sdata)
        userData = userData.reindex(ndat.index, axis=1)
        userData.loc[ticker] = ndat
        startd = userData.ix[ticker, "Buy"]
        endd = userData.ix[ticker, "Sell"]
        print(ticker, "Change of: ", userData.ix[ticker,"Beta"] , "over", (endd - startd).days, "days with",\
        userData.ix[ticker, "Shares"], "shares.")
    return userData
def graphData(userData, compdat, portb, compb):
    elements = userData.shape[0] +2
    width = 1/elements
    colors = where(userData["Beta"]>=0, 'blue','red').tolist()
    graphdata= userData["pBeta"].tolist() + [portb, compb]
    p1 = plt.bar(arange(elements), graphdata, width, color = (colors + ['yellow', 'green']))
    plt.ylabel("%beta")
    plt.yticks(arange(min(graphdata),max(graphdata)+0.01,max(graphdata)/10))
    plt.xticks(arange(elements),((userData.index).tolist() + ["portfolio Beta", "S&P 500"]))
    plt.show()

def stockRetrace(file):
    '''
    Finds portfolio change. comp is for alpha.
    '''
    fin = pd.read_excel("CurrentPortfolio.xlsx")
    userData = __fixDates__(pd.DataFrame(fin, columns=fin.keys()))
    panel_data=dict()
    for index,stock in userData.iterrows():
        endv = "\n" if (index==userData.iloc[-1:].index[0]) else "\r"
        print("Retreaving data for:",stock.name,end=endv)
        try:
            pdat = pdr.DataReader(stock.name,'iex', start=stock.Buy, end=stock.Sell)
            panel_data[stock.name] = pdat.drop(pdat.index[1:-1])
        except ValueError:
            print("The data for \"", stock.name, "\" are incomplete. Continuing without.")
            continue;
        except KeyError:
            print("The ticker \"", stock.name, "\" was not found. Continuing without.", sep='')
            continue;
    userData = __calculateMetrics__(panel_data.items(), userData)
    #portfolioBeta
    portb = (userData["currentVal"].sum() - userData["purchaseVal"].sum())/ userData["purchaseVal"].sum()
    #Generating alpha based off spy (s&p index) and when first stock was bought and last was sold.
    compdat = pdr.DataReader(COMPVAL,'iex', start=userData['Buy'].min(), end=userData['Sell'].max())
    compb=((compdat.ix[-1, "close"] - compdat.ix[0,"open"])/ compdat.ix[0,"open"])
    print("Net beta: $", userData["Beta"].sum(), " or ", round(portb,2),"%", sep='')
    print("Net alpha: ", round((portb-compb)*100, 2), "%", sep='')
    graphData(userData, compdat, portb, compb)
    return round(portb-compb, 2)
    #print(panel_data, userData.head())
if __name__=='__main__':
    stockRetrace(sys.argv[1:])
