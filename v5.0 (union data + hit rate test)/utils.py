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

def clean_up(collectors_geo_data_frame: gpd.GeoDataFrame)-> gpd.GeoDataFrame: 
    # Reset index
    collectors_geo_data_frame.index = range(0, len(collectors_geo_data_frame)) 

    collectors_geo_data_frame = collectors_geo_data_frame.rename(columns={'Longitude Decimal': 'LongitudeDecimal'})
    collectors_geo_data_frame = collectors_geo_data_frame.rename(columns={'Latitude Decimal': 'LatitudeDecimal'})
    collectors_geo_data_frame = collectors_geo_data_frame.rename(columns={'Primeiro_Esporo': 'Primeiro_Esporo'})
    
    if 'Cultivar' in collectors_geo_data_frame.columns:
        collectors_geo_data_frame = collectors_geo_data_frame.drop(columns=['Cultivar'])

    if 'Estadio Fenologico' in collectors_geo_data_frame.columns:
        collectors_geo_data_frame = collectors_geo_data_frame.drop(columns=['Estadio Fenologico'])

    collectors_geo_data_frame['Detected'] = 0

    return collectors_geo_data_frame

def calculate_false_positives_penalty(_collectors: pd.DataFrame, final_day: datetime.timedelta)-> int:
    
    penalty = 0
    false_positives = 0

    days_column = 'DiasAposInicioCiclo' if 'DiasAposInicioCiclo' in _collectors.columns else 'MediaDiasAposInicioCiclo'

    for i in range(0, len(_collectors)):
        if _collectors[days_column].iloc[i] == -1 and _collectors['Detected'].iloc[i] == 1:
            penalty += (abs(final_day - _collectors['discovery_day'].iloc[i])** 2)
            false_positives += 1

    penalty = 0 if false_positives == 0 else math.sqrt(penalty/false_positives)

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


    penalty = 0 if false_negatives == 0 else math.sqrt(penalty/false_negatives)

    return penalty

def find_closest_positive_collector(_collectors: pd.DataFrame, collector: pd.DataFrame)-> pd.DataFrame:

    collectors_with_spores = _collectors[_collectors['Situacao'] == 'Com esporos']

    closest_collector = None
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
