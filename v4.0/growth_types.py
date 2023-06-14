import pandas as pd
import geopandas as gpd
import datetime, plots, math 
from shapely.geometry import Point, LineString
from infection_circle import Infection_Circle
from burr import Burr
import fake_buffers
import utils
import coletores, cria_buffers

difference_values = []
true_positive_total_error = 0
true_positives = 0
fake_collectors_buffers_list = []
RAI = 0.08

def check_day(_collectors: pd.DataFrame, collector: pd.DataFrame, current_day: int) -> None:

    global true_positive_total_error, difference_values, true_positives

    if pd.isnull(collector.discovery_day):

        _collectors.loc[collector.Index, 'discovery_day'] = current_day

    if pd.isnull(collector.Primeiro_Esporo): # False positive
        
        return

    else: # True positive
        difference = abs((current_day - collector.Primeiro_Esporo).days)

        difference_values.append(difference)

        true_positive_total_error += difference**2

        true_positives += 1

def add_fake_buffer(fake_buffer: fake_buffers.Fake_Buffer, collector_id: int):

    global fake_collectors_buffers_list

    if len(fake_collectors_buffers_list) > 0:

        for fake_buffers_list in fake_collectors_buffers_list:

            if fake_buffers_list.collector_id == collector_id:

                fake_buffers_list.buffer_list.append(fake_buffer)

                return

    new_fake_buffers_list = fake_buffers.Fake_Buffer_List(collector_id)

    new_fake_buffers_list.buffer_list.append(fake_buffer)

    fake_collectors_buffers_list.append(new_fake_buffers_list)

def circular_growth_touch(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, old_geometries: list, TEST_PARAMS: dict) -> int:

    infection_circles = []

    positive_collectors = _collectors.query('DiasAposInicioCiclo != -1')

    first_appearances = positive_collectors[positive_collectors['DiasAposInicioCiclo'] == positive_collectors['DiasAposInicioCiclo'].min()]

    start_day = positive_collectors['Primeiro_Esporo'].iloc[0]

    for i in range(len(first_appearances)):

        infection_circle = Infection_Circle(
            Point(first_appearances['LongitudeDecimal'].iloc[i], first_appearances['LatitudeDecimal'].iloc[i]),
            1,
            start_day
        )

        infection_circles.append(infection_circle)

    for day in range(TEST_PARAMS['number_of_days']):

        # The following for is for like, if the current day is the first day of the collector's infection, 
        # check if there is already a infection circle for that collector, if not, create one.

        if start_day + datetime.timedelta(day) <= first_appearances['Primeiro_Esporo'].iloc[i]:

            for i in range(len(first_appearances)):

                # If the current day is the first day of the collector's infection
                if start_day + datetime.timedelta(day) == first_appearances['Primeiro_Esporo'].iloc[i]:

                    check = False

                    for circle in infection_circles:

                        centroid = (circle.circle.centroid.x, circle.circle.centroid.y)

                        # If a infection circle for the collector already exists
                        if centroid == (first_appearances['LongitudeDecimal'].iloc[i], first_appearances['LatitudeDecimal'].iloc[i]):
                            # Don't create a new infection circle
                            check = True
                            break

                    if check: continue

                    # Else create a new infection circle
                    infection_circle = Infection_Circle(
                        Point(first_appearances['LongitudeDecimal'].iloc[i], first_appearances['LatitudeDecimal'].iloc[i]),
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

        if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, infection_circles, old_geometries, start_day, day, None, None)

    global true_positive_total_error

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    # plots.save_fig_on_day(_map, _collectors, infection_circles, old_geometries, start_day, TEST_PARAMS['number_of_days'], None)

    return true_positive_total_error, infection_circles, 'Circular Growth touch'

def circular_growth_no_touch(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, old_geometries: list, TEST_PARAMS: dict):

    positive_collectors = _collectors.query('DiasAposInicioCiclo != -1')

    first_appearances = positive_collectors[positive_collectors['DiasAposInicioCiclo'] == positive_collectors['DiasAposInicioCiclo'].min()]

    infection_circles = []

    start_day = positive_collectors['Primeiro_Esporo'].iloc[0]

    for i in range(len(first_appearances)):

        infection_circle = Infection_Circle(
            Point(first_appearances['LongitudeDecimal'].iloc[i], first_appearances['LatitudeDecimal'].iloc[i]),
            1,
            start_day
        )

        _collectors.loc[first_appearances.index[i], 'Detected'] = 1
        _collectors.loc[first_appearances.index[i], 'color'] = 'green'
        _collectors.loc[first_appearances.index[i], 'discovery_day'] = start_day

        infection_circles.append(infection_circle)

    # index of the last collector that had a infection circle created
    current_collector_index = first_appearances.index[-1]

    for day in range(TEST_PARAMS['number_of_days']):

        # Loop for activating new infection circles as the days passes
        while True:
            
            if current_collector_index < len(_collectors):

                if start_day + datetime.timedelta(day) == _collectors['Primeiro_Esporo'].iloc[current_collector_index]:

                    infection_circle = Infection_Circle(
                        Point(_collectors['LongitudeDecimal'].iloc[current_collector_index], _collectors['LatitudeDecimal'].iloc[current_collector_index]),
                        1,
                        start_day + datetime.timedelta(day)
                    )

                    infection_circles.append(infection_circle)

                    current_collector_index += 1
                    if len(infection_circles) == len(_collectors):
                        break
                    if current_collector_index == len(_collectors):
                        break
                else:
                    break
            else:
                break

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
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, infection_circles, old_geometries, start_day, day, None, None)

    global true_positive_total_error

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    # plots.save_fig_on_day(_map, _collectors, infection_circles, old_geometries, start_day, TEST_PARAMS['number_of_days'], None)

    return true_positive_total_error, infection_circles, 'Circular Growth no touch'

def burr_growth_touch(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, first_appearances: pd.DataFrame, old_geometries: list, burrs: gpd.GeoSeries, TEST_PARAMS: dict) -> int:

    global fake_collectors_buffers_list

    start_day = _collectors['Primeiro_Esporo'].iloc[0]

    burrs_list = []

    # Start first burrs
    for i in range(len(first_appearances)):

        burrs_list.append(
        Burr(
            burrs[first_appearances['burr'].iloc[i]],
            0.0001,
            start_day
        ))

    for day in range(TEST_PARAMS['number_of_days']):
        
        day_original_len = len(burrs_list)

        # The following for is for like, if the current day is the first day of the collector's infection, 
        # check if there is already a burr growing for that collector, if not, create one.
        if start_day + datetime.timedelta(day) <= first_appearances['Primeiro_Esporo'].iloc[i]:
            for i in range(len(first_appearances)):

                # If the current day is the first day of the collector's infection
                if start_day + datetime.timedelta(day) == first_appearances['Primeiro_Esporo'].iloc[i]:

                    check = False

                    for burr in burrs_list:
                        
                        # If a burr for the collector already exists
                        if burr.geometry == burrs[first_appearances['burr'].iloc[i]]:
                            check = True
                            break

                    if check: continue

                    # Else create a new burr
                    burr = Burr(
                        burrs[first_appearances['burr'].iloc[i]],
                        0.0001,
                        start_day
                    )
                    
                    burrs_list.append(burr)

        if len(burrs_list) < len(_collectors):

            for burr in burrs_list: # For each burr, check if it contains a collector

                if burrs_list.index(burr) >= day_original_len: break

                for collector in _collectors.itertuples(): # For each collector, check if it is inside the burr

                    if collector.Detected == False: # If the collector is not detected
                        
                        collector_point = Point(collector.LongitudeDecimal, collector.LatitudeDecimal)

                        if collector.Fake == False:

                            if burr.geometry.contains(collector_point): # If the collector is inside the burr

                                _collectors.loc[collector.Index, 'Detected'] = 1

                                if collector.Situacao == 'Com esporos':

                                    _collectors.loc[collector.Index, 'color'] = 'green'

                                else:

                                    _collectors.loc[collector.Index, 'color'] = 'red'

                                check_day(_collectors, collector, start_day + datetime.timedelta(day))

                                if collector.burr is None: continue 

                                new_burr = Burr(
                                    burrs[int(collector.burr)],
                                    0.0001,
                                    start_day + datetime.timedelta(day)
                                )

                                burrs_list.append(new_burr)
                        else: 

                            if burr.geometry.contains(collector_point): # If the fake collector is inside the burr    

                                _collectors.loc[collector.Index, 'Detected'] = 1

                                # Color is equal to black because it is a fake collector
                                _collectors.loc[collector.Index, 'color'] = 'black'

                                check_day(_collectors, collector, start_day + datetime.timedelta(day))

                                burr_centroid = Point(burr.geometry.centroid.x, burr.geometry.centroid.y)

                                line_string = LineString([collector_point, utils.treat_position(burr_centroid, collector_point, RAI)])

                                test_fake_buffer = fake_buffers.Fake_Buffer(line_string, 0.0001)

                                add_fake_buffer(test_fake_buffer, collector.Index)
                                
                    elif collector.Fake == True:

                        collector_point = Point(collector.LongitudeDecimal, collector.LatitudeDecimal)

                        if burr.geometry.contains(collector_point):

                            burr_centroid = Point(burr.geometry.centroid.x, burr.geometry.centroid.y)

                            line_string = LineString([collector_point, utils.treat_position(burr_centroid, collector_point, RAI)])

                            test_fake_buffer = fake_buffers.Fake_Buffer(line_string, 0.0001)

                            add_fake_buffer(test_fake_buffer, collector.Index)


        for burr in burrs_list:
            burr.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, None, old_geometries, start_day, day, burrs_list, fake_collectors_buffers_list)

    global true_positive_total_error

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    # plots.save_fig_on_day(_map, _collectors, None, None, start_day, TEST_PARAMS['number_of_days'], burrs_list, fake_collectors_buffers_list)

    return true_positive_total_error, burrs_list, 'Burr Growth', fake_collectors_buffers_list

def topology_growth_no_touch(_map: gpd.GeoDataFrame, collectors_instance: coletores.Coletores, old_geometries: list, TEST_PARAMS: dict, plt):

    start_day = collectors_instance.geo_df['Primeiro_Esporo'].iloc[0]

    # active_collectors = collectors_instance.geo_df[collectors_instance.geo_df['DiasAposInicioCiclo'] == collectors_instance.geo_df['DiasAposInicioCiclo'].min()]

    active_collectors = collectors_instance.geo_df[0:20]

    growth_topology_dict = collectors_instance.topologiaCrescimentoDict

    for day in range(TEST_PARAMS['number_of_days']):

        buffers_to_generate = []

        for i in range(len(active_collectors)):

            buffers_to_generate.append(growth_topology_dict[active_collectors.iloc[i].id])

        buffers = cria_buffers.geraBuffersCarrapichos(buffers_to_generate, 0.005, False)

        for _ in range(len(active_collectors)):

            center_point = active_collectors.iloc[_].geometry
            plt.scatter(center_point.x, center_point.y, color=active_collectors.iloc[_].color, s=10)
            plt.annotate(_, (center_point.x, center_point.y), fontsize=10)

        for i in range(len(active_collectors)):

            plt.plot(*buffers[i].exterior.xy, color='yellow', linewidth=1)

        break 

    # global true_positive_total_error

    # true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)