import pandas as pd
import matplotlib.pyplot as plt
import datetime
from shapely.geometry import Point
import growth_functions as gf
import math
import csv

def write_csv(TEST_PARAMS: dict, PENALTIES: dict, start_day, end_day)-> None:

    f = open('data.csv', 'w')

    # For each key in TEST_PARAMS, write to a csv file
    for key in TEST_PARAMS:
        if key == 'growth_function_distance':
            f.write("%s,%s \n" % (key, TEST_PARAMS[key].__name__))
        elif key == 'growth_function_days':
            f.write("%s,%s \n" % (key, TEST_PARAMS[key].__name__))
        else:
            f.write("%s,%s \n" % (key, TEST_PARAMS[key]))
        
    # For each key in PENALTIES, write to a csv file
    for key in PENALTIES:
        f.write("%s,%s \n" % (key, PENALTIES[key]))

    f.write("Start day,%s \n" % start_day)

    f.write("End day,%s \n" % end_day)

    f.close()



def clean_up(_collectors: pd.DataFrame)-> pd.DataFrame: 
    # Reset index
    _collectors.index = range(0, len(_collectors)) 

    # Parse dates
    for i in range(0, len(_collectors)):
        if not pd.isnull(_collectors["Data_1o_Esporos"].iloc[i]):
            _collectors.loc[i, 'Data_1o_Esporos'] = _collectors["Data_1o_Esporos"].iloc[i].strftime('%Y-%m-%d')        

    # Remove unecessary columns
    _collectors = _collectors.drop(columns=['Cultivar', 'Estadio'])
    
    _collectors['Detected'] = 0

    return _collectors

def show_detected_collectors_city_names(_collectors: pd.DataFrame, plt: plt)-> None:
    for i in range(len(_collectors)):
        # Show only cities with collectors with spores
        if _collectors.loc[i, 'Situacao'] == 'Com esporos': 
            plt.gca().annotate(_collectors['Municipio'][i], (_collectors['Longitude'][i], _collectors['Latitude'][i]), fontsize=7)

def count_valid_collectors(_collectors: pd.DataFrame)-> int:
    number_of_valid_collectors = 0

    for i in range(0, len(_collectors)):
        if pd.notnull(_collectors['Data_1o_Esporos'].iloc[i]):
            number_of_valid_collectors += 1

    return number_of_valid_collectors

def calculate_false_positives_penalty(_collectors: pd.DataFrame, final_day: datetime.timedelta)-> int:
    
    penalty = 0
    false_positives = 0

    for i in range(0, len(_collectors)):
        if pd.isnull(_collectors['Data_1o_Esporos'].iloc[i]) and _collectors['Detected'].iloc[i] == 1:
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
    closest_point = Point(closest_collector['Longitude'], closest_collector['Latitude'])
    collector_point = Point(collector['Longitude'], collector['Latitude'])

    for i in range(0, len(collectors_with_spores)):

        iterator_point = Point(collectors_with_spores.iloc[i]['Longitude'], collectors_with_spores.iloc[i]['Latitude'])

        if iterator_point.distance(collector_point) < closest_point.distance(collector_point):
            closest_point = iterator_point
            closest_collector = collectors_with_spores.iloc[i]

    return closest_point.distance(collector_point)