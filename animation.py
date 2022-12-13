import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import datetime
from infection_circle import Infection_Circle

def coloring():
    
    global first_apperances

    _collectors['color'] = _collectors['Situacao'].apply(lambda x: 'white' if x == 'Com esporos' else 'red') # Color collectors with spores in green and collectors without spores in red
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
        test_log.write(f"{start_day + datetime.timedelta(day)} < {_collectors['Data_1o_Esporos'].iloc[collector_index]}\n")
        test_log.write(f"EARLY: -{_collectors['Data_1o_Esporos'].iloc[collector_index] - (start_day + datetime.timedelta(day))} days\n\n")
    elif difference.days > 0:
        late_detection += 1
        test_log.write(f"{start_day + datetime.timedelta(day)} > {_collectors['Data_1o_Esporos'].iloc[collector_index]}\n")
        test_log.write(f"LATE: +{start_day + datetime.timedelta(day) - _collectors['Data_1o_Esporos'].iloc[collector_index]} days\n\n")
    else:
        spot_on_detection += 1
        test_log.write(f"OK {start_day + datetime.timedelta(day)} = {_collectors['Data_1o_Esporos'].iloc[collector_index]}\n\n")
        
def check_miss(day, collectors_until_day):
    
    for collector_index in range(len(_collectors)):

        if collector_index in detected_collectors or collector_index in missed_collectors:
            continue

        if start_day + datetime.timedelta(day) == _collectors['Data_1o_Esporos'].iloc[collector_index]:

            collectors_until_day += 1

            _collectors.loc[collector_index, 'color'] = 'black'
            miss_log.write(f"MISS: {start_day + datetime.timedelta(day)} didn't detected:\n")
            # Change the color of the collector missed to black
            
            for column in _collectors.columns[:_collectors.columns.get_loc('Data') + 1]:
                miss_log.write(f"{column}: {_collectors[column].iloc[collector_index]}\n")
            miss_log.write("\n\n")
            missed_collectors.append(collector_index)
    
    return collectors_until_day

def growth(number_of_days, collectors_until_day):

    global infection_circles
    
    infection_circles = []

    for i in range(len(first_apperances)): # For each starting point

        infection_circle = Point(first_apperances['Longitude'].iloc[i], first_apperances['Latitude'].iloc[i]).buffer(0.01) # Create a new infection circle
        infection_circles.append(Infection_Circle(i, infection_circle, 1))

    for day in range(number_of_days): # For each day

        collectors_until_day = check_miss(day, collectors_until_day)

        for _infection_circle in infection_circles:

            for collector_index in range(len(_collectors)):

                current_color = _collectors['color'].iloc[collector_index]

                if current_color == 'lightgreen' or current_color == 'red' or current_color == 'yellow': # Prevent re-infection and collectors that don't have spores
                    continue
                else: 

                    if _infection_circle.circle.contains(
                        Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index])
                        ):

                        _collectors.loc[collector_index, 'color'] = 'lightgreen'

                        if collector_index not in first_apperances.index:

                            detected_collectors.append(collector_index)

                        check_day(day, collector_index)
                        collectors_until_day += 1

                        new_buffer = 1
                        new_infection_circle = Point(_collectors['Longitude'].iloc[collector_index], _collectors['Latitude'].iloc[collector_index]).buffer(0.01 * new_buffer)
                        infection_circles.append(Infection_Circle(collector_index, new_infection_circle, new_buffer))

        for _infection_circle in infection_circles: # For each day passed, the infection circle grows

            _infection_circle.buffer += 1
            _infection_circle.circle = Point(_infection_circle.circle.centroid.x, _infection_circle.circle.centroid.y).buffer(0.01 * _infection_circle.buffer)

        # intersection_union()

        if day == number_of_days - 1: plotting(day)

    return collectors_until_day

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

_map = gpd.read_file('Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') # Read map file
_collectors = pd.read_csv('Data/Collectors/2021/ColetoresSafra2122.csv', sep=';', decimal=',', parse_dates=['Data_1o_Esporos'], infer_datetime_format=True) \
            .sort_values(by='Data_1o_Esporos') # Read collectors file

_collectors.index = range(0, len(_collectors)) # Reset index

for i in range(0, len(_collectors)):
    if not pd.isnull(_collectors["Data_1o_Esporos"].iloc[i]):
        _collectors.loc[i, 'Data_1o_Esporos'] = _collectors["Data_1o_Esporos"].iloc[i].strftime('%Y-%m-%d')

start_day = _collectors['Data_1o_Esporos'].iloc[0]

miss_log = open('miss_log.txt', 'w+')
test_log = open('test_log.txt', 'w+')
early_detection = 0
late_detection = 0
spot_on_detection = 0
old_circles = []
detected_collectors = []
missed_collectors = []
collectors_until_day = 0
NUMBER_OF_DAYS = 100


coloring() 

collectors_until_day = growth(NUMBER_OF_DAYS, collectors_until_day)

test_log.write(f"Detected collectors: {len(detected_collectors)} ({len(detected_collectors) / collectors_until_day * 100}%)\n")
test_log.write(f"--> Early detection: {early_detection} ({early_detection / len(detected_collectors) * 100}%)\n")
test_log.write(f"--> Late detection: {late_detection} ({late_detection / len(detected_collectors) * 100}%)\n")
test_log.write(f"--> Spot on detection: {spot_on_detection} ({spot_on_detection / len(detected_collectors) * 100}%)\n")
test_log.write(f"Missed collectors: {len(missed_collectors)} ({len(missed_collectors) / collectors_until_day * 100}%)\n")
plt.show()

print(detected_collectors)

miss_log.close()
test_log.close()