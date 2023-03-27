import pandas as pd
import geopandas as gpd
import datetime, plots, math, time 
from shapely.geometry import Point
from infection_circle import Infection_Circle
from burr import Burr

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


def circular_growth(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, first_apperances: pd.DataFrame, old_geometries: list, TEST_PARAMS: dict) -> int:

    infection_circles = []

    start_day = _collectors['Primeiro_Esporo'].iloc[0]

    for i in range(len(first_apperances)):

        infection_circle = Infection_Circle(
            Point(first_apperances['LongitudeDecimal'].iloc[i], first_apperances['LatitudeDecimal'].iloc[i]),
            1,
            start_day
        )

        infection_circles.append(infection_circle)

    for day in range(TEST_PARAMS['number_of_days']):

        for i in range(len(first_apperances)):

            # If the current day is the first day of the collector's infection
            if start_day + datetime.timedelta(day) == first_apperances['Primeiro_Esporo'].iloc[i]:

                check = False

                for circle in infection_circles:

                    centroid = (circle.circle.centroid.x, circle.circle.centroid.y)

                    # If a infection circle for the collector already exists
                    if centroid == (first_apperances['LongitudeDecimal'].iloc[i], first_apperances['LatitudeDecimal'].iloc[i]):
                        # Don't create a new infection circle
                        check = True
                        break

                if check: continue

                # Else create a new infection circle
                infection_circle = Infection_Circle(
                    Point(first_apperances['LongitudeDecimal'].iloc[i], first_apperances['LatitudeDecimal'].iloc[i]),
                    1,
                    start_day
                )

                infection_circles.append(infection_circle)

        if len(infection_circles) < len(_collectors):
            
            for infection_circle in infection_circles:

                for collector in _collectors.itertuples():

                    if collector.Detected == 0:

                        if infection_circle.circle.contains(Point(collector.LongitudeDecimal, collector.LatitudeDecimal)):

                            _collectors.loc[collector.Index, 'Detected'] = 1

                            if collector.Situacao == 'Com esporos':

                                _collectors.loc[collector.Index, 'color'] = 'green'

                            else:

                                _collectors.loc[collector.Index, 'color'] = 'red'

                            check_day(_collectors, collector, start_day + datetime.timedelta(day))

                            new_infection_circle = Infection_Circle(
                                Point(collector.LongitudeDecimal, collector.LatitudeDecimal),
                                1, 
                                start_day + datetime.timedelta(day)
                            )

                            infection_circles.append(new_infection_circle)
        
        for infection_circle in infection_circles:
            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, infection_circles, old_geometries, start_day, day, None)

    global true_positive_total_error

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    plots.save_fig_on_day(_map, _collectors, infection_circles, old_geometries, start_day, TEST_PARAMS['number_of_days'], None)

    return true_positive_total_error, infection_circles

def burr_growth(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, first_apperances: pd.DataFrame, old_geometries: list, burrs: gpd.GeoSeries, TEST_PARAMS: dict) -> int:

    start_day = _collectors['Primeiro_Esporo'].iloc[0]

    burrs_list = []

    for i in range(len(first_apperances)):

        burrs_list.append(
        Burr(
            burrs[first_apperances['burr'].iloc[i]],
            0.001,
            start_day
        ))

    for day in range(TEST_PARAMS['number_of_days']):
        
        day_original_len = len(burrs_list)

        for i in range(len(first_apperances)):

            # If the current day is the first day of the collector's infection
            if start_day + datetime.timedelta(day) == first_apperances['Primeiro_Esporo'].iloc[i]:

                check = False

                for burr in burrs_list:
                    
                    # If a burr for the collector already exists
                    if burr.geometry == burrs[first_apperances['burr'].iloc[i]]:
                        check = True
                        break

                if check: continue

                # Else create a new burr
                burr = Burr(
                    burrs[first_apperances['burr'].iloc[i]],
                    1,
                    start_day
                )
                
                burrs_list.append(burr)

        if len(burrs_list) < len(_collectors):

            for burr in burrs_list: # For each burr, check if it contains a collector

                if burrs_list.index(burr) >= day_original_len: break

                for collector in _collectors.itertuples(): # For each collector, check if it is inside the burr

                    if collector.Detected == 0: # If the collector is not detected

                        if burr.geometry.contains(Point(collector.LongitudeDecimal, collector.LatitudeDecimal)): # If the collector is inside the burr

                            _collectors.loc[collector.Index, 'Detected'] = 1

                            if collector.Situacao == 'Com esporos':

                                _collectors.loc[collector.Index, 'color'] = 'green'

                            else:

                                _collectors.loc[collector.Index, 'color'] = 'red'

                            check_day(_collectors, collector, start_day + datetime.timedelta(day))

                            if collector.burr is None: continue 

                            new_burr = Burr(
                                burrs[collector.burr],
                                0.001,
                                start_day + datetime.timedelta(day)
                            )

                            burrs_list.append(new_burr)

        for burr in burrs_list:
            burr.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, None, old_geometries, start_day, day, burrs_list)

    global true_positive_total_error

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    plots.save_fig_on_day(_map, _collectors, None, None, start_day, TEST_PARAMS['number_of_days'], burrs_list)

    return true_positive_total_error, burrs_list