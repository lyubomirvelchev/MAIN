import requests, json

a = requests.get('https://api.twelvedata.com/indices?country=United%20States')
b = requests.get('https://api.twelvedata.com/forex_pairs')

c = json.loads(a.text)
d = json.loads(b.text)
e=0