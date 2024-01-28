import requests, time, json, gzip, base64
from datetime import datetime

def gzip_encode(data):
    return base64.b64encode(gzip.compress(json.dumps(data).encode('utf-8'))).decode('ascii')

def lambda_handler(event, context):

    startTime = str(datetime.fromtimestamp(time.time()-2592000).strftime("%Y-%m-%dT%H:%M:%S.000Z"))

    r = requests.post('http://ec2-44-201-185-109.compute-1.amazonaws.com:8888/druid/v2/?pretty', json={
    "queryType": "topN",
    "dataSource": {
        "type": "table",
        "name": "twitterFeed"
    },
    "dimension": {
        "type": "default",
        "dimension": "k",
        "outputName": "k",
        "outputType": "STRING"
    },
    "metric": {
        "type": "dimension",
        "ordering": {
        "type": "lexicographic"
        }
    },
    "filter": {"type": "not","field": {"type": "selector","dimension": "k","value": None}},
    "threshold": 100001,
    "intervals": {
        "type": "intervals",
        "intervals": [
        "-146136543-09-08T08:23:32.096Z/146140482-04-24T15:36:27.903Z"
        ]
    },
    "granularity": {
        "type": "all"
    }
    })

    jsonHolder = r.json()

    newHolder = []
    if(len(jsonHolder) > 0):
        newHolder = jsonHolder[0]['result']

    return {
        "isBase64Encoded": True,
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
            "Access-Control-Allow-Origin": "*"
        },
        'body': gzip_encode(newHolder)
    }


lambda_handler(0,0)