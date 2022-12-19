import pandas as pd
import geopandas as gpd
import datetime
from shapely.geometry import Point
from infection_circle import Infection_Circle
import plots

def check_day(current_day: int, collector: pd.DataFrame) -> None:

    global total_error
    total_error = 0

    # Check if the collector.Data_1o_Esporos is not null
    if pd.isnull(collector.Data_1o_Esporos):
        # print(f"Collector penality!")
        return

    differece = (current_day - collector.Data_1o_Esporos).days

    total_error += differece**2


def circular_growth(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, first_apperances: pd.DataFrame, old_circles: list, TEST_PARAMS: dict) -> int:

    infection_circles = []

    start_day = _collectors['Data_1o_Esporos'].iloc[0]

    for i in range(len(first_apperances)):
        infection_circle = Point(first_apperances['Longitude'].iloc[i], first_apperances['Latitude'].iloc[i])
        infection_circle.buffer(TEST_PARAMS['buffer_factor'])
        infection_circles.append(Infection_Circle(infection_circle, 1))

    for day in range(TEST_PARAMS['number_of_days']):

        for infection_circle in infection_circles:

            for collector in _collectors.itertuples():

                if collector.Detected == 0:

                    if infection_circle.circle.contains(Point(collector.Longitude, collector.Latitude)):

                        _collectors.loc[collector.Index, 'Detected'] = 1

                        if collector.Situacao == 'Com esporos':

                            _collectors.loc[collector.Index, 'color'] = 'green'

                        else:

                            _collectors.loc[collector.Index, 'color'] = 'red'

                        check_day(start_day + datetime.timedelta(day), collector)

                        new_infection_circle = Point(collector.Longitude, collector.Latitude)
                        new_infection_circle.buffer(TEST_PARAMS['buffer_factor'])
                        infection_circles.append(Infection_Circle(new_infection_circle, 1))
        
        for infection_circle in infection_circles:
            infection_circle.grow(TEST_PARAMS['buffer_factor'])
        
        if len(infection_circles) == len(_collectors):
            break

        plots.plotting(_map, _collectors, infection_circles, old_circles, start_day, day)
        
    return total_error, infection_circles