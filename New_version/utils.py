import pandas as pd
import matplotlib.pyplot as plt
import datetime
from shapely.geometry import Point
import growth_functions as gf
import math
import geopandas as gpd
import os

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

def clean_up(_collectors: pd.DataFrame)-> pd.DataFrame: 
    # Reset index
    _collectors.index = range(0, len(_collectors)) 

    _collectors = _collectors.rename(columns={'Longitude Decimal': 'LongitudeDecimal'})
    _collectors = _collectors.rename(columns={'Latitude Decimal': 'LatitudeDecimal'})
    _collectors = _collectors.rename(columns={'Primeiro_Esporo': 'Primeiro_Esporo'})

    # Parse dates
    for i in range(0, len(_collectors)):
        if not pd.isnull(_collectors["Primeiro_Esporo"].iloc[i]):
            # _collectors.loc[i, 'Primeiro_Esporo'] = _collectors["Primeiro_Esporo"].iloc[i].strftime('%Y/%m/%d')
            _collectors.loc[i, 'Primeiro_Esporo'] = datetime.datetime.strptime(_collectors["Primeiro_Esporo"].iloc[i], '%d/%m/%y')

    # Remove unecessary columns
    _collectors = _collectors.drop(columns=['Cultivar', 'Estadio Fenologico', 'fake'])

    _collectors['Detected'] = 0

    return _collectors

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

    not_detected_collectors = _collectors[_collectors['Detected'] == 0]

    for i in range(0, len(not_detected_collectors)):

        distance_to_reach = find_closest_positive_collector(_collectors, not_detected_collectors.iloc[i])

        days_to_reach = growth_function(distance_to_reach, base)

        penalty += abs(days_to_reach ** 2)

        false_negatives += 1

    if penalty > 0:
        penalty = math.sqrt(penalty/false_negatives)

    return penalty

def find_closest_positive_collector(_collectors: pd.DataFrame, collector: pd.DataFrame)-> pd.DataFrame:

    collectors_with_spores = _collectors[_collectors['Situacao'] == 'Com esporos']

    closest_collector = collectors_with_spores.iloc[0]
    closest_point = Point(closest_collector['LongitudeDecimal'], closest_collector['LatitudeDecimal'])
    collector_point = Point(collector['LongitudeDecimal'], collector['LatitudeDecimal'])

    for i in range(0, len(collectors_with_spores)):

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
        x, y = burr_buffer[_collectors['burr'].iloc[i]].exterior.xy
        plt.plot(x, y, color='red', alpha=0.7, linewidth=3, solid_capstyle='round')
    plt.show()

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