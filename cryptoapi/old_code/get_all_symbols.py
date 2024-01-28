api_key = '0075620F-AA4E-43F3-953F-309033B759FE'

import requests
import json

url = 'https://rest.coinapi.io/v1/assets'
headers = {'X-CoinAPI-Key': api_key}
response = requests.get(url, headers=headers)
ticker_info_list = json.loads(response.text)
tickers = []
for single_ticker in ticker_info_list:
    symbol = single_ticker['asset_id']
    tickers.append(symbol)

print(tickers)
print(len(tickers))
print(len(set(tickers)))

# TOILETPAPER,SAFEBUTT,ELONBALLS, PANDACOIN