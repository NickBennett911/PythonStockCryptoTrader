from HelperFunctions import *
from config import *
import keyboard
import time

TICKER = "DOGE"

LoginToRobinhood()

TotalPurchasedUnits = 0     # this only keeps track of how many units have been bought will the program has been running
OutstandingPurchasedUnits = 0   # this keeps track of how many units have been purchased and not sold yet
PurchaseHistory = []    # holds all purchase orders
TotalSoldUnits = 0      # this keeps track of how many units have been sold during the program life
SaleHistory = []        # holds all sale orders

PurchaseMade = False    # if a purchase has been made during
PurchaseInterval = 60 * 60 # can only make purchases every x number of seconds (mins * seconds)
CurPurchaseIntervalStartTime = 0.0  # keeps track of how long we've been in purchase interval
MaxPurchasesPerInterval = 5 # how many transactions can be made every purchase interval
NumPurchasesInInterval = 0 # keep track of how many units have been purchased during purchase interval

TimeStamp = time.time() # get initial time stamp

while 1:

    #check for quit input
    if keyboard.is_pressed("esc"):
        break
    elif keyboard.is_pressed("b"):
        # check the ticker's RSI value to see if we want to make a buy
        TickerInfo = GenerateCryptoInfo(TICKER, SPAN, INTERVAL)
        RSIInfo = TickerInfo["RSI"]
        print("Manual purchase mode entered: \n"
              "Note: type anything that isn't all numbers to exit purchase mode")
        Num = input("How many " + TICKER + " would you like to purchase at the current price of $" + str(CryptoQuote(TICKER)) + " and current RSI of " + str(RSIInfo[-1]) + ": ")
        if (Num.isdigit()):
            PurchaseHistory = ManualBuy(TICKER, int(Num), PurchaseHistory)
            TotalPurchasedUnits += int(Num)
    elif keyboard.is_pressed("s"):
        # check the ticker's RSI value to see if we want to make a buy
        TickerInfo = GenerateCryptoInfo(TICKER, SPAN, INTERVAL)
        RSIInfo = TickerInfo["RSI"]
        print("Manual sell mode entered: \n"
              "Note: type anything that isn't all numbers to exit sell mode")
        Num = input("How many " + TICKER + " would you like to sell at the current price of $" + str(CryptoQuote(TICKER)) + " and current RSI of " + str(RSIInfo[-1]) + ": ")
        if (Num.isdigit()):
            SaleHistory = ManualSell(TICKER, int(Num), SaleHistory)
            TotalSoldUnits += int(Num)


    CurTimeSeconds = time.time()  # get current time
    CurTime = TimeConvert(str(datetime.datetime.now().time()).split('.')[0])

    # update purchasing info
    if PurchaseMade:    # if we made a purchase keep track of purchase interval info
        PurchaseIntervalDt = CurTimeSeconds - CurPurchaseIntervalStartTime
        if PurchaseIntervalDt >= PurchaseInterval:  # we've reached the end of the purchase interval
            PurchaseMade = False
            NumPurchasesInInterval = 0


    CheckIntervalDt = CurTimeSeconds - TimeStamp    # calculate our delta time since our current time stamp

    if CheckIntervalDt >= CheckInterval:    # if check interval period time has passed
        #check the ticker's RSI value to see if we want to make a buy
        TickerInfo = GenerateCryptoInfo(TICKER, SPAN, INTERVAL)
        RSIInfo = TickerInfo["RSI"]

        if ShouldBuy(RSIInfo, LowerThreshold):  # if we should buy during this time check
            # buy desired amount
            if NumPurchasesInInterval <= MaxPurchasesPerInterval:   # we can make a purchase
                NumCanBuy = MaxPurchasesPerInterval - NumPurchasesInInterval

                Order = BuyCryptoByQuantity(TICKER, NumCanBuy)  # purchase however many we can
                PurchaseHistory.append(Order)   # add to our purchase history

                print("PURCHASE MADE AT: "  + CurTime + "\n" +      # print out the purchase info
                      "  Order: " + str(Order) + "\n" +
                      "  RSI Value: " + str(RSIInfo[-1]) + "\n" +
                      "  Units Purchased: " + str(Order['quantity']) + "\n" +
                      "  Unit Price: $" + str(Order['price']) + "\n" +
                      "  Total Cost: $" + str(float(Order['quantity']) * float(Order['price'])))

                TotalPurchasedUnits += NumCanBuy    # increment overall num purchases
                OutstandingPurchasedUnits += NumCanBuy  # increment outstanding number of units

                NumPurchasesInInterval += NumCanBuy     # increment how many we've purchased in the interval

                if not PurchaseMade:    # if this is the start of the purchase interval make sure to set the start time
                    CurPurchaseIntervalStartTime = time.time()
                PurchaseMade = True     # we've made a purchase
            else:
                NumCanBuy = MaxPurchasesPerInterval - NumPurchasesInInterval
                PurchaseIntervalDt = CurTimeSeconds - CurPurchaseIntervalStartTime
                print("!!! Wanted to purchase " + str(NumCanBuy) + " " + TICKER + " at " + CurTime + " but the max purchases per interval (" + str(MaxPurchasesPerInterval) + ") has been reached.")
                print("    " + str(PurchaseInterval - PurchaseIntervalDt) + " seconds left until more " + TICKER + " can be purchased.")

        elif ShouldSell(RSIInfo, UpperThreshold): # if we should sell during this time check
            # sell desired amount
            if OutstandingPurchasedUnits > 0: # make sure that we actually have units that we can sell
                Order = SellCryptoByQuantity(TICKER, OutstandingPurchasedUnits)   # sell all that we've bought to try and make profit
                print("SALE MADE AT: "  + CurTime + "\n"       # print out the sale info
                      "  Order: " + str(Order) + "\n" +
                      "  RSI Value: " + str(RSIInfo[-1]) + "\n" +
                      "  Units Sold: " + str(Order['quantity']) + "\n" +
                      "  Unit Price: $" + str(Order['price']) + "\n" +
                      "  Total Sold: $" + str(float(Order['quantity']) * float(Order['price'])))
                SaleHistory.append(Order)   # add to our sale history
                TotalSoldUnits += OutstandingPurchasedUnits # increment total units sold
                OutstandingPurchasedUnits = 0     # adjust our total purchased units
            else:
                print("!!! Wanted to sell " + TICKER + " with an RSI: " + str(RSIInfo[-1]) + " at " + CurTime + " but we have no avaliable units to sell.")
        else:
            print("Time: " + CurTime + " | Did nothing this interval. RSI value not ideal. Current Checked RSI: " + str(RSIInfo[-1]) + ".")

        TimeStamp = time.time()     # reset the time stamp


# display our closing info at the end once the loop has been shut down
GiveAndSaveClosingInfo(TotalPurchasedUnits, TotalSoldUnits, PurchaseHistory, SaleHistory)

LogoutOfRobinhood()