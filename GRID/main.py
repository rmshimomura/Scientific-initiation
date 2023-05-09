import geopandas as gpd
import pandas as pd
import utils
import matplotlib.pyplot as plt
import os
import shapely.geometry as sg
import shapely.ops
import math

root_folder = None

if 'Meu Drive' in os.getcwd():
    root_folder = 'Meu Drive'
elif 'My Drive' in os.getcwd():
    root_folder = 'My Drive'

def read_basic_info():

    global root_folder

    _map = gpd.read_file('G:/' + root_folder + '/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 
    # _collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/With_Burrs/coletoressafra2122.csv', sep=',', decimal='.', infer_datetime_format=True)
    _collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/NEW_DATA/coletores2223.csv', sep=',', decimal='.', infer_datetime_format=True)
    _collectors = _collectors.sort_values(by=['Primeiro_Esporo'])
    
    if 'carrap' in _collectors.columns:
        _collectors.drop(['carrap'], axis=1, inplace=True)

    _collectors = utils.clean_up(_collectors)

    _collectors['discovery_day'] = None
    _collectors['Fake'] = False

    return _map, _collectors

def coloring_collectors(_collectors):

    _collectors.loc[_collectors['Primeiro_Esporo'].notnull(), 'color'] = 'green'
    _collectors.loc[_collectors['Primeiro_Esporo'].isnull(), 'color'] = 'red'

def grid_region(_map, _collectors):
    _map.plot(color='white', edgecolor='lightgrey')
    for i in _collectors.itertuples():
        plt.plot(i.LongitudeDecimal, i.LatitudeDecimal, 'o', color=i.color, zorder=2)

    # Pick the most extreme points of the map
    min_point = _map.total_bounds[0:2]
    max_point = _map.total_bounds[2:4]

    # Calculate the total length and height of the map
    total_length = max_point[0] - min_point[0]
    total_height = max_point[1] - min_point[1]

    boxes = []

    map_exterior_geometry = shapely.ops.unary_union(_map.geometry).buffer(0.1)

    global horizontal_len, vertical_len

    horizontal_len = math.ceil(total_length / 0.1)
    vertical_len = math.ceil(total_height / 0.1)

    for i in range(horizontal_len):
        for j in range(vertical_len):
            new_box = sg.box(min_point[0] + (total_length * i / horizontal_len),
                            min_point[1] + (total_height * j / vertical_len),
                            min_point[0] + (total_length * (i + 1) / horizontal_len),
                            min_point[1] + (total_height * (j + 1) / vertical_len)
                            )            
            if map_exterior_geometry.contains(new_box):
                boxes.append(new_box)

    for box in boxes:
        contains = False
        for i in _collectors.itertuples():
            collector_point = sg.Point(i.LongitudeDecimal, i.LatitudeDecimal)
            if box.contains(collector_point) or box.touches(collector_point):
                if not pd.isna(i.Primeiro_Esporo):
                    contains = True
                    break

        if contains:
            x, y = box.exterior.xy
            plt.fill(x, y, fc='green', ec='k', alpha=0.2, zorder=1)
        else:
            x, y = box.exterior.xy
            plt.fill(x, y, fc='red', ec='k', alpha=0.2, zorder=1)
    



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
    'base' : 200000,
    'animation' : True,
    'Fake_Collectors' : False,
}

_map, _collectors = read_basic_info()
coloring_collectors(_collectors)

# if TEST_PARAMS['Fake_Collectors']:
#     if not os.path.exists('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/Fake_Collectors.csv'):
#         add_fake_collectors(_collectors)

#     _collectors = update_with_fake_collectors(_collectors)

# new_data = pd.read_csv('G:/' + root_folder + '/IC/Codes/NEW_DATA/coletores2223.csv', sep=',', decimal='.', infer_datetime_format=True)
# new_data = utils.clean_up(new_data)

grid_region(_map, _collectors)

# Plot map

# Plot all points of new_data
# for i in new_data.itertuples():
#     plt.plot(i.LongitudeDecimal, i.LatitudeDecimal, '*', color='blue')
plt.savefig('G:/' + root_folder + f'/IC/Codes/GRID/TESTS/Mapa_{horizontal_len}-{vertical_len}.png', dpi=300)
plt.show()