import mysql.connector
import gzip
import json
import base64

INVALID_PARAMETERS_GIVEN_ERROR = {
    'statusCode': 400,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": json.dumps({
        "message": "Bad request. Invalid parameters given."
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
PAGE_NUMBER_TOO_BIG_RESPONSE = {
    'statusCode': 404,
    "headers": {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    },
    "body": json.dumps({
        "message": "There is no data on this page. Use smaller page number."
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


def gzip_encode(data):
    return base64.b64encode(gzip.compress(json.dumps(data).encode('utf-8'))).decode('ascii')


def get_crypto_assets(event, context=None):
    try:
        limit = 450
        if event['queryStringParameters'] is None or 'page' not in event['queryStringParameters'].keys():
            return NO_PAGE_GIVEN_ERROR  # return error if no page parameter given
        else:
            page_number_str = event['queryStringParameters']['page']

        """Handle different cases for page value"""
        try:
            page_number = int(page_number_str)
        except (ValueError, TypeError):
            return INVALID_PAGE_NUMBER_ERROR_RESPONSE  # return error if page is not an integer
        if page_number < 0:
            return INVALID_PAGE_NUMBER_ERROR_RESPONSE  # return error if page is negative integer

        crypto_database_name = "crypto_fundamentals"
        database_connection = mysql.connector.connect(
            host="database-1.clns6yopmify.us-east-1.rds.amazonaws.com",
            user="admin",
            password="dsj89jdj!li3dj2ljefds",
            database=crypto_database_name
        )
        query = """SELECT Symbol, CoinName, Description, ImageUrl 
                   FROM {}.crypto_assets
                   LIMIT {} OFFSET {};""".format(crypto_database_name, limit, limit * page_number)
        my_cursor = database_connection.cursor(buffered=True)
        my_cursor.execute(query)
        results = my_cursor.fetchall()
        json_obj = {}
        if len(results) == 0:
            return PAGE_NUMBER_TOO_BIG_RESPONSE
        for idx in range(len(results)):
            json_obj[idx] = {}
            json_obj[idx]['asset_id'] = results[idx][0]
            json_obj[idx]['asset_symbol'] = results[idx][0].split('_')[1]
            json_obj[idx]['asset_name'] = results[idx][1]
            json_obj[idx]['asset_description'] = results[idx][2]
            json_obj[idx]['asset_logo'] = 'https://www.cryptocompare.com' + results[idx][3] if results[idx][3] else None
        return {
            "isBase64Encoded": True,
            'statusCode': 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "max-age=3600, public, must-revalidate",
                "Content-Encoding": "gzip",
                "Access-Control-Allow-Origin": "*"
            },
            'body': gzip_encode(json_obj)
        }
    except Exception as e:
        print(e)
        return INVALID_PARAMETERS_GIVEN_ERROR
