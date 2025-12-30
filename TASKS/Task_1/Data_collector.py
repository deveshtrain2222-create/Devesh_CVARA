import yfinance as yf
#collect data through yfinance


btc= yf.Ticker("BTC-USD")
data = btc.history(period="1mo")    
print(data.head())

data.to_csv("crypto_prices_1.csv",index=True)
print("CSV created successfully: crypto_prices_1.csv")