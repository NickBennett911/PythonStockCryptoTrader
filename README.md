# PythonStockCryptoTrader
Neat little bot I made to buy and sell a given TICKER based on that TICKER's RSI value

Pre-requisites:
  Robin Stocks API installed (https://robin-stocks.readthedocs.io/en/latest/install.html)
  MatPlotLib library installed (https://matplotlib.org/stable/users/installing/index.html)
  DateTime library installed (https://pypi.org/project/DateTime/)
  Pandas library installed (https://pandas.pydata.org/docs/getting_started/install.html)
  Pyotp library installed (https://pypi.org/project/pyotp/)
  Keyboard library installed (https://pypi.org/project/keyboard/)
  
 Once all libraries have been installed and referenced correctly in the project space you're using you'll be able to run the program.
 
 STEP 1:
 I would recommend checking out TradingFunctionsDemonstration.py first and getting that running first. This is so that you can see what some of the main functions I have do
 and so you'll be able to get your Robinhood access set up correctly. For this I would make sure to check out the robin stocks website as they have a nice explination
 on how to get things all set up and logged in.
 
 Once you get things set up correctly you'll notice the RSI line graph pop up as well as the RSI and RSI_CHECK spreadsheet files getting updated. You can check all three 
 of those resources as since they will all contain unique and potentailly useful information.
 
 After that I would recommend looking through the HelperFunctions.py file and atleast glance over all those functions so that you will know what they're doing when looking at
 Trader.py. When looking at Trader.py make sure to read all the comments and esspecially all the variables at the top of the file. The variables at the top of the file are a bulk
 of the variables and parameters that can be adjusted to suit you're specific crypto or stock.
 
 Once everything is up and running helpful information will get printed to the terminal window while the bot is running and "b" can be pressed to enter manual buy mode and "s"
 can be pressed to enter manual sell mode and escape can be pressed to exit the program. When exited with escape a summary of the bots run will get printed as well as 
 saved to a file (this file accumulates logs, it does not write over old ones) for easy lookback access.
 
 Hope you enjoy! (REMEMBER: this bot is not perfect and can be inconsistent/incorrect since it only uses RSI's for its decisions. Because of this imperfection I would not recommend
 giving the bot the ability to spend a lot of money)
