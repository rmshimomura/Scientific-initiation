import geopandas as gpd
import pandas as pd
import utils
import growth_functions as gf
import matplotlib.pyplot as plt
import os
import shapely.geometry as sg
import shapely.ops
import math
import shapely.affinity as sa

root_folder = None

if 'Meu Drive' in os.getcwd():
    root_folder = 'Meu Drive'
elif 'My Drive' in os.getcwd():
    root_folder = 'My Drive'

file_name = 'coletoressafra2021'

def read_basic_info():

    global root_folder, burr_buffer, file_name

    # Read map file
    _map = gpd.read_file('G:/' + root_folder + '/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    # Read collectors file
    # _collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Collectors/2021/With_Burrs/' + file_name + '.csv', sep=',', decimal='.', infer_datetime_format=True)
    _collectors = pd.read_csv('G:/My Drive/IC/Codes/NEW_DATA/coletoressafra2223.csv', sep=',', decimal='.', infer_datetime_format=True)

    # Make burr_buffer equal to a list of the last column of the _collectors dataframe
    _collectors = _collectors.sort_values(by=['Primeiro_Esporo'])

    burr_buffer = []
    if 'carrap' in _collectors.columns:
        if not pd.isna(_collectors['carrap']).any():
            burr_buffer = _collectors['carrap'].tolist()

    # Create buffers from burrs string
    for i in range(len(burr_buffer)):
        clear_string = burr_buffer[i].replace('POLYGON ((', '').replace('))', '').split(', ')
        for j in range(len(clear_string)):
            clear_string[j] = clear_string[j].split(' ')
            clear_string[j] = [float(clear_string[j][0]), float(clear_string[j][1])]

        burr_buffer[i] = sg.Polygon(clear_string)

    _collectors = utils.clean_up(_collectors)

    if len(burr_buffer) > 0:
        _collectors['burr'] = range(0, len(burr_buffer))

    _collectors['discovery_day'] = None
    _collectors['Fake'] = False


    return _map, _collectors

def coloring_collectors(_collectors):

    _collectors.loc[_collectors['Primeiro_Esporo'].notnull(), 'color'] = 'green'
    _collectors.loc[_collectors['Primeiro_Esporo'].isnull(), 'color'] = 'red'

def grid_region(_map, _collectors, burr_buffer):

    global file_name

    # _map.plot(color='white', edgecolor='lightgrey')

    new_points_data = open('G:/' + root_folder + '/IC/Codes/v.3.0/new_points/' + file_name + '.csv', 'w')

    new_points_data.write(',Mesorregiao,Regiao,Municipio,Produtor,Cultivar,LatitudeDecimal,LongitudeDecimal,Primeiro_Esporo,Estadio Fenologico,Situacao,Dias_apos_O0,Data,geometry,fake,carrap\n')

    min_point = _map.total_bounds[0:2]
    max_point = _map.total_bounds[2:4]
    total_length = max_point[0] - min_point[0]
    total_height = max_point[1] - min_point[1]

    boxes = []

    map_exterior_geometry = shapely.ops.unary_union(_map.geometry).buffer(0.2)

    global horizontal_len, vertical_len

    # horizontal_len = math.ceil(total_length / 0.1)
    # vertical_len = math.ceil(total_height / 0.1)
    horizontal_len = 31
    vertical_len = 23

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
        
        points_inside_box = []
        for i in _collectors.itertuples():
            collector_point = sg.Point(i.LongitudeDecimal, i.LatitudeDecimal)
            if box.contains(collector_point) or box.touches(collector_point):
                if not pd.isna(i.Primeiro_Esporo):

                    points_inside_box.append(i)

        first_apperance_day = None

        center_point = {
            'LongitudeDecimal': box.centroid.x,
            'LatitudeDecimal': box.centroid.y,
            'Primeiro_Esporo': None,
            'Situacao': 'Encerrado sem esporos'
        }

        for point in points_inside_box:

            if point.Primeiro_Esporo is not None and not pd.isnull(point.Primeiro_Esporo):
                if first_apperance_day is None:
                    first_apperance_day = point.Primeiro_Esporo    
                    center_point['Situacao'] = point.Situacao
                elif first_apperance_day > point.Primeiro_Esporo:
                    first_apperance_day = point.Primeiro_Esporo

        if first_apperance_day is not None:

            center_point['Primeiro_Esporo'] = first_apperance_day

        if center_point['Primeiro_Esporo'] is not None:

            new_points_data.write(f",,,,,,{center_point['LatitudeDecimal']},{center_point['LongitudeDecimal']},{center_point['Primeiro_Esporo'].strftime('%y-%m-%d').replace('-', '/')},,{center_point['Situacao']},,,,False,\n")
        
        else:
            
            new_points_data.write(f",,,,,,{center_point['LatitudeDecimal']},{center_point['LongitudeDecimal']},,,{center_point['Situacao']},,,,False\n")

        # if len(burrs_inside_box) == 0:
        #     pass
        #     # plt.plot(box_centroid.x, box_centroid.y, 'o', color='black', zorder=3, solid_capstyle='round', linewidth=0.2, alpha=0.5, markersize=1)

        # elif len(burrs_inside_box) > 0:
            

        #     for _ in burrs_inside_box:
        #         x, y = _.exterior.xy
        #         plt.plot(x, y, color='black', zorder=3, solid_capstyle='round', linewidth=1, alpha=0.5)

        #     plt.plot(box_centroid.x, box_centroid.y, '*', color='blue', zorder=3, solid_capstyle='round', linewidth=1, alpha=0.5, markersize=10)

        # if contains:
        #     x, y = box.exterior.xy
        #     plt.fill(x, y, fc='green', ec='k', alpha=0.15, zorder=1)
        # else:
        #     x, y = box.exterior.xy
        #     plt.fill(x, y, fc='red', ec='k', alpha=0.15, zorder=1)

    # for i in _collectors.itertuples():

    #     if not pd.isna(i.Primeiro_Esporo):

    #         plt.plot(i.LongitudeDecimal, i.LatitudeDecimal, color=i.color, zorder=2, markersize=5, marker='o')
        
    #     else:

    #         plt.plot(i.LongitudeDecimal, i.LatitudeDecimal, color='black', zorder=2, markersize=5, marker='^')
    
    
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

grid_region(_map, _collectors, burr_buffer)

plt.show()