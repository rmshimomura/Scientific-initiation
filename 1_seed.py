import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import datetime
from infection_circle import Infection_Circle

def read_basic_info():
    _map = gpd.read_file('Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') # Read map file
    _collectors = pd.read_csv('Data/Collectors/2021/ColetoresSafra2122.csv', sep=';', decimal=',', parse_dates=['Data_1o_Esporos'], infer_datetime_format=True) \
            .sort_values(by='Data_1o_Esporos') # Read collectors file
    _collectors.index = range(0, len(_collectors)) # Reset index
    for i in range(0, len(_collectors)):
        if not pd.isnull(_collectors["Data_1o_Esporos"].iloc[i]):
            _collectors.loc[i, 'Data_1o_Esporos'] = _collectors["Data_1o_Esporos"].iloc[i].strftime('%Y-%m-%d')
        
    return _map, _collectors


def coloring():
    
    global first_apperances

    _collectors['color'] = _collectors['Situacao'].apply(lambda x: 'blue' if x == 'Com esporos' else 'white') # Color collectors with spores in green and collectors without spores in red
    first_apperances = _collectors[_collectors['Data_1o_Esporos'] == _collectors['Data_1o_Esporos'].min()] # Get the first collectors to appear

    for i in first_apperances.index: # Color the first collectors to appear in yellow
        _collectors.loc[i, 'color'] = 'yellow'
       
def check_day(day, collector_index):
    
    global early_detection, late_detection, spot_on_detection

    if collector_index < len(first_apperances): 
        return

    difference = (start_day + datetime.timedelta(day)) - _collectors['Data_1o_Esporos'].iloc[collector_index]

    if difference.days < 0:
        early_detection += 1
        # test_log.write(f"{start_day + datetime.timedelta(day)} < {_collectors['Data_1o_Esporos'].iloc[collector_index]}\n")
        # test_log.write(f"EARLY: -{_collectors['Data_1o_Esporos'].iloc[collector_index] - (start_day + datetime.timedelta(day))} days\n\n")
    elif difference.days > 0:
        late_detection += 1
        # test_log.write(f"{start_day + datetime.timedelta(day)} > {_collectors['Data_1o_Esporos'].iloc[collector_index]}\n")
        # test_log.write(f"LATE: +{start_day + datetime.timedelta(day) - _collectors['Data_1o_Esporos'].iloc[collector_index]} days\n\n")
    else:
        spot_on_detection += 1
        # test_log.write(f"OK {start_day + datetime.timedelta(day)} = {_collectors['Data_1o_Esporos'].iloc[collector_index]}\n\n")
        
def check_miss():
    
    for collector_index in range(len(_collectors)):

        if _collectors['color'].iloc[collector_index] == 'blue':

            if collector_index not in first_apperances.index:

                _collectors.loc[collector_index, 'color'] = 'black'
                miss_log.write(f"MISS:\n")

                collector_point = Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index])

                closest_infection_circle = infection_circles[0]

                for infection_circle in infection_circles:

                    if collector_point.distance(infection_circle.circle) < collector_point.distance(closest_infection_circle.circle):
                        closest_infection_circle = infection_circle

                miss_log.write(f"Distance: {collector_point.distance(closest_infection_circle.circle)* 111.12} km\n")
                
                for column in _collectors.columns[:_collectors.columns.get_loc('Data') + 1]:
                    miss_log.write(f"{column}: {_collectors[column].iloc[collector_index]}\n")
                miss_log.write("\n\n")
                missed_collectors.append(collector_index)

def growth(number_of_days):

    global infection_circles
    
    infection_circles = []

    for i in range(len(first_apperances)): # For each starting point

        infection_circle = Point(first_apperances['Longitude'].iloc[i], first_apperances['Latitude'].iloc[i]).buffer(BUFFER_FACTOR) # Create a new infection circle
        infection_circles.append(Infection_Circle(i, infection_circle, 1))

    for day in range(number_of_days): # For each day

        for _infection_circle in infection_circles:

            for collector_index in range(len(_collectors)):

                current_color = _collectors['color'].iloc[collector_index]

                if current_color == 'lightgreen' or current_color == 'white' or current_color == 'yellow': # Prevent re-infection and collectors that don't have spores
                    # lightgreen: detected
                    # white: no spores
                    # yellow: first collector(s)
                    continue
                else: 

                    if _infection_circle.circle.contains(
                        Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index])
                        ):

                        _collectors.loc[collector_index, 'color'] = 'lightgreen'

                        if collector_index not in first_apperances.index and collector_index not in detected_collectors:

                            detected_collectors.append(collector_index)

                        check_day(day, collector_index)

                        new_buffer = 1
                        new_infection_circle = Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index]).buffer(BUFFER_FACTOR * new_buffer)
                        infection_circles.append(Infection_Circle(collector_index, new_infection_circle, new_buffer))

        for _infection_circle in infection_circles: # For each day passed, the infection circle grows

            _infection_circle.buffer += 1
            _infection_circle.circle = Point(_infection_circle.circle.centroid.x, _infection_circle.circle.centroid.y).buffer(BUFFER_FACTOR * _infection_circle.buffer)

        # intersection_union()

        if day == number_of_days - 1: plotting(day)

def plotting(day):

    if day == 0 or day == NUMBER_OF_DAYS - 1:
        # Map plot
        _map.plot(color='lightgrey', edgecolor='whitesmoke')
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        # Title and labels definitions
        
        plt.xlabel('Longitude', fontsize=15)
        plt.ylabel('Latitude', fontsize=15)
        
        for i in range(len(_collectors)):
            if _collectors.loc[i, 'Situacao'] == 'Com esporos': # Show only cities with collectors with spores
                plt.gca().annotate(_collectors['Municipio'][i], (_collectors['Longitude'][i], _collectors['Latitude'][i]), fontsize=7)

    plt.title(f"Ferrugem asiática no Paraná - dia {(start_day + datetime.timedelta(day)).strftime('%Y-%m-%d')} ({day})", fontsize=20)

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

def count_collectors_until_day():
    collectors_until_day = 0
    for i in range(len(_collectors)):
        if start_day + datetime.timedelta(NUMBER_OF_DAYS) >= _collectors['Data_1o_Esporos'].iloc[i]:
            if i not in first_apperances.index:
                collectors_until_day += 1
    
    return collectors_until_day

_map, _collectors = read_basic_info()

start_day = _collectors['Data_1o_Esporos'].iloc[0]

NUMBER_OF_DAYS = 200
BUFFER_FACTOR = 0.02
miss_log = open(f'miss_log_{BUFFER_FACTOR}.txt', 'w+')
test_log = open(f'test_log_{BUFFER_FACTOR}.txt', 'w+')
early_detection = 0
late_detection = 0
spot_on_detection = 0
old_circles = []
detected_collectors = []
missed_collectors = []

coloring() 

growth(NUMBER_OF_DAYS)

collectors_until_day = count_collectors_until_day()

check_miss()

test_log.write(f"Detected collectors: {len(detected_collectors)} ({len(detected_collectors) / collectors_until_day * 100}%)\n")
test_log.write(f"--> Early detection: {early_detection} ({early_detection / len(detected_collectors) * 100}%)\n")
test_log.write(f"--> Late detection: {late_detection} ({late_detection / len(detected_collectors) * 100}%)\n")
test_log.write(f"--> Spot on detection: {spot_on_detection} ({spot_on_detection / len(detected_collectors) * 100}%)\n")
test_log.write(f"Missed collectors: {len(missed_collectors)} ({len(missed_collectors) / collectors_until_day * 100}%)\n")
plt.savefig(f"Day_{NUMBER_OF_DAYS}_{BUFFER_FACTOR}.png", dpi=200, bbox_inches='tight')

print(f"Detected: {len(detected_collectors)}\nMissed: {len(missed_collectors)}\nSum: {len(detected_collectors) + len(missed_collectors)}\nTotal: {collectors_until_day}")

miss_log.close()
test_log.close()