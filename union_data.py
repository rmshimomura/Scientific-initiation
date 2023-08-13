import pandas as pd
import statistics

def geometric_mean(data : list):
    return statistics.geometric_mean([float(i) for i in data])

def arithmetic_mean(data : list):
    return statistics.mean([float(i) for i in data])

def harmonic_mean(data : list):
    return statistics.harmonic_mean([float(i) for i in data])

def learning(method, horizontal_len, vertical_len):

    first_file = pd.read_csv(f"G:\My Drive\IC\Codes\Data\Gridded_Data\Test_Data\coletoressafra2021_{horizontal_len}_{vertical_len}.csv", sep=',', decimal='.', infer_datetime_format=True)
    second_file = pd.read_csv(f"G:\My Drive\IC\Codes\Data\Gridded_Data\Test_Data\coletoressafra2122_{horizontal_len}_{vertical_len}.csv", sep=',', decimal='.', infer_datetime_format=True)
    third_file = pd.read_csv(f"G:\My Drive\IC\Codes\Data\Gridded_Data\Test_Data\coletoressafra2223_{horizontal_len}_{vertical_len}.csv", sep=',', decimal='.', infer_datetime_format=True)

    result = open(f'{method.__name__}_{horizontal_len}_{vertical_len}.csv', 'w')
    result.write('LatitudeDecimal,LongitudeDecimal,Situacao,MediaDiasAposInicioCiclo,QuantidadeDeAnosUsados,QuantidadeDeAnosPositivos\n')

    for i in range(len(first_file)):

        _1_info = first_file.iloc[i]
        _2_info = second_file.iloc[i]
        _3_info = third_file.iloc[i]

        _1_days = _1_info['DiasAposInicioCiclo']
        _2_days = _2_info['DiasAposInicioCiclo']
        _3_days = _3_info['DiasAposInicioCiclo']

        if _1_days == -1:
        
            if _2_days == -1:

                if _3_days == -1: # [-1,-1,-1]

                    result.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_1_info["Situacao"]},-1,3,0\n')

                elif _3_days != -1: # [-1,-1,3_days]

                    result.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_3_info["Situacao"]},{method([_3_days])},3,1\n')

            elif _2_days != -1: 

                if _3_days == -1: # [-1,2_days,-1]

                    result.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_2_info["Situacao"]},{method([_2_days])},3,1\n')

                elif _3_days != -1: # [-1,2_days,3_days]

                    result.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_2_info["Situacao"]},{method([_2_days, _3_days])},3,2\n')

        elif _1_days != -1:

            if _2_days != -1:

                if _3_days != -1: # [1,2,3]

                    result.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_1_info["Situacao"]},{method([_1_days, _2_days, _3_days])},3,3\n')

                elif _3_days == -1: # [1,2,-1]

                    result.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_1_info["Situacao"]},{method([_1_days, _2_days])},3,2\n')

            elif _2_days == -1:

                if _3_days != -1: # [1,-1,3]

                    result.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_1_info["Situacao"]},{method([_1_days, _3_days])},3,2\n')

                elif _3_days == -1: # [1,-1,-1]

                    result.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_1_info["Situacao"]},{method([_1_days])},3,1\n')

if __name__ == '__main__':

    learning(arithmetic_mean, 31, 23)
    learning(geometric_mean, 31, 23)
    learning(harmonic_mean, 31, 23)