import pandas as pd
import geopandas as gpd
import math 
from shapely.geometry import Point
from infection_circle import Infection_Circle
import coletores, cria_buffers, plots

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

def circular_growth_touch(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, old_geometries: list, number_of_starting_points: int, TEST_PARAMS: dict) -> int:

    global true_positive_total_error

    _collectors.sort_values(by=['DiasAposInicioCiclo'], inplace=True)

    true_positive_total_error = 0

    infection_circles = []

    positive_collectors = _collectors.query('DiasAposInicioCiclo != -1')

    first_k_appearances = positive_collectors[0:number_of_starting_points]

    start_day = positive_collectors['DiasAposInicioCiclo'].iloc[0]

    count = 0

    plot_days = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 137]

    for day in range(TEST_PARAMS['number_of_days']):

        while True:

            if count < len(first_k_appearances):

                current_collector_index = first_k_appearances.index[count]

                if _collectors.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= _collectors.loc[current_collector_index,'DiasAposInicioCiclo']:

                        infection_circle = Infection_Circle(
                            Point(_collectors.loc[current_collector_index, 'LongitudeDecimal'], _collectors.loc[current_collector_index, 'LatitudeDecimal']),
                            1,
                            start_day + day
                        )

                        _collectors.loc[current_collector_index, 'Detected'] = 1
                        _collectors.loc[current_collector_index, 'circle_created'] = 1
                        _collectors.loc[current_collector_index, 'color'] = 'green'
                        _collectors.loc[current_collector_index, 'discovery_day'] = start_day + day

                        infection_circles.append(infection_circle)

                        count += 1

                        if len(infection_circles) == len(_collectors):
                            break
                        if count == len(_collectors):
                            break
                    else:
                        break
                else:
                    count += 1
            else:
                break
            
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

                        check_day(_collectors, collector, start_day + day)

                        if _collectors.loc[collector.Index, 'circle_created'] == 0:

                            new_infection_circle = Infection_Circle(
                                Point(collector.LongitudeDecimal, collector.LatitudeDecimal),
                                1, 
                                start_day + day
                            )

                            infection_circles.append(new_infection_circle)

                            _collectors.loc[collector.Index, 'circle_created'] = 1

                        else:

                            print("?!?!?!?!?!?!?")
        
        for infection_circle in infection_circles:
            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if day + 1 in plot_days:
            plots.plot_def_circles(_map, _collectors, infection_circles, start_day, day)

    true_positive_total_error = 0 if true_positives == 0 else math.sqrt(true_positive_total_error/true_positives)

    return true_positive_total_error, infection_circles, 'Circular Growth touch'

def circular_growth_no_touch(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, old_geometries: list, TEST_PARAMS: dict):

    days_column = 'DiasAposInicioCiclo' if 'DiasAposInicioCiclo' in _collectors.columns else 'MediaDiasAposInicioCiclo'

    global true_positive_total_error, true_positives

    _collectors.sort_values(by=[days_column], inplace=True)

    true_positive_total_error = 0
    true_positives = 0
    positive_collectors = _collectors.query(f'{days_column} != -1')
    first_appearances = positive_collectors[positive_collectors[days_column] == positive_collectors[days_column].min()]
    infection_circles = []
    start_day = positive_collectors[days_column].iloc[0]

    plot_days = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 137]

    for i in range(len(first_appearances)):

        infection_circle = Infection_Circle(
            Point(first_appearances['LongitudeDecimal'].iloc[i], first_appearances['LatitudeDecimal'].iloc[i]),
            1,
            start_day
        )

        _collectors.loc[first_appearances.index[i], 'Detected'] = 1
        _collectors.loc[first_appearances.index[i], 'circle_created'] = 1
        _collectors.loc[first_appearances.index[i], 'color'] = 'green'
        _collectors.loc[first_appearances.index[i], 'discovery_day'] = start_day

        infection_circles.append(infection_circle)

    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        # Loop for activating new infection circles as the days passes
        while True:

            if count < len(positive_collectors):

                # index of the last collector that had a infection circle created because it is sorted by the number of days after the start of the cycle
                current_collector_index = positive_collectors.index[count]

                if _collectors.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= _collectors.loc[current_collector_index, days_column]:

                        infection_circle = Infection_Circle(
                            Point(_collectors.loc[current_collector_index, 'LongitudeDecimal'], _collectors.loc[current_collector_index, 'LatitudeDecimal']),
                            1,
                            start_day + day
                        )

                        _collectors.loc[current_collector_index, 'Detected'] = 1
                        _collectors.loc[current_collector_index, 'circle_created'] = 1
                        _collectors.loc[current_collector_index, 'color'] = 'green'
                        _collectors.loc[current_collector_index, 'discovery_day'] = start_day + day

                        infection_circles.append(infection_circle)

                        count += 1

                        if len(infection_circles) == len(_collectors):
                            break
                        if count == len(_collectors):
                            break
                    else:
                        break
                else:
                    count += 1
            else:
                break

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

                        check_day(_collectors, collector, start_day + day)
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if day + 1 in plot_days:
            plots.plot_def_circles(_map, _collectors, infection_circles, start_day, day)

    true_positive_total_error = 0 if true_positives == 0 else math.sqrt(true_positive_total_error/true_positives)
    
    return true_positive_total_error, infection_circles, 'Circular Growth no touch'

def mix_growth(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, old_geometries: list, TEST_PARAMS: dict):

    days_column = 'DiasAposInicioCiclo' if 'DiasAposInicioCiclo' in _collectors.columns else 'MediaDiasAposInicioCiclo'

    global true_positive_total_error, true_positives

    _collectors.sort_values(by=[days_column], inplace=True)

    true_positive_total_error = 0

    true_positives = 0

    positive_collectors = _collectors.query(f'{days_column} != -1')

    first_appearances = positive_collectors[positive_collectors[days_column] == positive_collectors[days_column].min()]

    infection_circles = []

    start_day = positive_collectors[days_column].iloc[0]

    plot_days = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 137]

    for i in range(len(first_appearances)):

        infection_circle = Infection_Circle(
            Point(first_appearances['LongitudeDecimal'].iloc[i], first_appearances['LatitudeDecimal'].iloc[i]),
            1,
            start_day
        )

        _collectors.loc[first_appearances.index[i], 'Detected'] = 1
        _collectors.loc[first_appearances.index[i], 'circle_created'] = 1
        _collectors.loc[first_appearances.index[i], 'color'] = 'green'
        _collectors.loc[first_appearances.index[i], 'discovery_day'] = start_day

        infection_circles.append(infection_circle)

    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        # Loop for activating new infection circles as the days passes
        while True:
            
            if count < len(positive_collectors):

                current_collector_index = positive_collectors.index[count]

                if _collectors.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= _collectors.loc[current_collector_index, days_column]:

                        infection_circle = Infection_Circle(
                            Point(_collectors.loc[current_collector_index, 'LongitudeDecimal'], _collectors.loc[current_collector_index, 'LatitudeDecimal']),
                            1,
                            start_day + day
                        )

                        _collectors.loc[current_collector_index, 'Detected'] = 1
                        _collectors.loc[current_collector_index, 'circle_created'] = 1
                        _collectors.loc[current_collector_index, 'color'] = 'green'
                        _collectors.loc[current_collector_index, 'discovery_day'] = start_day + day

                        infection_circles.append(infection_circle)

                        count += 1

                        if len(infection_circles) == len(_collectors):
                            break
                        if count == len(_collectors):
                            break
                    else:
                        break
                else:
                    count += 1
            else:
                break

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

                        check_day(_collectors, collector, start_day + day)

                        if _collectors.loc[collector.Index, 'circle_created'] == 0:

                            new_infection_circle = Infection_Circle(
                                Point(collector.LongitudeDecimal, collector.LatitudeDecimal),
                                1, 
                                start_day + day
                            )

                            infection_circles.append(new_infection_circle)

                            _collectors.loc[collector.Index, 'circle_created'] = 1

                        else:
                            print("??????")
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if day + 1 in plot_days:
            plots.plot_def_circles(_map, _collectors, infection_circles, start_day, day)

    true_positive_total_error = 0 if true_positives == 0 else math.sqrt(true_positive_total_error/true_positives)

    return true_positive_total_error, infection_circles, 'Mixed Growth'

def topology_growth_no_touch(_map, _collectors_instance: coletores.Coletores, TEST_PARAMS: dict):

    days_column = 'DiasAposInicioCiclo' if 'DiasAposInicioCiclo' in _collectors_instance.geo_df.columns else 'MediaDiasAposInicioCiclo'

    global true_positive_total_error, true_positives

    _collectors_instance.geo_df.sort_values(by=[days_column], inplace=True)
    true_positive_total_error = 0
    true_positives = 0
    positive_collectors = _collectors_instance.geo_df.query(f'{days_column} != -1')
    first_appearances = positive_collectors[positive_collectors[days_column] == positive_collectors[days_column].min()]
    current_day_growth_topologies = dict()
    start_day = positive_collectors[days_column].iloc[0]
    proportionSeg = TEST_PARAMS['proportionSeg']
    proportionLarg = TEST_PARAMS['proportionLarg']
    
    growth_topology_dict = _collectors_instance.topologiaCrescimentoDict

    plot_days = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 137]
    
    for i in range(len(first_appearances)):

        growth_topology = growth_topology_dict[first_appearances.index[i]]

        current_day_growth_topologies[first_appearances.index[i]] = growth_topology

        _collectors_instance.geo_df.loc[first_appearances.index[i], 'Detected'] = 1
        _collectors_instance.geo_df.loc[first_appearances.index[i], 'circle_created'] = 1
        _collectors_instance.geo_df.loc[first_appearances.index[i], 'color'] = 'green'
        _collectors_instance.geo_df.loc[first_appearances.index[i], 'discovery_day'] = start_day
        _collectors_instance.geo_df.loc[first_appearances.index[i], 'life_time'] = 1


    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        while True:

            if count < len(positive_collectors):

                current_collector_index = positive_collectors.index[count]

                if _collectors_instance.geo_df.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= _collectors_instance.geo_df.loc[current_collector_index, days_column]:

                        growth_topology = growth_topology_dict[current_collector_index]

                        current_day_growth_topologies[current_collector_index] = growth_topology

                        _collectors_instance.geo_df.loc[current_collector_index, 'Detected'] = 1
                        _collectors_instance.geo_df.loc[current_collector_index, 'circle_created'] = 1
                        _collectors_instance.geo_df.loc[current_collector_index, 'color'] = 'green'
                        _collectors_instance.geo_df.loc[current_collector_index, 'discovery_day'] = start_day + day
                        _collectors_instance.geo_df.loc[current_collector_index, 'life_time'] = 1

                        count += 1

                        if len(current_day_growth_topologies) == len(_collectors_instance.geo_df):
                            break
                        if count == len(_collectors_instance.geo_df):
                            break
                    else:
                        break
                else:
                    count += 1
            else:
                break

        # All topologies
        pairs = current_day_growth_topologies.items()
        # All burrs
        burrs = []
        appended_indexes = []

        for pair in pairs:

            key = pair[0]
            growth_topology = pair[1]
            life_time = _collectors_instance.geo_df.loc[key, 'life_time']
            life_time += 1

            if len(growth_topology.getSegments()) == 0:
                continue

            burr = cria_buffers.criaCarrapicho(growth_topology, 0.1, False, 0)
            burrs.append(burr)
            appended_indexes.append(key)
        
        # burrs = gpd.GeoSeries(burrs, index=current_day_growth_topologies.keys())
        burrs = gpd.GeoSeries(burrs, index=appended_indexes)

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

            key = index

            life_time = _collectors_instance.geo_df.loc[key, 'life_time']

            growth_topology.growTopology(proportionSeg, proportionLarg)

            _collectors_instance.geo_df.loc[key, 'life_time'] += 1

        if day + 1 in plot_days:
            plots.plot_def_topologies(_map, _collectors_instance.geo_df, current_day_growth_topologies.values(), burrs, start_day, day)

    true_positive_total_error = 0 if true_positives == 0 else math.sqrt(true_positive_total_error/true_positives)

    return true_positive_total_error, current_day_growth_topologies, 'Topology Growth no touch'