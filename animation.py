import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import os
import datetime
from infection_circle import Infection_Circle

def coloring():
    
    global first_apperances

    _collectors['color'] = _collectors['Situacao'].apply(lambda x: 'lightgreen' if x == 'Com esporos' else 'red') # Color collectors with spores in green and collectors without spores in red
    first_apperances = _collectors[_collectors['Data_1o_Esporos'] == _collectors['Data_1o_Esporos'].min()] # Get the first collectors to appear

    for i in first_apperances.index: # Color the first collectors to appear in yellow
        _collectors.loc[i, 'color'] = 'yellow'
        
def growth(number_of_days):

    global infection_circles

    infection_circles = []

    for i in range(len(first_apperances)): # For each starting point

        infection_circle = Point(first_apperances['Longitude'].iloc[i], first_apperances['Latitude'].iloc[i]).buffer(0.01) # Create a new infection circle
        infection_circles.append(Infection_Circle(i, infection_circle, 1))

    for day in range(number_of_days): # For each day

        for _infection_circle in infection_circles:

            for collector_index in range(len(_collectors)):

                current_color = _collectors['color'].iloc[collector_index]

                if current_color == 'yellow' or current_color == 'red': # Prevent re-infection and collectors that don't have spores
                    continue
                else:

                    if _infection_circle.circle.contains(Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index])):

                        _collectors.loc[collector_index, 'color'] = 'yellow'

                        if _collectors['Data_1o_Esporos'].iloc[_infection_circle.index] + datetime.timedelta(day) < _collectors['Data_1o_Esporos'].iloc[collector_index]:
                            print(f"{_collectors['Data_1o_Esporos'].iloc[_infection_circle.index] + datetime.timedelta(day)} < {_collectors['Data_1o_Esporos'].iloc[collector_index]}")
                            print(f"-{_collectors['Data_1o_Esporos'].iloc[collector_index] - (_collectors['Data_1o_Esporos'].iloc[_infection_circle.index] + datetime.timedelta(day))}")
                        elif _collectors['Data_1o_Esporos'].iloc[_infection_circle.index] + datetime.timedelta(day) > _collectors['Data_1o_Esporos'].iloc[collector_index]:
                            print(f"{_collectors['Data_1o_Esporos'].iloc[_infection_circle.index] + datetime.timedelta(day)} > {_collectors['Data_1o_Esporos'].iloc[collector_index]}")
                            print(f"+{_collectors['Data_1o_Esporos'].iloc[_infection_circle.index] + datetime.timedelta(day) - _collectors['Data_1o_Esporos'].iloc[collector_index]}")
                        else:
                            print(f"{_collectors['Data_1o_Esporos'].iloc[_infection_circle.index] + datetime.timedelta(day)} = {_collectors['Data_1o_Esporos'].iloc[collector_index]}")

                        new_buffer = 1
                        new_infection_circle = Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index]).buffer(0.01 * new_buffer)
                        infection_circles.append(Infection_Circle(collector_index, new_infection_circle, new_buffer))

        for _infection_circle in infection_circles: # For each day passed, the infection circle grows

            _infection_circle.buffer += 1
            _infection_circle.circle = Point(_infection_circle.circle.centroid.x, _infection_circle.circle.centroid.y).buffer(0.01 * _infection_circle.buffer)

        plotting(day)

def plotting(day):

    if day == 0:
        # Map plot
        _map.plot(color='lightgrey', edgecolor='whitesmoke')

        # Title and labels definitions
        
        plt.xlabel('Longitude', fontsize=15)
        plt.ylabel('Latitude', fontsize=15)
        
        for i in range(len(_collectors)):
            if _collectors.loc[i, 'Situacao'] == 'Com esporos': # Show only cities with collectors with spores
                plt.gca().annotate(_collectors['Municipio'][i], (_collectors['Longitude'][i], _collectors['Latitude'][i]), fontsize=2)

    plt.title(f'Ferrugem asiática no Paraná - dia {day}', fontsize=20)

    for old_infection_circle in old_circles:
        old_infection_circle.pop(0).remove()
    
    old_circles.clear()

    plot_infection_circles()

    plt.scatter(_collectors['Longitude'], _collectors['Latitude'], color=_collectors['color'], s=50, marker='*')

    plt.pause(0.1)

def plot_infection_circles():

    for i in range(len(infection_circles)):

        old_circles.append(plt.plot(*infection_circles[i].circle.exterior.xy, color='black', linewidth=1))

def intersection_union():

    i = 0
    j = 1

    while i < len(infection_circles):
        while j < len(infection_circles):
            if infection_circles[i].circle.intersects(infection_circles[j].circle):
                infection_circles[i].circle = infection_circles[i].circle.union(infection_circles[j].circle)
                infection_circles.pop(j)
            else:
                j += 1
        i += 1
        j = i + 1

for filename in os.listdir('Results'):
    os.remove(f'Results/{filename}')

_map = gpd.read_file('Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') # Read map file
_collectors = pd.read_csv('Data/Collectors/2021/ColetoresSafra2122.csv', sep=';', decimal=',', parse_dates=['Data_1o_Esporos'], infer_datetime_format=True) \
            .sort_values(by='Data_1o_Esporos') # Read collectors file

_collectors.index = range(0, len(_collectors)) # Reset index

for i in range(0, len(_collectors)):
    if not pd.isnull(_collectors["Data_1o_Esporos"].iloc[i]):
        _collectors.loc[i, 'Data_1o_Esporos'] = _collectors["Data_1o_Esporos"].iloc[i].strftime('%Y-%m-%d')
        
old_circles = []

coloring()
growth(number_of_days=100)
intersection_union()
plt.show()