from HelperFunctions import *
import datetime


TICKER = "DOGE"
SPAN = 'month'  # how far back we are looking
INTERVAL = 'hour'    # how often we get past info

LoginToRobinhood()

### Demonstration of just using the Helper Functions ###
TickerInfo = GenerateCryptoInfo(TICKER, SPAN, INTERVAL)
SaveGeneratedCryptoInfoToFile(TickerInfo, TICKER)
CheckAccuracy(TickerInfo, TICKER)
ShowRSILineGraph(TickerInfo)

LogoutOfRobinhood()