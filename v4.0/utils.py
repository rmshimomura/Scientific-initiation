import pandas as pd
import matplotlib.pyplot as plt
import datetime
from shapely.geometry import Point
import growth_functions as gf
import math
import os
import shapely
import shapely.geometry as sg
import geopandas as gpd

def write_csv(TEST_PARAMS: dict, PENALTIES: dict, start_day, end_day, method_used)-> None:


    # Retrive the keys from the dictionary
    keys = TEST_PARAMS.keys()
    values = TEST_PARAMS.values()

    # Check if the file data.csv exists
    if not os.path.exists('data.csv'):
        f = open('data.csv', 'w')
        f.write(f"{'Method,' + ','.join(keys) + ',Start_day,End_day,Test_time,TPP,TNP,FPP,FNP'}\n")
        f.close()
        
    f = open('data.csv', 'a')

    f.write(f"{method_used},{','.join(str(value) for value in values) + f',{start_day},{end_day},{datetime.datetime.now()},' + ','.join(str(value) for value in PENALTIES.values())}\n")

    f.close()

def clean_up(collectors_geo_data_frame: gpd.GeoDataFrame)-> gpd.GeoDataFrame: 
    # Reset index
    collectors_geo_data_frame.index = range(0, len(collectors_geo_data_frame)) 

    collectors_geo_data_frame = collectors_geo_data_frame.rename(columns={'Longitude Decimal': 'LongitudeDecimal'})
    collectors_geo_data_frame = collectors_geo_data_frame.rename(columns={'Latitude Decimal': 'LatitudeDecimal'})
    collectors_geo_data_frame = collectors_geo_data_frame.rename(columns={'Primeiro_Esporo': 'Primeiro_Esporo'})

    # Parse dates
    for i in range(0, len(collectors_geo_data_frame)):
        if not pd.isnull(collectors_geo_data_frame["Primeiro_Esporo"].iloc[i]):
            collectors_geo_data_frame.loc[i, 'Primeiro_Esporo'] = datetime.datetime.strptime(collectors_geo_data_frame["Primeiro_Esporo"].iloc[i], '%d/%m/%y')

    # Remove unecessary columns

    # Check if the column 'fake' exists
    if 'fake' in collectors_geo_data_frame.columns:
        collectors_geo_data_frame = collectors_geo_data_frame.drop(columns=['fake'])
    
    if 'Cultivar' in collectors_geo_data_frame.columns:
        collectors_geo_data_frame = collectors_geo_data_frame.drop(columns=['Cultivar'])

    if 'Estadio Fenologico' in collectors_geo_data_frame.columns:
        collectors_geo_data_frame = collectors_geo_data_frame.drop(columns=['Estadio Fenologico'])

    collectors_geo_data_frame['Detected'] = 0

    return collectors_geo_data_frame

def show_detected_collectors_city_names(_collectors: pd.DataFrame, plt: plt)-> None:
    for i in range(len(_collectors)):
        # Show only cities with collectors with spores
        if _collectors.loc[i, 'Situacao'] == 'Com esporos': 
            plt.gca().annotate(_collectors['Cidade'][i], (_collectors['LongitudeDecimal'][i], _collectors['LatitudeDecimal'][i]), fontsize=7)

def count_valid_collectors(_collectors: pd.DataFrame)-> int:
    number_of_valid_collectors = 0

    for i in range(0, len(_collectors)):
        if pd.notnull(_collectors['Primeiro_Esporo'].iloc[i]):
            number_of_valid_collectors += 1

    return number_of_valid_collectors

def calculate_false_positives_penalty(_collectors: pd.DataFrame, final_day: datetime.timedelta)-> int:
    
    penalty = 0
    false_positives = 0

    for i in range(0, len(_collectors)):
        if pd.isnull(_collectors['Primeiro_Esporo'].iloc[i]) and _collectors['Detected'].iloc[i] == 1:
            penalty += (abs(final_day - _collectors['discovery_day'].iloc[i]).days ** 2)
            false_positives += 1

    penalty = math.sqrt(penalty/false_positives)

    return penalty

def calculate_false_negatives_penalty(_collectors: pd.DataFrame, growth_function, base)-> int:

    penalty = 0

    false_negatives = 0

    not_detected_positive_collectors = _collectors.query('Detected == 0 and Situacao == "Com esporos"')

    for i in range(0, len(not_detected_positive_collectors)):

        distance_to_reach = find_closest_positive_collector(_collectors, not_detected_positive_collectors.iloc[i])

        days_to_reach = growth_function(distance_to_reach, base)

        penalty += abs(days_to_reach ** 2)

        false_negatives += 1

        print(f"Distance to reach: {distance_to_reach * 111.45}km, days to reach: {days_to_reach}")

    if penalty > 0:
        penalty = math.sqrt(penalty/false_negatives)

    return penalty

def find_closest_positive_collector(_collectors: pd.DataFrame, collector: pd.DataFrame)-> pd.DataFrame:

    collectors_with_spores = _collectors[_collectors['Situacao'] == 'Com esporos']

    # closest_collector = collectors_with_spores.iloc[0]
    closest_collector = None
    # closest_point = Point(closest_collector['LongitudeDecimal'], closest_collector['LatitudeDecimal'])
    closest_point = None
    collector_point = Point(collector['LongitudeDecimal'], collector['LatitudeDecimal'])

    for i in range(0, len(collectors_with_spores)):

        if collectors_with_spores.iloc[i].id != collector.id:

            if closest_collector is None:

                closest_collector = collectors_with_spores.iloc[i]
                closest_point = Point(closest_collector['LongitudeDecimal'], closest_collector['LatitudeDecimal'])

            else: 

                iterator_point = Point(collectors_with_spores.iloc[i]['LongitudeDecimal'], collectors_with_spores.iloc[i]['LatitudeDecimal'])

                if iterator_point.distance(collector_point) < closest_point.distance(collector_point):
                    closest_point = iterator_point
                    closest_collector = collectors_with_spores.iloc[i]

    return closest_point.distance(collector_point)

def debug_burr(_map, burr_buffer, _collectors, plt):

    _map.plot(color='lightgrey', edgecolor='grey', linewidth=0.5)
    plt.scatter(_collectors['LongitudeDecimal'], _collectors['LatitudeDecimal'], c=_collectors['color'])
    for i in range(len(_collectors)):
        # plt.plot(_collectors['LongitudeDecimal'].iloc[i], _collectors['LatitudeDecimal'].iloc[i], 'o', color='black', markersize=5)
        x, y = burr_buffer[int(_collectors['burr'].iloc[i])].exterior.xy
        plt.plot(x, y, color='red', alpha=0.7, linewidth=3, solid_capstyle='round')

def check_burr(_map, burr_buffer, _collectors, plt):

    _map.plot(color='lightgrey', edgecolor='grey', linewidth=0.5)
    for i in range(len(burr_buffer)):
        x, y = burr_buffer[i].exterior.xy
        plt.plot(x, y, color='red', alpha=0.7, linewidth=3, solid_capstyle='round')
        plt.plot(_collectors['LongitudeDecimal'].iloc[i], _collectors['LatitudeDecimal'].iloc[i], 'o', color='black', markersize=5)
        plt.pause(0.1)
    plt.show()

def treat_position(origin, point_found, c_radius):
    
    result_point = []

    if point_found.x == origin.x:
        if point_found.y < origin.y:
            return Point(point_found.x, point_found.y - c_radius)
        else:
            return Point(point_found.x, point_found.y + c_radius)
    elif point_found.y == origin.y:
        if point_found.x < origin.x:
            return Point(point_found.x - c_radius, point_found.y)
        else:
            return Point(point_found.x + c_radius, point_found.y)

    slope = (point_found.y - origin.y) / (point_found.x - origin.x)

    if point_found.x < origin.x:
        result_point.append(point_found.x - abs((math.cos(math.atan(slope)) * c_radius)))
    else:
        result_point.append(point_found.x + abs((math.cos(math.atan(slope)) * c_radius)))
    if point_found.y < origin.y:
        result_point.append(point_found.y - abs((math.sin(math.atan(slope)) * c_radius)))
    else:
        result_point.append(point_found.y + abs((math.sin(math.atan(slope)) * c_radius)))
    
    return Point(result_point[0], result_point[1])

def grid_region(_map, _collectors, root_folder):

    global file_name, year_analyzed, horizontal_len, vertical_len

    # horizontal_len = math.ceil(total_length / 0.1)
    # vertical_len = math.ceil(total_height / 0.1)
    horizontal_len = 31
    vertical_len = 23

    new_points_data = open(f"G:/{root_folder}/IC/Codes/v3.0/new_points/{file_name}_{horizontal_len}_{vertical_len}.csv", 'w')

    new_points_data.write('Mesorregiao,Regiao,Municipio,Produtor,Cultivar,LatitudeDecimal,LongitudeDecimal,Primeiro_Esporo,Estadio Fenologico,Situacao,Dias_apos_O0,InicioCiclo,DiasAposInicioCiclo\n')

    min_point = _map.total_bounds[0:2]
    max_point = _map.total_bounds[2:4]
    total_length = max_point[0] - min_point[0]
    total_height = max_point[1] - min_point[1]

    boxes = []

    map_exterior_geometry = shapely.ops.unary_union(_map.geometry).buffer(0.2)

    ## Create a datetime date for september 10th with year = year_analyzed
    september_10th = datetime.datetime(year_analyzed, 9, 10)

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
        
        # Pick all points inside the box
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

        # Search for the earliest apperance day
        for point in points_inside_box:

            if point.Primeiro_Esporo is not None and not pd.isnull(point.Primeiro_Esporo):

                if first_apperance_day is None:

                    first_apperance_day = point.Primeiro_Esporo    
                    center_point['Situacao'] = point.Situacao

                elif first_apperance_day > point.Primeiro_Esporo:

                    first_apperance_day = point.Primeiro_Esporo

        if first_apperance_day is not None:

            center_point['Primeiro_Esporo'] = first_apperance_day

        # If any point detected a spore
        if center_point['Primeiro_Esporo'] is not None:

            days_differ = (center_point['Primeiro_Esporo'] - september_10th).days

            new_points_data.write(f",,,,,{center_point['LatitudeDecimal']},{center_point['LongitudeDecimal']},{center_point['Primeiro_Esporo'].strftime('%d/%m/%y')},,{center_point['Situacao']},,{september_10th.strftime('%d/%m/%y')},{days_differ}\n")
        
        # If no point detected a spore
        else:
            
            new_points_data.write(f",,,,,{center_point['LatitudeDecimal']},{center_point['LongitudeDecimal']},,,{center_point['Situacao']},,{september_10th.strftime('%d/%m/%y')},\n")
    