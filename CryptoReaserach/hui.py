import requests
import json
import pandas as pd

# x = requests.get('https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=2000&toTs=1180224000')
#
# data = json.loads(x.content)
# values = data['Data']['Data']
# df = pd.DataFrame(values)
#
# df = df.drop(df.columns[[-2, -1]], axis=1)
# df.to_csv('kurec4.csv')

#
# df1 = pd.read_csv('kurec.csv')
# df2 = pd.read_csv('kurec2.csv')
# df3 = pd.read_csv('kurec3.csv')
#
# bigdf = pd.concat([df1, df2, df3])
# bigdf.sort_values(['time'], inplace=True)
# bigdf = bigdf[bigdf.iloc[:, 2] != 0]
# bigdf.reset_index(inplace=True)
# bigdf.drop(bigdf.columns[[0, 1, -2, -1]], axis=1, inplace=True)
# bigdf.to_csv('btc1D')
#

df = pd.read_csv('btc1D.csv')