import requests
import random
import math
import time
import matplotlib
import matplotlib.pyplot as plt

def GetStockList():
    '''
    output: a list of all stock names
    '''
    r = requests.get('https://oec-2018.herokuapp.com/api/stock/list?key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    if a['success'] == True:
        return a['stock_tickers']
    
def GetCurrentPrice(stock_identifier):
    '''
    stock_identifier: a string
    output: a list of historical data
    '''
    r = requests.get('https://oec-2018.herokuapp.com/api/stock?ticker=' + stock_identifier + '&key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    if a['success'] == True:
        return a['historical_price']

def GetCurrentPrice2(stock_identifier,window):
    '''
    stock_identifier: a string
    window: an integer
    output: a list of the last "window" number of historical data
    '''
    r = requests.get('https://oec-2018.herokuapp.com/api/stock?ticker=' + stock_identifier + '&key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    if a['success'] == True:
        return a['historical_price'][-1-window:-1]

def Cash():
    '''
    output: current cash value in cents
    '''
    r = requests.get('https://oec-2018.herokuapp.com/api/account?key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    if a['success'] == True:
        return a['cash']

def asset():
    return Cash()+Holdings3()
        
def Holdings():
    '''
    output: list of dictionaries: one dictionary per held stock
    '''
    r = requests.get('https://oec-2018.herokuapp.com/api/account?key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    if a['success'] == True:
        return a['holdings']

def Holdings2():
    '''
    output: a dicationary with stock identifier and number
    '''
    res={}
    list=Holdings()
    for i in list:
        res[ i['ticker'] ]=i['shares']
    return res

def Holdings3():
    '''
    output: a dicationary with stock identifier and number
    '''
    res=0
    list=Holdings()
    for i in list:
        res+=i["market_value"]
    return res

def GetallPrice():
    '''
    output1: a list of all stocks available on market
    output2: a dictionary of all stocks with historical data
    '''
    identifiers=GetStockList()
    res={}
    for i in identifiers:
        res[i]=GetCurrentPrice(i)
    return identifiers,res
    
def GetallPrice2(window):
    '''
    window: an integer number
    output1: a list of all stocks available on market
    output2: a dictionary of all stocks with historical data
    '''
    identifiers=GetStockList()
    res={}
    for i in identifiers:
        res[i]=GetCurrentPrice2(i,window)
    return identifiers,res

def BuyStock(stock_identifier, num_shares):
    '''
    stock_identifier: a string
    num_shares: a string of a number
    output: if transaction is successful
    '''
    r = requests.get('https://oec-2018.herokuapp.com/api/buy?ticker=' + stock_identifier + '&shares=' + num_shares + '&key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    return a['success']

def SellStock(stock_identifier, num_shares):
    '''
    stock_identifier: a string
    num_shares: a string of a number
    output: if transaction is successful
    '''
    r = requests.get('https://oec-2018.herokuapp.com/api/sell?ticker=' + stock_identifier + '&shares=' + num_shares + '&key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    return a['success']

def plotstock(stock_identifier):
    '''
    stock_identifier: a string
    output: a graph
    '''
    plt.figure()
    price=GetCurrentPrice(stock_identifier)
    plt.plot(price)
    plt.title(stock_identifier)
    plt.show()
    return

def plotallstock():
    '''
    output: graphs are saved in directory
    '''
    #matplotlib.use('Agg')
    id=GetStockList()
    for i in id:
        plt.plot(GetCurrentPrice(i))
        plt.title(i)
        plt.savefig(i)
        plt.close()
    return

def smooth(his,smoother):
    '''
    his: a list of historical data
    smoother: an integer
    output: a list of smoothed data
    '''
    res=his
    for i in range(len(his)):
        res[i]=sum(his[-smoother-i:-i])/smoother
    return res[smoother//2:-smoother//2]
    
def scorebuy(current,prices,para):
    '''
    para is a list of parameters
    [mark1,mark2,mark3]
    buy the one with highest positive
    '''
    slopeInitial = prices[1] - prices[0]
    slopeFinal = prices[-1] - prices[-2]
    score=0
    if slopeFinal!=0:
        score+=slopeFinal/abs(slopeFinal)*para[0]
    if slopeInitial!=0:
        score+=slopeInitial/abs(slopeInitial)*para[1]
    return score-current/para[2]
    

def modify(para,old,new):
    '''
    modifying the parameters used in score function
    '''
    res=para
    if new<old:
        res[random.randint(0,2)]+=-1+2*random.random()
    return res
    
def BestAlgorithm(p):
    '''
    using the score function to determine the best buying option out of five ones
    '''
    stocks = GetStockList()
    n = len(stocks)
    scoremax=p['scoremax']
    scoremin=p['scoremin']
    stockmin=''
    stockmax=''
    pricemax=0
    pricemin=0
    currHoldings = Holdings2() #dictionary with the holdings we have
    for i in range(p['nStocks']): 
        currStock = stocks[math.floor(random.random() * n)] #Get a random stock
        prices = GetCurrentPrice2(currStock, p['window']) #Get prices for the stock
        current=prices[-1]
        prices = smooth(prices, p['smoother']) #Smooth the prices
        scorecur=scorebuy(current,prices,p['para'])
        print(scorecur)
        if(scoremax<scorecur):
            scoremax=scorecur
            stockmax=currStock
            pricemax=current
        if currStock in currHoldings.keys() and currHoldings[currStock] // p['sell']>0 and scoremin>scorecur:
            scoremin=scorecur
            stockmin=currStock
            pricemin=current
    if stockmin!='':
        SellStock(currStock, str( currHoldings[currStock] // p['sell'] )) #Sell half of the stocks. MODIFY LATER
        print("sell"+currStock)
    if stockmax!='':
        BuyStock(stockmax, str( math.floor(p['buy'] * Cash()//currmin ) ))
        print("buy"+currStock)
    
    
if __name__=='__main__':
    p={'window':20,'nStocks':5,'smoother':3,'scoremax':0,'scoremin':0,'para':[10,10,10],'sell':2,'buy':0.2}
    t=time.time()
    old=asset()
    while(1):
        if time.time()-t>1000:
            new=asset()
            p['para']=modify(p['para'],old,new)
            t=time.time()
            old=new
        BestAlgorithm(p)