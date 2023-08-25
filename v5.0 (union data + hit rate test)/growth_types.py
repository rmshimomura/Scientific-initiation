import pandas as pd
import geopandas as gpd
import plots, math 
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

def circular_growth_touch(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, old_geometries: list, number_of_starting_points: int, TEST_PARAMS: dict) -> int:

    global true_positive_total_error

    _collectors.sort_values(by=['DiasAposInicioCiclo'], inplace=True)

    true_positive_total_error = 0

    infection_circles = []

    positive_collectors = _collectors.query('DiasAposInicioCiclo != -1')

    first_k_appearances = positive_collectors[0:number_of_starting_points]

    start_day = positive_collectors['DiasAposInicioCiclo'].iloc[0]

    count = 0

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

        # if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, infection_circles, old_geometries, start_day, day, None, None)

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    # plots.save_fig_on_day(_map, _collectors, infection_circles, old_geometries, start_day, TEST_PARAMS['number_of_days'], None)

    return true_positive_total_error, infection_circles, 'Circular Growth touch'

def circular_growth_no_touch(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, old_geometries: list, TEST_PARAMS: dict):

    global true_positive_total_error, true_positives

    _collectors.sort_values(by=['DiasAposInicioCiclo'], inplace=True)

    true_positive_total_error = 0
    true_positives = 0
    positive_collectors = _collectors.query('DiasAposInicioCiclo != -1')
    first_appearances = positive_collectors[positive_collectors['DiasAposInicioCiclo'] == positive_collectors['DiasAposInicioCiclo'].min()]
    infection_circles = []
    start_day = positive_collectors['DiasAposInicioCiclo'].iloc[0]

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

                    if start_day + day >= _collectors.loc[current_collector_index, 'DiasAposInicioCiclo']:

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

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)
    
    return true_positive_total_error, infection_circles, 'Circular Growth no touch'

def mix_growth(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, old_geometries: list, TEST_PARAMS: dict):

    global true_positive_total_error, true_positives

    _collectors.sort_values(by=['DiasAposInicioCiclo'], inplace=True)

    true_positive_total_error = 0

    true_positives = 0

    positive_collectors = _collectors.query('DiasAposInicioCiclo != -1')

    first_appearances = positive_collectors[positive_collectors['DiasAposInicioCiclo'] == positive_collectors['DiasAposInicioCiclo'].min()]

    infection_circles = []

    start_day = positive_collectors['DiasAposInicioCiclo'].iloc[0]

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
                            print("??????")
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, infection_circles, old_geometries, start_day, day, None, None)

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    return true_positive_total_error, infection_circles, 'Mixed Growth'

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