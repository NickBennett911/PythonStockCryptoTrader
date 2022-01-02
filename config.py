import datetime
import HelperFunctions

### Time/Interval settings ###
SPAN = 'week'  # how far back we are looking
INTERVAL = '5minute'    # how often we get past info
CheckInterval = 2 * 60 # we want to check if we want to purchase or sell every x number of seconds (mins * seconds)

### Threshold settings ###
UpperThreshold = 70.0
LowerThreshold = 30.0

def GiveAndSaveClosingInfo(TotalPurchasedUnits, TotalSoldUnits, PurchaseHistory, SaleHistory):
    # print all the useful info from the programs lifetime including all buy and sell transactions with details on each
    # as well as general overall info at the very end
    print("\nCalculating Stats...")

    print("\n------- Purchase History and Info -------")
    RunningCostTotal = 0.0
    RunningUnitTotal = 0
    for i in range(len(PurchaseHistory)):
        print("----------- Purchase " + str(i) + " -----------")
        NumUnits = float(PurchaseHistory[i]['quantity'])
        UnitPrice = float(PurchaseHistory[i]['price'])
        print(PurchaseHistory[i])
        print("Summary of above purchase:\n"
              "Number of Units Purchased: " + str(NumUnits) + "\n"
              "Price Per Unit: " + str(UnitPrice) + "\n"
              "Total Cost: " + str(NumUnits * UnitPrice))
        RunningCostTotal += NumUnits * UnitPrice
        RunningUnitTotal += NumUnits
    print("\nTotal Cost of All Units: $" + str(RunningCostTotal))
    print("Total Number of Units Purchased: " + str(RunningUnitTotal))

    print("\n------- Sell History and Info -------")
    RunningSellCost = 0.0
    RunningUnitSale = 0
    for i in range(len(SaleHistory)):
        print("----------- Sale " + str(i) + " -----------")
        NumUnits = float(SaleHistory[i]['quantity'])
        UnitPrice = float(SaleHistory[i]['price'])
        print(SaleHistory[i])
        print("Summary of above sale:\n"
              "Number of Units Sold: " + str(NumUnits) + "\n"
              "Price Per Unit: " + str(UnitPrice) + "\n"
              "Total Sale Price: " + str(NumUnits * UnitPrice))
        RunningSellCost += NumUnits * UnitPrice
        RunningUnitSale += NumUnits
    print("\nTotal Return on All Units Sold: $" + str(RunningSellCost))
    print("Total Number of Units Sold: " + str(RunningUnitSale))

    print("\n------- Overall History and Info -------")
    print("Total Units Purchased: " + str(TotalPurchasedUnits))
    print("Total Units Sold: " + str(TotalSoldUnits))
    print("Total Spent: $" + str(RunningCostTotal) + ", on " + str(RunningUnitTotal) + " units in total")
    print("Total Sold: $" + str(RunningSellCost) + ", from " + str(RunningUnitSale) + " total units sold")
    print("Net Total at End: $" + str(RunningSellCost - RunningCostTotal))

    ### SAVE ALL OF OUR DATA TO HISTORY FILE ###
    File = open("TradingHistory.txt", "a")
    CurDateTime = str(datetime.datetime.now()).split(" ")
    File.write("\n----------------------------\n")
    File.write("Trading Session Finish Time: " + FormatDateTime(CurDateTime[0], CurDateTime[1]) + "\n")
    File.write("------- Purchase History and Info -------\n")
    RunningCostTotal = 0.0
    RunningUnitTotal = 0
    for i in range(len(PurchaseHistory)):
        File.write("----------- Purchase " + str(i) + " -----------\n")
        NumUnits = float(PurchaseHistory[i]['quantity'])
        UnitPrice = float(PurchaseHistory[i]['price'])
        File.write(str(PurchaseHistory[i]) + "\n")
        File.write("Summary of above purchase:\n"
              "Number of Units Purchased: " + str(NumUnits) + "\n"
              "Price Per Unit: " + str(UnitPrice) + "\n"
              "Total Cost: " + str(NumUnits * UnitPrice) + "\n")
        RunningCostTotal += NumUnits * UnitPrice
        RunningUnitTotal += NumUnits
    File.write("\nTotal Cost of All Units: $" + str(RunningCostTotal) + "\n")
    File.write("Total Number of Units Purchased: " + str(RunningUnitTotal) + "\n")

    File.write("\n------- Sell History and Info -------\n")
    RunningSellCost = 0.0
    RunningUnitSale = 0
    for i in range(len(SaleHistory)):
        File.write("----------- Sale " + str(i) + " -----------\n")
        NumUnits = float(SaleHistory[i]['quantity'])
        UnitPrice = float(SaleHistory[i]['price'])
        File.write(str(SaleHistory[i]) + "\n")
        File.write("Summary of above sale:\n"
              "Number of Units Sold: " + str(NumUnits) + "\n"
              "Price Per Unit: " + str(UnitPrice) + "\n"
              "Total Sale Price: " + str(NumUnits * UnitPrice) + "\n")
        RunningSellCost += NumUnits * UnitPrice
        RunningUnitSale += NumUnits
    File.write("\nTotal Return on All Units Sold: $" + str(RunningSellCost) + "\n")
    File.write("Total Number of Units Sold: " + str(RunningUnitSale) + "\n")

    File.write("\n------- Overall History and Info -------\n")
    File.write("Total Units Purchased: " + str(TotalPurchasedUnits) + "\n")
    File.write("Total Units Sold: " + str(TotalSoldUnits) + "\n")
    File.write("Total Spent: $" + str(RunningCostTotal) + ", on " + str(RunningUnitTotal) + " units in total\n")
    File.write("Total Sold: $" + str(RunningSellCost) + ", from " + str(RunningUnitSale) + " total units sold\n")
    File.write("Net Total at End: $" + str(RunningSellCost - RunningCostTotal) + "\n")

def FormatDateTime(Date, Time):
    NewDate = HelperFunctions.ReformatDate(Date)
    NewTime = HelperFunctions.TimeConvert(Time.split(".")[0])
    return str(NewDate + " " + NewTime)