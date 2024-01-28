import os
import pandas as pd
import warnings
from pyspark.sql import SparkSession, functions


def change_column_types(df, type_dict):
    for type, columns in type_dict.items():
        for column in columns:
            df = df.withColumn(column, functions.col(column).cast(type))
    return df


if __name__ == '__main__':
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    spark_session = SparkSession.builder.appName("HUI").getOrCreate()
    df = spark_session.read.option('header', 'true').csv(os.path.join(ROOT_DIR, 'heart.csv'))
    integer_columns = ['Age', 'RestingBP', 'Cholesterol', 'FastingBS', 'MaxHR', 'HeartDisease']
    float_columns = ['Oldpeak']
    df = change_column_types(df, {'int': integer_columns, 'float': float_columns})
    df.printSchema()
