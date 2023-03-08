import pandas as pd
import geopandas as gpd
import datetime, plots, math, time 
from shapely.geometry import Point
from infection_circle import Infection_Circle
import growth_functions as gf

difference_values = []
true_positive_total_error = 0
true_positives = 0

def check_day(_collectors: pd.DataFrame, collector: pd.DataFrame, current_day: int) -> None:

    global true_positive_total_error, difference_values, true_positives

    if pd.isnull(collector.Primeiro_Esporo): # False positive

        if pd.isnull(collector.discovery_day):

            _collectors.loc[collector.Index, 'discovery_day'] = current_day
        
        return

    else: # True positive
        difference = abs((current_day - collector.Primeiro_Esporo).days)

        difference_values.append(difference)

        true_positive_total_error += difference**2

        true_positives += 1


def circular_growth(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, first_apperances: pd.DataFrame, old_circles: list, TEST_PARAMS: dict) -> int:

    infection_circles = []

    start_day = _collectors['Primeiro_Esporo'].iloc[0]

    for i in range(len(first_apperances)):

        infection_circle = Infection_Circle(
            Point(first_apperances['Longitude_Decimal'].iloc[i], first_apperances['Latitude_Decimal'].iloc[i]),
            1,
            start_day
        )

        infection_circles.append(infection_circle)

    for day in range(TEST_PARAMS['number_of_days']):

        for i in range(len(first_apperances)):

            if start_day + datetime.timedelta(day) == first_apperances['Primeiro_Esporo'].iloc[i]:
                check = False

                for circle in infection_circles:

                    centroid = (circle.circle.centroid.x, circle.circle.centroid.y)

                    if centroid == (first_apperances['Longitude_Decimal'].iloc[i], first_apperances['Latitude_Decimal'].iloc[i]):
                        check = True
                        break

                if check: continue

                infection_circle = Infection_Circle(
                    Point(first_apperances['Longitude_Decimal'].iloc[i], first_apperances['Latitude_Decimal'].iloc[i]),
                    1,
                    start_day
                )

                infection_circles.append(infection_circle)

        if len(infection_circles) < len(_collectors):
            
            for infection_circle in infection_circles:

                for collector in _collectors.itertuples():

                    if collector.Detected == 0:

                        if infection_circle.circle.contains(Point(collector.Longitude_Decimal, collector.Latitude_Decimal)):

                            _collectors.loc[collector.Index, 'Detected'] = 1

                            if collector.Situacao == 'Com esporos':

                                _collectors.loc[collector.Index, 'color'] = 'green'

                            else:

                                _collectors.loc[collector.Index, 'color'] = 'red'

                            check_day(_collectors, collector, start_day + datetime.timedelta(day))

                            new_infection_circle = Infection_Circle(
                                Point(collector.Longitude_Decimal, collector.Latitude_Decimal),
                                1, 
                                start_day + datetime.timedelta(day)
                            )

                            infection_circles.append(new_infection_circle)
        
        for infection_circle in infection_circles:
            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, infection_circles, old_circles, start_day, day)

    global true_positive_total_error

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    plots.save_fig_on_day(_map, _collectors, infection_circles, old_circles, start_day, TEST_PARAMS['number_of_days'])

    return true_positive_total_error, infection_circles