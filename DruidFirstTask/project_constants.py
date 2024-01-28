FIELDS_TO_SELECT = ["t", "f", "uf", "ul", "en", "un", "__time", "k", "id"]
BASE_JSON = {
    "queryType": "scan",
    "dataSource": {
        "type": "table",
        "name": "twitterFeed"
    },
    "intervals": {
        "type": "intervals",
        "intervals": [
            "-146136543-09-08T08:23:32.096Z/146140482-04-24T15:36:27.903Z"
        ]
    },
    "resultFormat": "compactedList",
    "limit": 100,
    "offset": 0,
    "order": "descending",
    "columns": [
        "__time",
        "en",
        "f",
        "id",
        "k",
        "t",
        "uf",
        "ul",
        "un"
    ],
    "legacy": False,
    "context": {
        "sqlOuterLimit": 1001,
        "sqlQueryId": "ade47208-d355-4cf2-88ab-80a587ad0959",
        "useNativeQueryExplain": True
    },
    "granularity": {
        "type": "all"
    }
}
KEYWORD_NOT_NULL_FILTER = {
    "type": "not",
    "field": {
        "type": "selector",
        "dimension": "k",
        "value": None
    }
}

KEYWORD_LIKE_FILTER = {
    "type": "like",
    "dimension": "k",
    "pattern": "",
    "escape": None,
    "extractionFn": None
}

ASSET_NAMES_FILTER = {
    "type": "in",
    "dimension": "as",
    "values": []
}

ASSET_CLASS_FILTER = {
    "type": "in",
    "dimension": "as",
    "values": [],
    "extractionFn": {
        "type": "substring",
        "index": 0,
        "length": 3
    }
}

ASSET_CLASSES_MAP = {
    "stock": "st_",
    "etf": "et_",
    "crypto": "cr_",
    "forex": "fo_",
    "indices": "in_"
}

POSSIBLE_PARAMETERS = ["asset", "assetClass", "keywords"]
