import os
import sys
import geopandas as gpd
import pandas as pd
import utils
import growth_functions as gf
import growth_types as gt
import matplotlib.pyplot as plt
import shapely.geometry as sg
import coletores, cria_buffers
import time
import datetime

root_folder = None

if 'Meu Drive' in os.getcwd():
    root_folder = 'Meu Drive'
elif 'My Drive' in os.getcwd():
    root_folder = 'My Drive'


file_name = 'coletoressafra2021_31_23'

def read_basic_info():

    global root_folder, burr_buffer, file_name

    # Read map file
    _map = gpd.read_file('G:/' + root_folder + '/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    # Read collectors file
    _collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/v4.0/processed_data/' + file_name + '.csv', sep=',', decimal='.', infer_datetime_format=True)

    geometry = [sg.Point(x,y) for x,y in zip(_collectors.LongitudeDecimal, _collectors.LatitudeDecimal)]

    _collectors_geo_df = gpd.GeoDataFrame(_collectors, geometry=geometry)

    _collectors_geo_df = _collectors_geo_df.sort_values(by=['DiasAposInicioCiclo'])

    _collectors_geo_df = utils.clean_up(_collectors_geo_df)

    _collectors_geo_df['discovery_day'] = None
    _collectors_geo_df['id'] = _collectors_geo_df.index
    _collectors_geo_df.loc[_collectors_geo_df['Primeiro_Esporo'].notnull(), 'color'] = 'green'
    _collectors_geo_df.loc[_collectors_geo_df['Primeiro_Esporo'].isnull(), 'color'] = 'red'

    return _map, _collectors_geo_df

TEST_PARAMS = {
    'number_of_days' : 30,
    'growth_function_distance' : gf.logaritmic_growth_distance,
    'growth_function_days' : gf.logaritmic_growth_days,
    'base' : 200000,
    'animation' : False,
    'Fake_Collectors' : False,
    'raio_de_abrangencia_imediata' : 0.05,
    'raio_de_possivel_contaminacao' : 0.5,
}

old_geometries = []

_map, _collectors_geo_df = read_basic_info()

# ''' Circular Growth No Touch Test
start_day = _collectors_geo_df.query('DiasAposInicioCiclo != -1')['Primeiro_Esporo'].iloc[0]

true_positive_penalty, infection_circles, method_used = \
    gt.circular_growth_no_touch(_map, _collectors_geo_df, old_geometries, TEST_PARAMS)

true_negative_penalty = 0

false_positive_penalty = utils.calculate_false_positives_penalty(_collectors_geo_df, start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1))

false_negative_penalty = utils.calculate_false_negatives_penalty(_collectors_geo_df, TEST_PARAMS['growth_function_days'], TEST_PARAMS['base'])

PENALTIES = {
    'true_positive' : true_positive_penalty,
    'true_negative' : true_negative_penalty,
    'false_positive' : false_positive_penalty,
    'false_negative' : false_negative_penalty
}

print(f"TEST PARAMS: {TEST_PARAMS}")
print(f"True positive penalty: {true_positive_penalty}")
print(f"True negative penalty: {true_negative_penalty}")
print(f"False positive penalty: {false_positive_penalty}")
print(f"False negative penalty: {false_negative_penalty}")
# '''

''' Topology Test
collectors_instance = coletores.Coletores('LongitudeDecimal', 'LatitudeDecimal', 'Primeiro_Esporo')
collectors_instance.geo_df = _collectors_geo_df
collectors_instance.criaGrafo(_collectors_geo_df, TEST_PARAMS['raio_de_possivel_contaminacao'])
collectors_instance.geraTopologiasCrescimento(TEST_PARAMS['raio_de_abrangencia_imediata'], TEST_PARAMS['raio_de_possivel_contaminacao'], 0.01)

# If the parameter is set to true, the buffers are generated in a weird way, that is incorrect
buffers = cria_buffers.geraBuffersCarrapichos(collectors_instance.topologiaCrescimentoDict.values(), 0.005, True)
_map.plot()

for key, growth_topology in collectors_instance.topologiaCrescimentoDict.items():

    for segment in growth_topology.getSegments():

        seg = segment.seg
        plt.plot(*seg.xy, color='black', linewidth=0.5)

for _ in range(len(collectors_instance.geo_df)):

    center_point = collectors_instance.geo_df.iloc[_].geometry
    plt.scatter(center_point.x, center_point.y, color=collectors_instance.geo_df.iloc[_].color, s=5)
    plt.annotate(_, (center_point.x, center_point.y), fontsize=5)

for _ in range(len(buffers)):
    plt.plot(*buffers[_].exterior.xy, color='yellow', linewidth=0.5)

plt.show()

first_apperances  = _collectors_geo_df[_collectors_geo_df['DiasAposInicioCiclo'] == _collectors_geo_df['DiasAposInicioCiclo'].min()]

true_positive_penalty, infection_circles, method_used = \
    gt.circular_growth(_map, _collectors_geo_df, first_apperances, old_geometries, TEST_PARAMS)

gt.topology_growth(_map, collectors_instance, old_geometries, TEST_PARAMS, plt)

plt.show()
'''

if TEST_PARAMS['animation']: plt.show()