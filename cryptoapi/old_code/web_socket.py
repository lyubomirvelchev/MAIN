import time
from websocket._core import WebSocket

api_key = '0075620F-AA4E-43F3-953F-309033B759FE'
ws_link = 'ws://ws.coinapi.io/v1/'

json_as_str = '{"type": "hello", "apikey": "0075620F-AA4E-43F3-953F-309033B759FE", "heartbeat": false, "subscribe_data_type": ["trade"], "subscribe_filter_asset_id": ["BTC", "ETH"]}'
ws = WebSocket()
ws.connect(ws_link)
print('connected')
start = time.time()
ws.send(json_as_str)
while time.time() - start < 10:
    result = ws.recv()
    print(result)
ws.close()
