import pandas as pd
import geopandas as gpd
import math 
from shapely.geometry import Point
from infection_circle import Infection_Circle
import coletores, cria_buffers

true_positive_total_error = 0
true_positives = 0

def check_day(_collectors: pd.DataFrame, collector: pd.DataFrame, current_day: int) -> None:

    global true_positive_total_error, true_positives

    if collector.Situacao == "Encerrado sem esporos": # False positive
        
        return

    else: # True positive

        if 'MediaDiasAposInicioCiclo' in _collectors.columns:

            difference = abs(current_day - collector.MediaDiasAposInicioCiclo)

        else:

            difference = abs(current_day - collector.DiasAposInicioCiclo)

        true_positive_total_error += difference**2

        true_positives += 1

def start_first_appearances_circles(first_appearances, _collectors, start_day, infection_circles):

    for i in range(len(first_appearances)):

        x = first_appearances['LongitudeDecimal'].iloc[i]
        y = first_appearances['LatitudeDecimal'].iloc[i]
        index = first_appearances.index[i]

        activate_circle(_collectors, x, y, index, start_day, infection_circles)

def start_first_apperances_topologies(first_appearances, _collectors, start_day, growth_topology_dict, current_day_growth_topologies):
    
    for i in range(len(first_appearances)):

        activate_topology(_collectors, first_appearances.index[i], start_day, growth_topology_dict, current_day_growth_topologies)

def activate_topology(_collectors, index, current_day, growth_topology_dict, current_day_growth_topologies):

    growth_topology = growth_topology_dict[index]

    current_day_growth_topologies[index] = growth_topology

    _collectors.geo_df.loc[index, 'Detected'] = 1
    _collectors.geo_df.loc[index, 'circle_created'] = 1
    _collectors.geo_df.loc[index, 'color'] = 'green'
    _collectors.geo_df.loc[index, 'discovery_day'] = current_day
    _collectors.geo_df.loc[index, 'life_time'] = 1

def activate_new_topologies(_collectors_instance, positive_collectors, current_day, count, days_column, growth_topology_dict, current_day_growth_topologies):

    while True:

        if count < len(positive_collectors):

            current_collector_index = positive_collectors.index[count]

            if _collectors_instance.geo_df.loc[current_collector_index, 'circle_created'] == 0:

                if current_day >= _collectors_instance.geo_df.loc[current_collector_index, days_column]:

                    activate_topology(_collectors_instance, current_collector_index, current_day, growth_topology_dict, current_day_growth_topologies)

                    count += 1

                    if len(current_day_growth_topologies) == len(_collectors_instance.geo_df):
                        break

                else:
                    break
            else:
                count += 1
        else:
            break

def create_topology_buffers(_collectors_instance, current_day_growth_topologies):

    # All topologies
    pairs = current_day_growth_topologies.items()

    # All burrs
    burrs = []
    appended_indexes = []

    for pair in pairs:

        key = pair[0]
        growth_topology = pair[1]

        # Sometimes, the topology is empty, meaning that it probably didn't affected any nearby collectors (because of distance or time)
        if len(growth_topology.getSegments()) == 0:
            continue
    
        life_time = _collectors_instance.geo_df.loc[key, 'life_time']
        life_time += 1

        # Geometry around the topology
        burr = cria_buffers.criaCarrapicho(growth_topology, 0.1, False, 0)
        burrs.append(burr)
        appended_indexes.append(key)
    
    # burrs = gpd.GeoSeries(burrs, index=current_day_growth_topologies.keys())
    burrs = gpd.GeoSeries(burrs, index=appended_indexes)

    return burrs

def activate_circle(_collectors, x, y, index, current_day, list_of_circles):

    infection_circle = Infection_Circle(
        Point(x, y),
        1,
        current_day
    )

    _collectors.loc[index, 'Detected'] = 1
    _collectors.loc[index, 'circle_created'] = 1
    _collectors.loc[index, 'color'] = 'green'
    _collectors.loc[index, 'discovery_day'] = current_day

    list_of_circles.append(infection_circle)

def activate_new_circles(_collectors, positive_collectors, current_day, count, days_column, infection_circles, limit=0):

    if limit == 0:
        # CGNT and MG
        limit = len(positive_collectors)
    else:
        # CGT
        limit = limit

    while True:

        # Are there still collectors to be activated?
        if count < limit:

            # index of the next collector to be activated
            current_collector_index = positive_collectors.index[count]

            # Does the current collector already have a circle?
            if _collectors.loc[current_collector_index, 'circle_created'] == 0:

                # Is the current collector's day of appearance the current day?
                if current_day >= _collectors.loc[current_collector_index, days_column]:

                    x = _collectors.loc[current_collector_index, 'LongitudeDecimal']
                    y = _collectors.loc[current_collector_index, 'LatitudeDecimal']
                    index = current_collector_index

                    activate_circle(_collectors, x, y, index, current_day, infection_circles)

                    count += 1

                    # If all collectors have been activated, then we stop the loop
                    if len(infection_circles) == len(_collectors):
                        break
                else:
                    # If the current collector's day of appearance is not the current day, then no other collector will appear on the current day
                    break
            else:
                # If the current collector already has a circle, then we move on to the next collector
                count += 1
        else:
            # No, there are no more collectors to be activated
            break

def circular_growth_touch(_collectors: pd.DataFrame, number_of_starting_points: int, TEST_PARAMS: dict) -> int:

    global true_positive_total_error

    _collectors.sort_values(by=['DiasAposInicioCiclo'], inplace=True)

    true_positive_total_error = 0

    infection_circles = []

    positive_collectors = _collectors.query('DiasAposInicioCiclo != -1')

    first_k_appearances = positive_collectors[0:number_of_starting_points]

    start_day = positive_collectors['DiasAposInicioCiclo'].iloc[0]

    count = 0

    for day in range(TEST_PARAMS['number_of_days']):

        # Here we check if there are any new collectors to be activated, but only for the first k collectors.
        activate_new_circles(_collectors, first_k_appearances, start_day, day, count, 'DiasAposInicioCiclo', infection_circles, number_of_starting_points)
            
        for infection_circle in infection_circles:

            for collector in _collectors.itertuples():

                if collector.Detected == 0:

                    if infection_circle.circle.contains(Point(collector.LongitudeDecimal, collector.LatitudeDecimal)):

                        _collectors.loc[collector.Index, 'color'] = 'green' if collector.Situacao == 'Com esporos' else 'red'

                        check_day(_collectors, collector, start_day + day)

                        if _collectors.loc[collector.Index, 'circle_created'] == 0:

                            x = collector.LongitudeDecimal
                            y = collector.LatitudeDecimal
                            index = collector.Index
                            
                            activate_circle(_collectors, x, y, index, start_day + day, infection_circles)
        
        for infection_circle in infection_circles:
            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

    true_positive_total_error = 0 if true_positives == 0 else math.sqrt(true_positive_total_error/true_positives)

    return true_positive_total_error, 'Circular Growth touch'

def circular_growth_no_touch(_collectors: pd.DataFrame, TEST_PARAMS: dict):

    days_column = 'DiasAposInicioCiclo' if 'DiasAposInicioCiclo' in _collectors.columns else 'MediaDiasAposInicioCiclo'

    global true_positive_total_error, true_positives

    _collectors.sort_values(by=[days_column], inplace=True)

    true_positive_total_error = 0
    true_positives = 0
    positive_collectors = _collectors.query(f'{days_column} != -1')
    first_appearances = positive_collectors[positive_collectors[days_column] == positive_collectors[days_column].min()]
    infection_circles = []
    start_day = positive_collectors[days_column].iloc[0]

    start_first_appearances_circles(first_appearances, _collectors, start_day, infection_circles)

    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        # Check if there are any new collectors to be activated
        activate_new_circles(_collectors, positive_collectors, start_day + day, count, days_column, infection_circles)
        
        # Considering the current infection circles, check if any collector is inside any of them

        # For each infection circle, check if any of them contains new collectors
        for infection_circle in infection_circles:

            for collector in _collectors.itertuples():

                if collector.Detected == 0:

                    if infection_circle.circle.contains(Point(collector.LongitudeDecimal, collector.LatitudeDecimal)):

                        _collectors.loc[collector.Index, 'Detected'] = 1
                        _collectors.loc[collector.Index, 'discovery_day'] = start_day + day

                        if collector.Situacao == 'Com esporos':

                            _collectors.loc[collector.Index, 'color'] = 'green'

                        else:

                            _collectors.loc[collector.Index, 'color'] = 'red'

                        # Using the metrics, we can calculate the error
                        check_day(_collectors, collector, start_day + day)
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

    true_positive_total_error = 0 if true_positives == 0 else math.sqrt(true_positive_total_error/true_positives)
    
    return true_positive_total_error, 'Circular Growth no touch'

def mix_growth(_collectors: pd.DataFrame, TEST_PARAMS: dict):

    days_column = 'DiasAposInicioCiclo' if 'DiasAposInicioCiclo' in _collectors.columns else 'MediaDiasAposInicioCiclo'

    global true_positive_total_error, true_positives

    _collectors.sort_values(by=[days_column], inplace=True)

    true_positive_total_error = 0

    true_positives = 0

    positive_collectors = _collectors.query(f'{days_column} != -1')

    first_appearances = positive_collectors[positive_collectors[days_column] == positive_collectors[days_column].min()]

    infection_circles = []

    start_day = positive_collectors[days_column].iloc[0]

    start_first_appearances_circles(first_appearances, _collectors, start_day, infection_circles)

    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        # Check if there are any new collectors to be activated
        activate_new_circles(_collectors, positive_collectors, start_day, day, count, days_column, infection_circles)

        # Considering the current infection circles, check if any collector is inside any of them

        # For each infection circle, check if any of them contains new collectors
        for infection_circle in infection_circles:
            
            for collector in _collectors.itertuples():

                if collector.Detected == 0:

                    if infection_circle.circle.contains(Point(collector.LongitudeDecimal, collector.LatitudeDecimal)):

                        _collectors.loc[collector.Index, 'Detected'] = 1
                        _collectors.loc[collector.Index, 'discovery_day'] = start_day + day

                        if collector.Situacao == 'Com esporos':

                            _collectors.loc[collector.Index, 'color'] = 'green'

                        else:

                            _collectors.loc[collector.Index, 'color'] = 'red'

                        # Using the metrics, we can calculate the error
                        check_day(_collectors, collector, start_day + day)

                        # Here is the difference between this function and the circular_growth_no_touch function
                        # If the collector is inside the circle, then we create a new circle
                        # That's why this function is called mix_growth
                        if _collectors.loc[collector.Index, 'circle_created'] == 0:

                            x = collector.LongitudeDecimal
                            y = collector.LatitudeDecimal
                            index = collector.Index
                            
                            activate_circle(_collectors, x, y, index, start_day + day, infection_circles)
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

    true_positive_total_error = 0 if true_positives == 0 else math.sqrt(true_positive_total_error/true_positives)

    return true_positive_total_error, 'Mixed Growth'

def topology_growth_no_touch(_collectors_instance: coletores.Coletores, TEST_PARAMS: dict):

    days_column = 'DiasAposInicioCiclo' if 'DiasAposInicioCiclo' in _collectors_instance.geo_df.columns else 'MediaDiasAposInicioCiclo'

    global true_positive_total_error, true_positives

    _collectors_instance.geo_df.sort_values(by=[days_column], inplace=True)
    true_positive_total_error = 0
    true_positives = 0
    positive_collectors = _collectors_instance.geo_df.query(f'{days_column} != -1')
    first_appearances = positive_collectors[positive_collectors[days_column] == positive_collectors[days_column].min()]
    current_day_growth_topologies = dict()
    start_day = positive_collectors[days_column].iloc[0]
    
    growth_topology_dict = _collectors_instance.topologiaCrescimentoDict
    
    start_first_apperances_topologies(first_appearances, _collectors_instance, start_day, growth_topology_dict, current_day_growth_topologies)

    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        activate_new_topologies(_collectors_instance, positive_collectors, start_day + day, count, days_column, growth_topology_dict, current_day_growth_topologies)

        burrs = create_topology_buffers(_collectors_instance, current_day_growth_topologies)

        for burr in burrs:

            for collector in _collectors_instance.geo_df.itertuples():

                if collector.Detected == 0:

                    collector_point = Point(collector.LongitudeDecimal, collector.LatitudeDecimal)

                    if collector_point.within(burr):

                        _collectors_instance.geo_df.loc[collector.Index, 'Detected'] = 1
                        _collectors_instance.geo_df.loc[collector.Index, 'discovery_day'] = start_day + day

                        if collector.Situacao == 'Com esporos':

                            _collectors_instance.geo_df.loc[collector.Index, 'color'] = 'green'

                        else:

                            _collectors_instance.geo_df.loc[collector.Index, 'color'] = 'red'

                        check_day(_collectors_instance.geo_df, collector, start_day + day)

        for index, growth_topology in current_day_growth_topologies.items():

            growth_topology.growTopology(TEST_PARAMS['proportionSeg'], TEST_PARAMS['proportionLarg'])

            _collectors_instance.geo_df.loc[index, 'life_time'] += 1

    true_positive_total_error = 0 if true_positives == 0 else math.sqrt(true_positive_total_error/true_positives)

    return true_positive_total_error, 'Topology Growth no touch'