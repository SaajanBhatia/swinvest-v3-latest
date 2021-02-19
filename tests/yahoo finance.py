import pandas as pd
import yfinance as yf

stock = yf.Ticker("GOOGL")
dataFrame = pd.dataFrame(stock.history(period="max"))
marketInfo = stock.info()