import json
import time
from updater import UpdateTables
from project_constants import *


def lambda_handler(event=None, context=None):
    aws_connection = 'mysql+mysqlconnector://admin:dsj89jdj!li3dj2ljefds@database-1.clns6yopmify.us-east-1.rds.amazonaws.com:3306'
    aws_database_name = 'assets'
    UpdateTables(aws_connection, aws_database_name, EXCHANGE_LIST_V1)
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Database updated!",
        }),
    }
