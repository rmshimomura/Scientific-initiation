import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import os
import datetime


for filename in os.listdir('Results'):
    os.remove(f'Results/{filename}')

_map = gpd.read_file('Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') # Read map file
_collectors = pd.read_csv('Data/Collectors/2021/ColetoresSafra2122.csv', sep=';', decimal=',', parse_dates=['Data_1o_Esporos'], infer_datetime_format=True).sort_values(by='Data_1o_Esporos') # Read collectors file

_collectors.index = range(0, len(_collectors)) # Reset index

for i in range(0, len(_collectors)):
    # print _collectors["Data"].iloc[i] only if the value is not nan
    if not pd.isnull(_collectors["Data_1o_Esporos"].iloc[i]):
        _collectors.loc[i, 'Data_1o_Esporos'] = _collectors["Data_1o_Esporos"].iloc[i].strftime('%Y-%m-%d')
        print(_collectors["Data_1o_Esporos"].iloc[i])


# print(_collectors["Data_1o_Esporos"].iloc[0] + datetime.timedelta(days=2))

old_circles = []

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

        infection_circle = Point(first_apperances['Longitude'].iloc[i], first_apperances['Latitude'].iloc[i]).buffer(0.01 * 1) # Create a new infection circle
        infection_circles.append([i, infection_circle, 1]) # Add the infection circle to the list
        
    for day in range(number_of_days): # For each day

        for infection_circle_index in range(len(infection_circles)): # For each infection circle

            for collector_index in range(len(_collectors)): # For each collector

                current_color = _collectors['color'].iloc[collector_index]

                if current_color == 'yellow' or current_color == 'red': # Prevent re-infection and collectors that don't have spores
                    continue
                else:
                    if infection_circles[infection_circle_index][1].contains(Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index])):
                        _collectors.loc[collector_index, 'color'] = 'yellow'
                        new_buffer = 1
                        new_infection_circle = Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index]).buffer(0.01 * new_buffer)
                        infection_circles.append([collector_index, new_infection_circle, new_buffer])

        for infection_circle_index in range(len(infection_circles)): # For each day passed, the infection circle grows
            infection_circles[infection_circle_index][2] += 1
            infection_circles[infection_circle_index][1] = Point(infection_circles[infection_circle_index][1].centroid.x, infection_circles[infection_circle_index][1].centroid.y).buffer(0.01 * infection_circles[infection_circle_index][2])

        plotting(day)

def plotting(day):

    if day == 0:
        # Map plot
        _map.plot(color='lightgrey', edgecolor='whitesmoke')

        # Title and labels definitions
        plt.title('Ferrugem asiática no Paraná', fontsize=20)
        plt.xlabel('Longitude', fontsize=15)
        plt.ylabel('Latitude', fontsize=15)
        
        for i in range(len(_collectors)):
            if _collectors.loc[i, 'Situacao'] == 'Com esporos': # Show only cities with collectors with spores
                plt.gca().annotate(_collectors['Municipio'][i], (_collectors['Longitude'][i], _collectors['Latitude'][i]), fontsize=2)

    for old_infection_circle in old_circles:
        old_infection_circle.pop(0).remove()
    
    old_circles.clear()

    plot_infection_circles()

    plt.scatter(_collectors['Longitude'], _collectors['Latitude'], color=_collectors['color'], s=50, marker='*')

    plt.savefig(f'Results/Day_{day}.png', dpi=300, bbox_inches='tight')

def plot_infection_circles():

    intersection_union()

    for i in range(len(infection_circles)):

        old_circles.append(plt.plot(*infection_circles[i][1].exterior.xy, color='black', linewidth=1))

def intersection_union():

    i = 0
    j = 1

    while i < len(infection_circles):
        while j < len(infection_circles):
            if infection_circles[i][1].intersects(infection_circles[j][1]):
                infection_circles[i][1] = infection_circles[i][1].union(infection_circles[j][1])
                infection_circles.pop(j)
            else:
                j += 1
        i += 1
        j = i + 1

coloring()
growth(number_of_days=20)