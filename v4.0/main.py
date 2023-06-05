import geopandas as gpd
import pandas as pd
import utils
import growth_functions as gf
import matplotlib.pyplot as plt
import os
import shapely.geometry as sg

root_folder = None

if 'Meu Drive' in os.getcwd():
    root_folder = 'Meu Drive'
elif 'My Drive' in os.getcwd():
    root_folder = 'My Drive'

file_name = 'coletoressafra2223'
year_analyzed = 2022

def read_basic_info():

    global root_folder, burr_buffer, file_name

    # Read map file
    _map = gpd.read_file('G:/' + root_folder + '/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    # Read collectors file
    _collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Collectors/actual/' + file_name + '.csv', sep=',', decimal='.', infer_datetime_format=True)

    geometry = [sg.Point(x,y) for x,y in zip(_collectors.LongitudeDecimal, _collectors.LatitudeDecimal)]

    _collectors_geo_df = gpd.GeoDataFrame(_collectors, geometry=geometry).sort_values(by=['Primeiro_Esporo'])

    _collectors_geo_df = utils.clean_up(_collectors_geo_df)

    _collectors_geo_df['discovery_day'] = None
    _collectors.loc[_collectors['Primeiro_Esporo'].notnull(), 'color'] = 'green'
    _collectors.loc[_collectors['Primeiro_Esporo'].isnull(), 'color'] = 'red'

    return _map, _collectors_geo_df

TEST_PARAMS = {
    'number_of_days' : 100,
    'growth_function_distance' : gf.logaritmic_growth_distance,
    'growth_function_days' : gf.logaritmic_growth_days,
    'base' : 200000,
    'animation' : True,
    'Fake_Collectors' : False,
}

_map, _collectors_geo_df = read_basic_info()
old_geometries = []

print(_collectors_geo_df.columns)

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

if TEST_PARAMS['animation']: plt.show()