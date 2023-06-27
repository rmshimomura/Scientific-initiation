import pandas as pd
import itertools

def generate_pairs(file_names):
    pairs = []
    combinations = itertools.combinations(file_names, 2)
    for combination in combinations:
        pairs.append(combination)
    return pairs

horizontal_len = 31
vertical_len = 23

names = ['2021', '2122', '2223']

pairs = generate_pairs(names)

for pair in pairs:

    first_file = pd.read_csv(f"./v4.0/processed_data/coletoressafra{pair[0]}_{horizontal_len}_{vertical_len}.csv", sep=',', decimal='.', infer_datetime_format=True)
    second_file = pd.read_csv(f"./v4.0/processed_data/coletoressafra{pair[1]}_{horizontal_len}_{vertical_len}.csv", sep=',', decimal='.', infer_datetime_format=True)

    file_test = open(f'./{pair[0]}-{pair[1]}.csv', 'w')
    file_test.write('LatitudeDecimal,LongitudeDecimal,Situacao,MediaDiasAposInicioCiclo,QuantidadeDeAnosUsados,QuantidadeDeAnosPositivos\n')

    for i in range(len(first_file)):

        _1_info = first_file.iloc[i]
        _2_info = second_file.iloc[i]

        _1_days = _1_info['DiasAposInicioCiclo']
        _2_days = _2_info['DiasAposInicioCiclo']

        if _1_days == -1:
        
            if _2_days == -1:

                file_test.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_1_info["Situacao"]},-1,2,0\n')

            elif _2_days != -1:

                file_test.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_2_info["Situacao"]},{_2_days},2,1\n')

        elif _1_days != -1:

            if _2_days == -1:

                file_test.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_1_info["Situacao"]},{_1_days},2,1\n')

            elif _2_days != -1:

                file_test.write(f'{_1_info["LatitudeDecimal"]},{_1_info["LongitudeDecimal"]},{_1_info["Situacao"]},{(_1_days + _2_days)/2},2,2\n')