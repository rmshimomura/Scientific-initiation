import geopandas as gpd
import pandas as pd
import utils, datetime
import growth_types as gt
import growth_functions as gf
import matplotlib.pyplot as plt
import os

root_folder = None

if 'Meu Drive' in os.getcwd():
    root_folder = 'Meu Drive'
elif 'My Drive' in os.getcwd():
    root_folder = 'My Drive'

def read_basic_info():

    global root_folder

    # Read map file
    _map = gpd.read_file('G:/' + root_folder + '/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    # Read collectors file and sort them based on the date of the first spores
    _collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/ColetoresSafra2021Final.csv', sep=',', decimal='.', parse_dates=['Primeiro_Esporo'], infer_datetime_format=True)
    _collectors = _collectors.sort_values(by=['Primeiro_Esporo'])

    _collectors = utils.clean_up(_collectors)

    _collectors['discovery_day'] = None
    _collectors['Fake'] = False

    return _map, _collectors

def coloring_collectors(_collectors):

    global first_apperances

    _collectors['color'] = 'white'

    first_apperances = _collectors[0:3]
    # first_apperances = _collectors[0:6]

    for apperance in first_apperances.itertuples():
        _collectors.loc[apperance.Index, 'color'] = 'yellow'
        _collectors.loc[apperance.Index, 'Detected'] = 1
    
    for i in first_apperances.itertuples():
        _collectors.loc[i.Index, 'color'] = 'yellow'
        _collectors.loc[i.Index, 'Detected'] = 1

def add_fake_collectors(_collectors):

    fake_collectors_file = open('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/Fake_Collectors.csv', 'w')

    min_point = _map.total_bounds[0:2]
    max_point = _map.total_bounds[2:4]

    total_length = max_point[0] - min_point[0]
    total_height = max_point[1] - min_point[1]
    fake_collectors_file.write('Macro,Regiao,Cidade,Produtor-Instituicao,Cultivar,Situacao,Primeiro_Esporo,Estadio Fenologico,Longitude Decimal,Latitude Decimal,Dias_apos_O0,Data\n')

    for i in range(30):
        for j in range(15):
            _collectors.loc[len(_collectors), ['LatitudeDecimal', 'LongitudeDecimal', 'color', 'Detected', 'Fake']] = min_point[1] + total_height * j / 15, min_point[0] + total_length * i / 30, 'black', 0, True
            fake_collectors_file.write(f',,,,,,,,{min_point[0] + total_length * i / 30},{min_point[1] + total_height * j / 15},, \n')

def update_with_fake_collectors(_collectors):

    fakes = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/Fake_Collectors.csv', sep=',', decimal='.', parse_dates=['Primeiro_Esporo'], infer_datetime_format=True)
    fakes['Fake'] = True
    return pd.concat([_collectors, fakes], ignore_index=True)

TEST_PARAMS = {
    'number_of_days' : 100,
    'growth_function_distance' : gf.logaritmic_growth_distance,
    'growth_function_days' : gf.logaritmic_growth_days,
    'base' : 1000,
    'animation' : True
}

_map, _collectors = read_basic_info()
coloring_collectors(_collectors)

_collectors = update_with_fake_collectors(_collectors)

print(_collectors['Fake'])

# teste_buffer = gpd.GeoSeries.from_file('G:/' + root_folder + '/IC/Codes/buffers-seminais/15-005-safra2021-buffer-seminais-carrap.shp')

''' -- Debug burr 

# _map.plot()

# for i in range(len(teste_buffer)):
#     x, y = teste_buffer[i].exterior.xy
#     plt.plot(x, y, color='red')

# # plt.scatter(teste_buffer.centroid.x, teste_buffer.centroid.y, color='yellow', s=10)
# plt.scatter(_collectors['LongitudeDecimal'], _collectors['LatitudeDecimal'], color=_collectors['color'], s=15)
# plt.show()

'''

# start_day = _collectors['Primeiro_Esporo'].iloc[0]
# old_circles = []


# true_positive_penalty, infection_circles = \
#     gt.circular_growth(_map, _collectors, first_apperances, old_circles, TEST_PARAMS)

# true_negative_penalty = 0

# false_positive_penalty = utils.calculate_false_positives_penalty(_collectors, start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1))

# false_negative_penalty = utils.calculate_false_negatives_penalty(_collectors, TEST_PARAMS['growth_function_days'], TEST_PARAMS['base'])

# PENALTIES = {
#     'true_positive' : true_positive_penalty,
#     'true_negative' : true_negative_penalty,
#     'false_positive' : false_positive_penalty,
#     'false_negative' : false_negative_penalty
# }

# utils.write_csv(TEST_PARAMS, PENALTIES, start_day, start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1))

# print(f"TEST PARAMS: {TEST_PARAMS}")
# print(f"True positive penalty: {true_positive_penalty}")
# print(f"True negative penalty: {true_negative_penalty}")
# print(f"False positive penalty: {false_positive_penalty}")
# print(f"False negative penalty: {false_negative_penalty}")

# # for i in range(len(infection_circles)):
# #     print(f"Circle {i} has {infection_circles[i].buffer * 111.045} km of radius and {infection_circles[i].life_span} life span")

# if TEST_PARAMS['animation']: plt.show()