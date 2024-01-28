import enum
import operator

DailyFields = enum.Enum(
    "DailyFields", [('close', "c"),
                    ('open', 'o'),
                    ('high', 'h'),
                    ('low', 'l'),
                    ('volume', 'v'),
                    ('vwap', 'vw'),
                    ]
)

ComparisonOperators = enum.Enum("ComparisonOperators", [
    ("<", operator.lt), ('>', operator.gt),
    ('<=', operator.le), ('>=', operator.ge),
    ('==', operator.eq)
])

TimeFrames = enum.Enum('TimeFrames', {
    '1min': 1, '2min': 2, '3min': 3,
    '5min': 5, '6min': 6, '10min': 10,
    '15min': 15, '30min': 30, '60min': 60
})

if __name__ == "__main__":
    pass
