import pandas as pd
from datetime import datetime

horizontal_len = 31
vertical_len = 23

c2021 = pd.read_csv(f"./v3.0/new_points/coletoressafra2021_{horizontal_len}_{vertical_len}.csv", sep=',', decimal='.', infer_datetime_format=True)
c2122 = pd.read_csv(f"./v3.0/new_points/coletoressafra2122_{horizontal_len}_{vertical_len}.csv", sep=',', decimal='.', infer_datetime_format=True)
c2223 = pd.read_csv(f"./v3.0/new_points/coletoressafra2223_{horizontal_len}_{vertical_len}.csv", sep=',', decimal='.', infer_datetime_format=True)

rows_size = len(c2021)

first = '2122'
second = '2223'

result_file = open(f"./UNION_DATA/{first}_{second}_{horizontal_len}_{vertical_len}.csv", "w")

result_file.write('Mesorregiao,Regiao,Municipio,Produtor,Cultivar,LatitudeDecimal,LongitudeDecimal,Primeiro_Esporo,Estadio Fenologico,Situacao,Dias_apos_O0,Data,geometry,fake,carrap\n')

for i in range(rows_size):

    collector_1 = c2122.iloc[i]
    collector_2 = c2223.iloc[i]

    if collector_1['Situacao'] == 'Com esporos' or collector_2['Situacao'] == 'Com esporos':
        situation = 'Com esporos'
    else:
        situation = 'Encerrado sem esporos'

    dates = [collector_1['Primeiro_Esporo'], collector_2['Primeiro_Esporo']]

    if type(dates[0]) == str and type(dates[1]) == str:

        # Extract day and month components from dates
        date_parts = [datetime.strptime(date, '%d/%m/%y').date().replace(year=1900) for date in dates]

        # Calculate the average day and month
        avg_day = sum(date.day for date in date_parts) // len(date_parts)
        avg_month = sum(date.month for date in date_parts) // len(date_parts)

        # Create the average date object with a placeholder year
        average_date = datetime(year=1900, month=avg_month, day=avg_day).date()

        # Convert the average date to the desired format
        average_date_formatted = average_date.strftime('%d/%m/%y')

    elif type(dates[0]) == str and type(dates[1]) != str:

        average_date_formatted = dates[0].date().replace(year=1900)

    elif type(dates[0]) != str and type(dates[1]) == str:

        average_date_formatted = dates[1].date().replace(year=1900)

    else:
        average_date_formatted = ''

    result_file.write(f",,,,,{collector_1['LatitudeDecimal']},{collector_1['LongitudeDecimal']},{average_date_formatted},{situation},,,,False,\n")
