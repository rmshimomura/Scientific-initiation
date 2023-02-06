import pandas as pd
import geopandas as gpd
import datetime, plots, math
from shapely.geometry import Point
from infection_circle import Infection_Circle
import growth_functions as gf

difference_values = []
total_error = 0
invalid_collectors = 0

def check_day(collector: pd.DataFrame, current_day: int) -> None:

    global total_error, difference_values, invalid_collectors

    if pd.isnull(collector.Data_1o_Esporos): # False positive

        collector.discovery_day = current_day
        
        return

    else: # True positive
        difference = abs((current_day - collector.Data_1o_Esporos).days)

        difference_values.append(difference)

        total_error += difference**2


def circular_growth(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, first_apperances: pd.DataFrame, old_circles: list, TEST_PARAMS: dict) -> int:

    infection_circles = []

    start_day = _collectors['Data_1o_Esporos'].iloc[0]

    for i in range(len(first_apperances)):

        infection_circle = Infection_Circle(
            Point(first_apperances['Longitude'].iloc[i], first_apperances['Latitude'].iloc[i]),
            1,
            start_day
        )

        infection_circles.append(infection_circle)

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

                            check_day(collector, start_day + datetime.timedelta(day))

                            new_infection_circle = Infection_Circle(
                                Point(collector.Longitude, collector.Latitude),
                                1, 
                                start_day + datetime.timedelta(day)
                            )

                            infection_circles.append(new_infection_circle)
        
        for infection_circle in infection_circles:
            infection_circle.grow(gf.logarithmic_growth_distance)

        if day == TEST_PARAMS['number_of_days'] - 1:
            plots.plotting(_map, _collectors, infection_circles, old_circles, start_day, day)
        
    return total_error, infection_circles, invalid_collectors