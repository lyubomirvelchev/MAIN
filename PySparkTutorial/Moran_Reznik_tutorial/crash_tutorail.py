import os
import pandas as pd
from pyspark.sql import SparkSession, functions

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
spark_session = SparkSession.builder.appName("HUI").getOrCreate()

# schema = 'Age INTEGER, Sex STRING, ChestPainType STRING, RestingBP INTEGER, Cholesterol INTEGER'
# df = spark_session.read.option('header', 'true').csv(os.path.join(ROOT_DIR, 'heart.csv'), schema=schema)
# df.show(5)

df = spark_session.read.parquet(os.path.join(ROOT_DIR, 'heart_rate.parquet'))

integer_columns = ['Age', 'RestingBP', 'Cholesterol', 'FastingBS', 'MaxHR', 'HeartDisease']
float_columns = ['Oldpeak']
for column in integer_columns:
    df = df.withColumn(column, functions.col(column).cast('int'))
for column in float_columns:
    df = df.withColumn(column, functions.col(column).cast('float'))

# fancy but will only return df with those columns only
# df = df.select([functions.col(column).cast('int') for column in integer_columns])

df.printSchema()
df.show(10)

if not os.path.exists(os.path.join(ROOT_DIR, 'heart_rate.parquet')):
    """Should find a non pandas way to save file"""
df.write.parquet(os.path.join(ROOT_DIR, 'heart_rate.parquet'))

df.describe().show()