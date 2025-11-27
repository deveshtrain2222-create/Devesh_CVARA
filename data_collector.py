import requests
import pandas as pd

coin = "bitcoin"
days = 30

url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={days}"

response = requests.get(url)
data = response.json()

prices = data["prices"]

df = pd.DataFrame(prices, columns=["timestamp", "price"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

print(df.head())
df.to_csv("crypto_prices2.csv",index=True)
print("CSV created successfully: crypto_prices2.csv")
import pandas as pd

df = pd.read_csv("crypto_prices2.csv")
print(df.columns)