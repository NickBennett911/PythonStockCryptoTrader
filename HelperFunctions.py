from robin_stocks import robinhood
import pandas as pd
import matplotlib.pyplot as plt
import pyotp
from Credentials import *
import datetime
from config import *

LINEPLOTWIDTH = 10
LINEPLOTHEIGHT = 6

LOOKBACK = 14   # how many SpanIntervals to look back when calculating RSI

def ShouldSell(RSIInfo, UpperThreshold):
    if RSIInfo[-1] >= UpperThreshold:   # if most recent RSI value is above threshold
        return True
    return False

def ShouldBuy(RSIInfo, LowerThreshold):
    if RSIInfo[-1] <= LowerThreshold:   # if most recent RSI value is below threshold
        return True
    return False

def ManualBuy(ticker, Num, history):
    Order = BuyCryptoByQuantity(ticker, Num)  # purchase however many we can
    history.append(Order)  # add to our purchase history

    TickerInfo = GenerateCryptoInfo(ticker, SPAN, INTERVAL)
    RSIInfo = TickerInfo["RSI"]
    CurTime = TimeConvert(str(datetime.datetime.now().time()).split('.')[0])

    print("MANUAL PURCHASE MADE AT: " + CurTime + "\n" +  # print out the purchase info
          "  Order: " + str(Order) + "\n" +
          "  RSI Value: " + str(RSIInfo[-1]) + "\n" +
          "  Units Purchased: " + str(Order['quantity']) + "\n" +
          "  Unit Price: $" + str(Order['price']) + "\n" +
          "  Total Cost: $" + str(float(Order['quantity']) * float(Order['price'])))

    return history

def ManualSell(ticker, Num, history):
    Order = SellCryptoByQuantity(ticker, Num)  # purchase however many we can
    history.append(Order)  # add to our purchase history

    TickerInfo = GenerateCryptoInfo(ticker, SPAN, INTERVAL)
    RSIInfo = TickerInfo["RSI"]
    CurTime = TimeConvert(str(datetime.datetime.now().time()).split('.')[0])

    print("MANUAL SALE MADE AT: " + CurTime + "\n" +  # print out the purchase info
          "  Order: " + str(Order) + "\n" +
          "  RSI Value: " + str(RSIInfo[-1]) + "\n" +
          "  Units Purchased: " + str(Order['quantity']) + "\n" +
          "  Unit Price: $" + str(Order['price']) + "\n" +
          "  Total Cost: $" + str(float(Order['quantity']) * float(Order['price'])))

    return history

def LoginToRobinhood():
    totp = pyotp.TOTP(KEY).now()
    login = robinhood.authentication.login(EMAIL, PASSWORD, mfa_code=CODE)
    return login

def LogoutOfRobinhood():
    robinhood.authentication.logout()

def TimeConvert(miliTime):
    hours, minutes, seconds = miliTime.split(":")
    hours, minutes = int(hours), int(minutes)
    setting = "AM"
    if hours > 12:          # "14:00" -> 2:00pm
        setting = "PM"
        hours -= 12
    elif hours == 12:       # "12:00" -> 12:00pm noon
        setting = "PM"
    elif hours == 0:        # "00:00" -> 12:00am midnight
        hours = 12
    if minutes < 10:
        minutes = "0" + str(minutes)
    return str(hours) + ":" + str(minutes) + setting

def ReformatDate(date):     # date -> yyyy:mm:dd
    year, month, day = date.split("-")
    return month + "/" + day + "/" + year

def CryptoQuote(ticker):
    r = robinhood.get_crypto_quote(ticker.upper())
    #print(ticker.upper() + ": $" + str(r))
    return r['ask_price']

def StockQuote(ticker):
    r = robinhood.get_latest_price(ticker.upper())
    print(ticker.upper() + ": $" + str(r[0]))

def GetCryptoHistorics(ticker, span, interval='None'):
    SpanInterval = {'day' : '5minute', 'week': '10minute', 'month': 'hour'}
    if interval == 'None':
        r = robinhood.get_crypto_historicals(ticker.upper(), interval=SpanInterval[span], span=span)
    else:
        r = robinhood.get_crypto_historicals(ticker.upper(), interval=interval, span=span)

    # remove all the data points that are in the future
    for i in range(len(r) - 1, -1, -1):     # remove the historics data that is in the future
        date = r[i]['begins_at']
        CurrentYear, CurrentMonth, CurrentDay = str(datetime.datetime.now().date()).split('-')
        HistoricsYear, HistoricsMonth, HistoricsDay = date.split('T')[0].split('-')
        chour, cmin, csecond = str(datetime.datetime.now().time()).split('.')[0].split(':')
        dhour, dmin, dsecond = date.split('T')[1].split('Z')[0].split(':')
        if (int(CurrentDay) == int(HistoricsDay) and int(CurrentMonth) == int(HistoricsMonth) and int(CurrentYear) == int(HistoricsYear)):      # if we are on the same day and month
            if (int(chour) < int(dhour)):     # current hour is less than our data point hour
                r.remove(r[i])
            elif (int(chour) == int(dhour) and int(cmin) < int(dmin)):     # current minute is less than our data point minute
                r.remove(r[i])
            elif (span == 'month'):
                if (int(chour)-1 < int(dhour)):  # current hour-1 is less than our data point hour this eliminates the
                                                 # situation where at 9:45pm we have a close price for 9:00pm since there is no close price for 9
                    r.remove(r[i])
        elif (int(CurrentDay) < int(HistoricsDay) and int(CurrentMonth) < int(HistoricsMonth) and int(CurrentYear) < int(HistoricsMonth)):
            r.remove(r[i])

    return r

def BuyCryptoByQuantity(ticker, amount):
    return robinhood.orders.order_buy_crypto_by_quantity(ticker.upper(), amount)

def SellCryptoByQuantity(ticker, amount):
    return robinhood.orders.order_sell_crypto_by_quantity(ticker.upper(), amount)

def GenerateCryptoInfo(ticker, span, interval='None'):
    # our lists necessary for storing all of our data
    dates = []
    times = []
    closePrices = []
    upPrices = []
    downPrices = []
    avg_gain = []
    avg_loss = []
    RS = []
    RSI = []

    if interval == 'None':
        Historics = GetCryptoHistorics(ticker, span)
    else:
        Historics = GetCryptoHistorics(ticker, span, interval)

    # loop through and add to our dates as well as the close price for that day
    for data_point in Historics:
        DayAndTime = data_point["begins_at"].split("Z")[0]
        Date, Time = DayAndTime.split("T")
        dates.append(ReformatDate(Date))
        times.append(TimeConvert(Time))
        closePrices.append(float(data_point["close_price"]))

    # loop through close prices to generate the upPrices and downPrices
    for i in range(len(closePrices)):
        if i == 0:  # since this will be our first data point we have no previous to go back to so we fill with zeros
            upPrices.append(0)
            downPrices.append(0)
        else:
            if (closePrices[i] - closePrices [i - 1]) > 0:  # if our current close price is higher than previous close price
                upPrices.append(closePrices[i] - closePrices[i - 1])
                downPrices.append(0)
            else:  # current close price is lower than previous
                upPrices.append(0)
                downPrices.append(closePrices[i] - closePrices[i - 1])

    #  Loop to calculate the average gain and loss
    for i in range(len(upPrices)):
        if i < LOOKBACK+1:  # we have a spans worth of history but we only want to take into account the lookback time
            avg_gain.append(0)
            avg_loss.append(0)
        else:
            sumGain = 0
            sumLoss = 0
            y = i - LOOKBACK
            while y <= i:  # sum up the average gain and lose over the lookback period
                sumGain += upPrices[y]
                sumLoss += downPrices[y]
                y += 1
            avg_gain.append(sumGain / LOOKBACK)       # total sum /
            avg_loss.append(abs(sumLoss / LOOKBACK))

    #  Loop to calculate RSI and RS
    for i in range(len(closePrices)):
        if i < LOOKBACK+1:  # ignore anything that is not within our lookback period
            RS.append(0)
            RSI.append(0)
        else:
            RSvalue = (avg_gain[i] / avg_loss[i])       # relative strength
            RS.append(RSvalue)
            RSI.append(100 - (100 / (1 + RSvalue)))     # relative strenght index

    # dict to save our data into our chart
    DataDict = {
        'Dates': dates,
        'Times': times,
        'closePrices': closePrices,
        'upPrices': upPrices,
        'downPrices': downPrices,
        'AvgGain': avg_gain,
        'AvgLoss': avg_loss,
        'RS': RS,
        'RSI': RSI
    }

    return DataDict

def CheckAccuracy(info, ticker):
    #  Code to test the accuracy of the RSI at predicting stock prices
    Compare_Stocks = pd.DataFrame(
        columns=["Company", "Hours_Observed", "Crosses", "True_Positive", "False_Positive", "True_Negative",
                 "False_Negative", "Sensitivity",
                 "Specificity", "Accuracy", "TPR", "FPR"])
    prices = info["closePrices"]
    RSI = info["RSI"]
    Hours_Observed = LOOKBACK + 1
    Crosses = 0             # number of times the RSI crosses the 30 or 70 line
    nothing = 0             # number of times the check does for cross fails
    True_Positive = 0       # a cross coming up from the 30 that continues to rise after the cross
    False_Positive = 0      # a cross coming up from the 30 that doesn't continue to rise after the cross
    True_Negative = 0       # a cross coming down from the 70 that continues to fall after the cross
    False_Negative = 0      # a cross coming down from the 70 that doesnt continue to fall after the cross
    Sensitivity = 0
    Specificity = 0
    Accuracy = 0
    while Hours_Observed < len(prices) - 5:
        if RSI[Hours_Observed] <= 30:
            if ((prices[Hours_Observed + 1] + prices[Hours_Observed + 2] + prices[Hours_Observed + 3] + prices[
                Hours_Observed + 4] + prices[Hours_Observed + 5]) / 5) > prices[Hours_Observed]:
                True_Positive += 1
            else:
                False_Negative += 1
            Crosses += 1
        elif RSI[Hours_Observed] >= 70:
            if ((prices[Hours_Observed + 1] + prices[Hours_Observed + 2] + prices[Hours_Observed + 3] + prices[
                Hours_Observed + 4] + prices[Hours_Observed + 5]) / 5) <= prices[Hours_Observed]:
                True_Negative += 1
            else:
                False_Positive += 1
            Crosses += 1
        else:
            # Do nothing
            nothing += 1
        Hours_Observed += 1


    try:
        Sensitivity = (True_Positive / (True_Positive + False_Negative))  # Calculate sensitivity
    except ZeroDivisionError:  # Catch the divide by zero error
        Sensitivity = 0

    try:
        Specificity = (True_Negative / (True_Negative + False_Positive))  # Calculate specificity
    except ZeroDivisionError:
        Specificity = 0

    try:
        Accuracy = (True_Positive + True_Negative) / (
                    True_Negative + True_Positive + False_Positive + False_Negative)  # Calculate accuracy
    except ZeroDivisionError:
        Accuracy = 0

    TPR = Sensitivity  # Calculate the true positive rate
    FPR = 1 - Specificity  # Calculate the false positive rate
    # Create a row to add to the compare_stocks
    add_row = {'Company': ticker.upper(), 'Hours_Observed': Hours_Observed, 'Crosses': Crosses, 'True_Positive': True_Positive,
               'False_Positive': False_Positive,
               'True_Negative': True_Negative, 'False_Negative': False_Negative, 'Sensitivity': Sensitivity,
               'Specificity': Specificity, 'Accuracy': Accuracy, 'TPR': TPR, 'FPR': FPR}
    Compare_Stocks = Compare_Stocks.append(add_row,
                                           ignore_index=True)  # Add the analysis on the stock to the existing Compare_Stocks dataframe


    Compare_Stocks.to_csv("D:\\MySelfProjects\\PythonStockTrading\\" + ticker.upper() + "_RSI_Check.csv", index=False)  # Save the compiled data on each stock to a csv

    return add_row

def SaveGeneratedCryptoInfoToFile(info, ticker):
    # saves the info into a DataFrame structure and saves that into an excel file for us
    # function returns absolute path of file generated
    df = pd.DataFrame(info, columns=['Dates', 'Times', 'closePrices', 'upPrices', 'downPrices', 'AvgGain', 'AvgLoss', 'RS', "RSI"])
    df.to_csv("D:\\MySelfProjects\\PythonStockTrading\\" + ticker.upper() + "_RSI.csv", index=False)
    return "D:\\MySelfProjects\\PythonStockTrading\\" + ticker.upper() + "_RSI.csv"

def ShowRSILineGraph(TickerInfo):
    # LETS VISUALIZE SOME OF THE DATA THAT WE ACQUIRED
    # for our graph lets just chart the RSI values for the start of each day so we dont bog matplotlib down

    dates = TickerInfo["Dates"]
    times = TickerInfo["Times"]
    RSI = TickerInfo["RSI"]

    # modify our dates and rsi so that it is every day so that there isnt as much data and matplot lib doesnt get angry
    modified_RSI = []
    modified_Dates = []
    for i in range(len(RSI)):           # modify to only show the data in our lookback range
        if i >= len(RSI) - LOOKBACK:
            modified_RSI.append(RSI[i])
            modified_Dates.append(dates[i] + " at " + times[i])

    # reverse them since we read through the lists backwards and we still want to data to show up from left to right in order

    # visualize the floor of RSI = 30 and ceiling of RSI = 70
    ceiling = [[modified_Dates[0], modified_Dates[len(modified_RSI)-1]], [70, 70]]
    floor = [[modified_Dates[0], modified_Dates[len(modified_RSI)-1]], [30, 30]]

    # define some import sizes and autolayout features with matplotlib
    plt.rcParams["figure.figsize"] = [LINEPLOTWIDTH, LINEPLOTHEIGHT]
    plt.rcParams["figure.autolayout"] = True

    plt.plot(modified_Dates, modified_RSI, label="RSI Value")
    ax = plt.gca()
    ax.tick_params(axis='x', labelrotation=90)
    plt.plot(ceiling[0], ceiling[1], label="Ceiling", color='green')
    plt.plot(floor[0], floor[1], label="Floor", color='red')
    plt.title('DOGE\'s RSI value vs Given Day and Time')
    plt.xlabel('Date and Time')
    plt.ylabel('RSI Value at start of time')
    plt.legend()
    plt.grid(True)
    plt.show()