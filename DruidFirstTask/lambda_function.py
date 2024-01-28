import copy, pprint

import requests, time, json, gzip, base64
from datetime import datetime
from project_constants import *

NO_DATA_ERROR = {
    "statusCode": 404,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": json.dumps({
        "message": "No data with the current parameters exists!"
    }),
}
NO_PAGE_GIVEN_ERROR = {
    "statusCode": 400,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": json.dumps({
        "message": "No page parameter given!"
    }),
}
INVALID_PAGE_NUMBER_ERROR_RESPONSE = {
    "statusCode": 400,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": json.dumps({
        "message": "Invalid page number. Page number has to be positive integer."
    }),
}
INVALID_PARAMETERS_ERROR_RESPONSE = {
    "statusCode": 400,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": json.dumps({
        "message": "Invalid parameters."
    }),
}


def gzip_encode(data):
    return base64.b64encode(gzip.compress(json.dumps(data).encode('utf-8'))).decode('ascii')


def handle_keyword_values(params):
    values = params.split(',')
    values_upper = [value.upper() for value in values if value != '']
    return values_upper


def handle_asset_name_values(params):
    values = params.split(',')
    actual_values = [value for value in values if value[:3] in ASSET_CLASSES_MAP.values()]
    return actual_values


def handle_asset_class_values(params):
    values = params.split(',')
    actual_values = [ASSET_CLASSES_MAP[value] for value in values if value in ASSET_CLASSES_MAP.keys()]
    return actual_values


def construct_druid_json(event):
    params = event['queryStringParameters']
    param_keys = params.keys()
    temporary_json_obj = BASE_JSON
    page_number = int(params['page'])
    temporary_json_obj['offset'] = 100 * page_number
    if not any(key in POSSIBLE_PARAMETERS for key in param_keys):
        temporary_json_obj['filter'] = KEYWORD_NOT_NULL_FILTER
        return temporary_json_obj
    else:
        temporary_json_obj['filter'] = {}
        temporary_json_obj['filter']['type'] = "and"
        temporary_json_obj['filter']['fields'] = [KEYWORD_NOT_NULL_FILTER]
    if 'keywords' in param_keys:
        values = handle_keyword_values(params['keywords'])
        for value in values:
            new_like_filter = copy.deepcopy(KEYWORD_LIKE_FILTER)
            new_like_filter['pattern'] = value
            temporary_json_obj['filter']['fields'].append(new_like_filter)
    if "asset" in param_keys:
        values = handle_asset_name_values(params['asset'])
        if len(values) > 0:
            new_asset_filter = copy.deepcopy(ASSET_NAMES_FILTER)
            for value in values:
                new_asset_filter['values'].append(value)
            new_asset_filter['values'].append(None)
            temporary_json_obj['filter']['fields'].append(new_asset_filter)
        else:
            return False
    else:
        if "assetClass" in param_keys:
            values = handle_asset_class_values(params['assetClass'])
            if len(values) > 0:
                new_asset_class_filter = copy.deepcopy(ASSET_CLASS_FILTER)
                for value in values:
                    new_asset_class_filter['values'].append(value)
                temporary_json_obj['filter']['fields'].append(new_asset_class_filter)
            else:
                return False
    return temporary_json_obj


def raise_error_if_page_number_invalid(event):
    """Return error message if page number is invalid or False if page number is valid"""
    if event['queryStringParameters'] is None or 'page' not in event['queryStringParameters'].keys():
        return NO_PAGE_GIVEN_ERROR  # return error if no page parameter given
    else:
        page_number_str = event['queryStringParameters']['page']
    try:
        page_number = int(page_number_str)
        return False if page_number >= 0 else INVALID_PAGE_NUMBER_ERROR_RESPONSE  # return False is number is valid
    except (ValueError, TypeError):
        return INVALID_PAGE_NUMBER_ERROR_RESPONSE  # return error if page is not an integer


def lambda_function(event, context=None):
    print(event)
    invalid_page_error = raise_error_if_page_number_invalid(event)
    if invalid_page_error:
        return invalid_page_error
    json_obj = construct_druid_json(event)
    if not json_obj:
        return INVALID_PARAMETERS_ERROR_RESPONSE
    r = requests.post('http://ec2-44-201-185-109.compute-1.amazonaws.com:8888/druid/v2/?pretty', json=json_obj)
    json_result = r.json()
    if len(json_result) == 0:
        return NO_DATA_ERROR
    else:
        json_result = json_result[0]
    new_json = {}
    for idx, value in enumerate(json_result['events']):
        new_json[idx] = {}
        for col_idx, column_name in enumerate(json_result['columns']):
            new_json[idx][column_name] = value[col_idx]
    pprint.pprint(new_json)
    return {
        "isBase64Encoded": True,
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
            "Access-Control-Allow-Origin": "*"
        },
        'body': gzip_encode(new_json)
    }


event = {'resource': '/dashboard/v2/twitterfeed', 'path': '/dashboard/v2/twitterfeed', 'httpMethod': 'GET', 'headers': {'Accept': 'application/json', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,de;q=0.7,bg;q=0.6', 'Authorization': 'sampleapikeygoeshere', 'cache-control': 'no-cache', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '9070', 'CloudFront-Viewer-Country': 'BG', 'content-type': 'application/json', 'Host': '5nx0jjoub7.execute-api.us-east-1.amazonaws.com', 'origin': 'https://chatterquant.com', 'pragma': 'no-cache', 'Referer': 'https://chatterquant.com/', 'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36', 'Via': '2.0 19d23243200e63f987eb95cd84ad557c.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': 'RmMa5psVmP9CKJhF__2DRZt3wkK34Db99fuzTDhABtwQNOPd4vU2Tg==', 'X-Amzn-Trace-Id': 'Root=1-6369211a-1eff3d7d37aaced50e8b9e01', 'X-Forwarded-For': '87.118.155.8, 130.176.219.17', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['application/json'], 'Accept-Encoding': ['gzip, deflate, br'], 'Accept-Language': ['en-GB,en;q=0.9,en-US;q=0.8,de;q=0.7,bg;q=0.6'], 'Authorization': ['sampleapikeygoeshere'], 'cache-control': ['no-cache'], 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['9070'], 'CloudFront-Viewer-Country': ['BG'], 'content-type': ['application/json'], 'Host': ['5nx0jjoub7.execute-api.us-east-1.amazonaws.com'], 'origin': ['https://chatterquant.com'], 'pragma': ['no-cache'], 'Referer': ['https://chatterquant.com/'], 'sec-ch-ua': ['"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"'], 'sec-ch-ua-mobile': ['?0'], 'sec-ch-ua-platform': ['"Windows"'], 'sec-fetch-dest': ['empty'], 'sec-fetch-mode': ['cors'], 'sec-fetch-site': ['cross-site'], 'User-Agent': ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'], 'Via': ['2.0 19d23243200e63f987eb95cd84ad557c.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': ['RmMa5psVmP9CKJhF__2DRZt3wkK34Db99fuzTDhABtwQNOPd4vU2Tg=='], 'X-Amzn-Trace-Id': ['Root=1-6369211a-1eff3d7d37aaced50e8b9e01'], 'X-Forwarded-For': ['87.118.155.8, 130.176.219.17'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': {'asset': 'st_AMZN', 'keywords': 'DATABASE', 'page': '0'}, 'multiValueQueryStringParameters': {'asset': ['st_AMZN'], 'keywords': ['DATABASE'], 'page': ['0']}, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'du16n4', 'authorizer': {'principalId': 'user', 'integrationLatency': 80}, 'resourcePath': '/dashboard/v2/twitterfeed', 'httpMethod': 'GET', 'extendedRequestId': 'bPIcNHPmIAMFbpA=', 'requestTime': '07/Nov/2022:15:15:38 +0000', 'path': '/prod/dashboard/v2/twitterfeed', 'accountId': '000832285022', 'protocol': 'HTTP/1.1', 'stage': 'prod', 'domainPrefix': '5nx0jjoub7', 'requestTimeEpoch': 1667834138715, 'requestId': 'e5164b2a-0765-401a-b608-488c4ac768e5', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '87.118.155.8', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36', 'user': None}, 'domainName': '5nx0jjoub7.execute-api.us-east-1.amazonaws.com', 'apiId': '5nx0jjoub7'}, 'body': None, 'isBase64Encoded': False}



a = lambda_function(event)
print(a['statusCode'])
print(a['body'])
b = 9
