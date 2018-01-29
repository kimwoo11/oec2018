import requests
import numpy
import time

def GetStockList():
    r = requests.get('https://oec-2018.herokuapp.com/api/stock/list?key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    if a['success'] == True:
        return a['stock_tickers']
    
def GetCurrentPrice(stock_identifier):
    r = requests.get('https://oec-2018.herokuapp.com/api/stock?ticker=' + stock_identifier + '&key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    if a['success'] == True:
        return a['historical_price']

def BuyStock(stock_identifier, num_shares):
    r = requests.get('https://oec-2018.herokuapp.com/api/buy?ticker=' + stock_identifier + '&shares=' + num_shares + '&key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    return a['success']
    
def SellStock(stock_identifier, num_shares):
    r = requests.get('https://oec-2018.herokuapp.com/api/sell?ticker=' + stock_identifier + '&shares=' + num_shares + '&key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    return a['success']
    
def AccountStatus():
    r = requests.get('https://oec-2018.herokuapp.com/api/account?key=uBFH_Il5adJf50GtyZguAA')
    a = r.json()
    return [a['cash'], a['holdings']]

def PolyFit(x, y, degree): #Fit polynomial to data
    c = numpy.polyfit(x, y, degree)
    return c
    
def PolyVal(coeff, xrange): #Evaluate polynomial at each element of xrange
    return polyval(coeff, xrange)
    
def Loss(A, B): #Loss function that we want to minimize
    sum = 0
    for i in range(len(A)):
        sum += (A[i] - B[i]) ** 2
    return sum
    
def ListMult(l, a): 
    for i in range(len(l)):
        l[i] *= a
    return l
    
def ListSub(l, m):
    for i in range(len(l)):
        l[i] -= m[i]
    return l

def Train(data, degree, slice, section): #Use different weightings for short fit, medium fit and far fit, use gradient descent to optimize weighting
    l = round(len(data) * slice)
    weight = [1 / 3, 1 / 3, 1 / 3]
    increase = [0, 0, 0]
    C = []
    S = []
    trainSet = data[0 : l]
    testSet = data[l : len(data)]
    C[0] = PolyFit(range(l - round(l * section * section), l), data[l - round(l * section * section), l], degree)
    C[1] = PolyFit(range(l - round(l * section), l), data[l - round(l * section), l], degree)
    C[2] = PolyFit(range(0, l), data[0, l], degree)
    S[0] = PolyVal(C[0], range(l, len(data)))
    S[1] = PolyVal(C[1], range(l, len(data)))
    S[2] = PolyVal(C[2], range(l, len(data)))
    error = 1
    while error > 0.01:
        for i in [0, 1, 2]:
            newWeight = weight[:]
            newWeight[i] += 1
            newWeight = ListMult(newWeight, 1 / sum(newWeight))
            increase[i] = Loss(testSet, ListMult(S[0], newWeight[0]) + ListMult(S[1], newWeight[1]) + ListMult(S[2], newWeight[2]) - Loss(testSet, ListMult(S[0], Weight[0]) + ListMult(S[1], Weight[1]) + ListMult(S[2], Weight[2]))
        weight = ListSub(weight, increase)
        weight = ListMult(weight, 1 / sum(weight))
    return [weight, C[0], C[1], C[2]]
    
def Operate(degree, slice, section, future):
    stocks = GetStockList()
    owned = AccountStatus()
    cash = owned[0]
    stuffs = owned[1]
    best = ''
    max = 0
    min = 0
    worst = ''
    for stock in stocks:
        price = GetCurrentPrice(stock)
        [Weight, C[0], C[1], C[2]] = Train(price, degree, slice, section)
        result = Weight[0] * PolyVal(C[0], len(price) - 1 + future) + Weight[1] * PolyVal(C[1], len(price) - 1 + future) + Weight[2] * PolyVal(C[2], len(price) - 1 + future)
        if result > max:
            max = result
            best = stock
        else if result < min:
            min = result
            worst = stock
    BuyStock(best, 1)
    SellStock(worst, 1)
    
degree = 5
slice = 0.8
section = 0.15
future = 5

currTime = time.time()
while time.time() - currTime > 60:
    currTime = time.time()
    operate(degree, slice, section, future)
    
    