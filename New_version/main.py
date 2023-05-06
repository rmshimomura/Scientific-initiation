import geopandas as gpd
import pandas as pd
import utils
import growth_types as gt
import growth_functions as gf
import matplotlib.pyplot as plt
import datetime
import os
import shapely.geometry as sg

root_folder = None

if 'Meu Drive' in os.getcwd():
    root_folder = 'Meu Drive'
elif 'My Drive' in os.getcwd():
    root_folder = 'My Drive'

def read_basic_info():

    global root_folder, burr_buffer

    # Read map file
    _map = gpd.read_file('G:/' + root_folder + '/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    # Read collectors file
    _collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/With_Burrs/coletoressafra2122.csv', sep=',', decimal='.', infer_datetime_format=True)

    # Make burr_buffer equal to a list of the last column of the _collectors dataframe
    _collectors = _collectors.sort_values(by=['Primeiro_Esporo'])
    burr_buffer = _collectors['carrap'].tolist()

    # Create buffers from burrs string
    for i in range(len(burr_buffer)):
        clear_string = burr_buffer[i].replace('POLYGON ((', '').replace('))', '').split(', ')
        for j in range(len(clear_string)):
            clear_string[j] = clear_string[j].split(' ')
            clear_string[j] = [float(clear_string[j][0]), float(clear_string[j][1])]

        burr_buffer[i] = sg.Polygon(clear_string)

    _collectors = utils.clean_up(_collectors)

    _collectors['burr'] = range(0, len(burr_buffer))
    _collectors['discovery_day'] = None
    _collectors['Fake'] = False


    return _map, _collectors

def coloring_collectors(_collectors):

    global first_apperances

    _collectors['color'] = 'white'

    first_apperances = _collectors[0:3]

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
    fake_collectors_file.write('Mesorregiao,Regiao,Municipio,Produtor,Situacao,Primeiro_Esporo,LongitudeDecimal,LatitudeDecimal,Dias_apos_O0,Data\n')

    for i in range(30):
        for j in range(15):
            _collectors.loc[len(_collectors), ['LatitudeDecimal', 'LongitudeDecimal', 'color', 'Detected', 'Fake']] = min_point[1] + total_height * j / 15, min_point[0] + total_length * i / 30, 'black', 0, True
            fake_collectors_file.write(f',,,,,,{min_point[0] + total_length * i / 30},{min_point[1] + total_height * j / 15},, \n')

def update_with_fake_collectors(_collectors):

    fakes = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/Fake_Collectors.csv', sep=',', decimal='.', parse_dates=['Primeiro_Esporo'], infer_datetime_format=True)
    fakes['color'] = 'black'
    fakes['Detected'] = 0
    fakes['Fake'] = True
    return pd.concat([_collectors, fakes], ignore_index=True)

TEST_PARAMS = {
    'number_of_days' : 100,
    'growth_function_distance' : gf.logaritmic_growth_distance,
    'growth_function_days' : gf.logaritmic_growth_days,
    'base' : 200000,
    'animation' : True,
    'Fake_Collectors' : False,
}

_map, _collectors = read_basic_info()
old_geometries = []
coloring_collectors(_collectors)

start_day = _collectors['Primeiro_Esporo'].iloc[0]

if TEST_PARAMS['Fake_Collectors']:
    if not os.path.exists('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/Fake_Collectors.csv'):
        add_fake_collectors(_collectors)

    _collectors = update_with_fake_collectors(_collectors)

method_used = None

new_data = pd.read_csv('G:/' + root_folder + '/IC/Codes/NEW_DATA/coletores2223.csv', sep=',', decimal='.', infer_datetime_format=True)
new_data = utils.clean_up_2(new_data)

# Plot map
_map.plot(color='white', edgecolor='lightgrey')
# Plot all points of new_data
for i in new_data.itertuples():
    plt.plot(i.LongitudeDecimal, i.LatitudeDecimal, '*', color='blue')

# Plot all points of _collectors
for i in _collectors.itertuples():
    plt.plot(i.LongitudeDecimal, i.LatitudeDecimal, 'o', color='red')

plt.show()

# utils.debug_burr(_map, burr_buffer, _collectors,plt)

# true_positive_penalty, infection_circles, method_used = \
#     gt.circular_growth(_map, _collectors, first_apperances, old_geometries, TEST_PARAMS)

# true_positive_penalty, burrs_list, method_used, fake_buffers_test = \
#     gt.burr_growth(_map, _collectors, first_apperances, old_geometries, burr_buffer, TEST_PARAMS)

# true_negative_penalty = 0

# false_positive_penalty = utils.calculate_false_positives_penalty(_collectors, start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1))

# false_negative_penalty = utils.calculate_false_negatives_penalty(_collectors, TEST_PARAMS['growth_function_days'], TEST_PARAMS['base'])

# PENALTIES = {
#     'true_positive' : true_positive_penalty,
#     'true_negative' : true_negative_penalty,
#     'false_positive' : false_positive_penalty,
#     'false_negative' : false_negative_penalty
# }

# utils.write_csv(TEST_PARAMS, PENALTIES, start_day, start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1), method_used)

# # print(f"TEST PARAMS: {TEST_PARAMS}")
# print(f"True positive penalty: {true_positive_penalty}")
# print(f"True negative penalty: {true_negative_penalty}")
# print(f"False positive penalty: {false_positive_penalty}")
# print(f"False negative penalty: {false_negative_penalty}")

# if TEST_PARAMS['animation']: plt.show()