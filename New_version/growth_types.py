import pandas as pd
import geopandas as gpd
import datetime, plots, math
from shapely.geometry import Point
from infection_circle import Infection_Circle

difference_values = []
total_error = 0
invalid_collectors = 0

def check_day(_collectors: pd.DataFrame, current_day: int, collector: pd.DataFrame, TEST_PARAMS: dict) -> None:

    global total_error, difference_values, invalid_collectors

    if pd.isnull(collector.Data_1o_Esporos):
        # total_error += TEST_PARAMS['collector_penalty']**2

        closest_collectors = []

        for i in _collectors.itertuples():
            if not pd.isnull(i.Data_1o_Esporos):
                closest_collectors.append(i)

        closest_collectors.sort(key=lambda x: Point(x.Longitude, x.Latitude).distance(Point(collector.Longitude, collector.Latitude)))

        closest_collectors = closest_collectors[0]

        print(f"Closest: {Point(closest_collectors.Longitude, closest_collectors.Latitude).distance(Point(collector.Longitude, collector.Latitude)) * 111.045}km")
        print(f"Days difference: {(current_day - closest_collectors.Data_1o_Esporos).days} days\n")
        print(f"Penalty applied: {math.abs((current_day - closest_collectors.Data_1o_Esporos).days)}")
        # If the days are positive, put the number of days needed to reach the specific collector?
        invalid_collectors += 1
        return

    differece = (current_day - collector.Data_1o_Esporos).days

    difference_values.append(differece)

    total_error += differece**2

    if current_day == TEST_PARAMS['end_day']:
        difference_log = open(f'G:/My Drive/IC/Codes/Logs/difference_log_{TEST_PARAMS["number_of_days"]}_{TEST_PARAMS["buffer_factor"]}.txt', 'w')

        for value in difference_values:
            difference_log.write(f'Difference: {value} days\n')

        difference_log.write(f'\nMean: {sum(difference_values)/len(difference_values)}, Standard deviation: {math.sqrt(sum(difference_values)/len(difference_values))}')

        difference_log.close()


def circular_growth(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, first_apperances: pd.DataFrame, old_circles: list, TEST_PARAMS: dict) -> int:

    infection_circles = []

    start_day = _collectors['Data_1o_Esporos'].iloc[0]

    for i in range(len(first_apperances)):
        infection_circle = Point(first_apperances['Longitude'].iloc[i], first_apperances['Latitude'].iloc[i])
        infection_circle.buffer(TEST_PARAMS['buffer_factor'])
        infection_circles.append(Infection_Circle(infection_circle, 1))

    for day in range(TEST_PARAMS['number_of_days']):

        if len(infection_circles) < len(_collectors):
            
            for infection_circle in infection_circles:

                for collector in _collectors.itertuples():

                    if collector.Detected == 0:

                        if infection_circle.circle.contains(Point(collector.Longitude, collector.Latitude)):

                            _collectors.loc[collector.Index, 'Detected'] = 1

                            if collector.Situacao == 'Com esporos':

                                _collectors.loc[collector.Index, 'color'] = 'green'

                            else:

                                _collectors.loc[collector.Index, 'color'] = 'red'

                            check_day(_collectors, start_day + datetime.timedelta(day), collector, TEST_PARAMS)

                            new_infection_circle = Point(collector.Longitude, collector.Latitude)
                            new_infection_circle.buffer(TEST_PARAMS['buffer_factor'])
                            infection_circles.append(Infection_Circle(new_infection_circle, 1))
        
        for infection_circle in infection_circles:
            infection_circle.grow(TEST_PARAMS['buffer_factor'], day)

        if day == TEST_PARAMS['number_of_days'] - 1:
            plots.plotting(_map, _collectors, infection_circles, old_circles, start_day, day)
        
    return total_error, infection_circles, invalid_collectors