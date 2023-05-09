import pandas as pd
import matplotlib.pyplot as plt
import datetime
from shapely.geometry import Point
import math
import geopandas as gpd
import os

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
            try:
                _collectors.loc[i, 'Primeiro_Esporo'] = datetime.datetime.strptime(_collectors["Primeiro_Esporo"].iloc[i], '%d/%m/%y')
            except:
                _collectors.loc[i, 'Primeiro_Esporo'] = datetime.datetime.strptime(_collectors["Primeiro_Esporo"].iloc[i], '%d/%m/%Y')

    # Remove unecessary columns

    # Check if the column 'fake' exists
    if 'fake' in _collectors.columns:
        _collectors = _collectors.drop(columns=['fake'])
    
    if 'Cultivar' in _collectors.columns:
        _collectors = _collectors.drop(columns=['Cultivar'])

    if 'Estadio Fenologico' in _collectors.columns:
        _collectors = _collectors.drop(columns=['Estadio Fenologico'])

    _collectors['Detected'] = 0

    return _collectors

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