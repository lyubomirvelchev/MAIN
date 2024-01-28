import os
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import FloatType

CURRENT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(CURRENT_ABSOLUTE_PATH, 'test.csv')
NAN_VALUES_FILE_PATH = os.path.join(CURRENT_ABSOLUTE_PATH, 'AB.csv')
INTEGER_COLUMNS = ['open', 'high', 'close', 'low', 'salary', 'number_transactions', 'volume', 'volume_weighted']

spark = SparkSession.builder.appName("Practice").getOrCreate()
hui = spark.read.option('header', 'true').csv(NAN_VALUES_FILE_PATH)
for column in INTEGER_COLUMNS:
    hui = hui.withColumn(column, hui[column].cast(FloatType()))
# hui = hui.withColumn("HUI", hui['high'] + 2)
hui.show()
hui.na.fill("HUI", ['high', 'open']).show()
hui.filter("high >= 22.77").select(['high', 'open', 'date']).show()
hui.filter((hui["high"] >= 22.5) | (hui["high"] <= 21.5)).select(['high', 'open']).show()
hui = hui.filter(~(hui["high"] >= 22.77)).select(['high', 'open', 'department', 'salary'])
hui.show()
hui.groupBy('department').max().show()
hui.groupBy('department').sum().show()
hui.groupBy('department').count().show()
# def foo(x):
#     return x+2
# hui.apply(foo).sort_index().show()

a = 9
# hui.na.drop(how='all').show()
# hui.na.drop(how='any', subset=['high']).show()
# hui = hui.drop("HUI")
# hui.show()
# hui = hui.withColumnRenamed('high', "HIGH AS F")
# hui.show()
# hui.select(["high", 'low']).show()
# print(hui.dtypes)
# hui.describe().show()
# hui.filter((hui.high == '22.550000') & (hui.close == '22.350000')).show()
# hui.printSchema()
# df_pyspark = spark.read.csv()
# df_pyspark.show()
