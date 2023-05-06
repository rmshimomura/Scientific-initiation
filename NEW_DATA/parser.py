import pandas as pd

wow = pd.read_csv('./NEW_DATA/final.csv', sep=',', decimal='.', infer_datetime_format=True)

print(wow.head())