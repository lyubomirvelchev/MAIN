import json, boto3, gzip, base64
from boto3.dynamodb.conditions import Key


def gzip_encode(data):
    return base64.b64encode(gzip.compress(json.dumps(data).encode('utf-8'))).decode('ascii')


def lambda_handler(event, context):
    if ('queryStringParameters' in event and event['queryStringParameters'] is not None and 'assetClass' in event[
        'queryStringParameters'] and event['queryStringParameters']['assetClass'] in ['stocks', 'etf', 'crypto',
                                                                                      'forex', 'indices']):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('asset_info')
        prepareResponse = []
        iterateLoop = True
        lowerBound = event['queryStringParameters']['assetClass']
        upperBound = event['queryStringParameters']['assetClass'] + "||"
        iterateKey = False
        while iterateLoop:
            if iterateKey:
                response = table.query(
                    KeyConditionExpression=Key('pk').eq("assets") & Key('sk').between(lowerBound, upperBound),
                    ExclusiveStartKey=iterateKey
                )
            else:
                response = table.query(
                    KeyConditionExpression=Key('pk').eq("assets") & Key('sk').between(lowerBound, upperBound)
                )
            for item in response['Items']:
                prepareResponse += item['o']
            if ('LastEvaluatedKey' in response):
                iterateLoop = True
                iterateKey = response['LastEvaluatedKey']
            else:
                iterateLoop = False

        return {
            "isBase64Encoded": True,
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Content-Encoding": "gzip",
                "Access-Control-Allow-Origin": "*"
            },
            "body": gzip_encode({"data": prepareResponse})
        }
    else:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "Invalid asset class."
            })
        }