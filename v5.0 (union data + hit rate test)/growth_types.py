import pandas as pd
import geopandas as gpd
import datetime, plots, math 
from shapely.geometry import Point
from infection_circle import Infection_Circle
import coletores, cria_buffers

true_positive_total_error = 0
true_positives = 0

def check_day(_collectors: pd.DataFrame, collector: pd.DataFrame, current_day: int) -> None:

    global true_positive_total_error, true_positives

    if pd.isnull(collector.discovery_day):

        _collectors.loc[collector.Index, 'discovery_day'] = current_day

    if collector.Situacao == "Com esporos": # False positive
        
        return

    else: # True positive
        difference = abs(current_day - collector.MediaDiasAposInicioCiclo)

        true_positive_total_error += difference**2

        true_positives += 1

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

    global true_positive_total_error, true_positives

    true_positive_total_error = 0

    true_positives = 0

    positive_collectors = _collectors.query('MediaDiasAposInicioCiclo != -1')

    first_appearances = positive_collectors[positive_collectors['MediaDiasAposInicioCiclo'] == positive_collectors['MediaDiasAposInicioCiclo'].min()]

    infection_circles = []

    start_day = positive_collectors['MediaDiasAposInicioCiclo'].iloc[0]

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

                if start_day + day >= _collectors['MediaDiasAposInicioCiclo'].iloc[current_collector_index]:

                    infection_circle = Infection_Circle(
                        Point(_collectors['LongitudeDecimal'].iloc[current_collector_index], _collectors['LatitudeDecimal'].iloc[current_collector_index]),
                        1,
                        start_day + day
                    )

                    _collectors.loc[_collectors.index[current_collector_index], 'Detected'] = 1

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

                        check_day(_collectors, collector, start_day + day)
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        if TEST_PARAMS['animation']: plots.plotting(_map, _collectors, infection_circles, old_geometries, start_day, day, None, None)

    true_positive_total_error = math.sqrt(true_positive_total_error/true_positives)

    # plots.save_fig_on_day(_map, _collectors, infection_circles, old_geometries, start_day, TEST_PARAMS['number_of_days'], None)

    return true_positive_total_error, infection_circles, 'Circular Growth no touch'

def test_CGNT(_map, trained_collectors: pd.DataFrame, test_collectors: pd.DataFrame, TEST_PARAMS: dict):

    global true_positive_total_error, true_positives

    true_positive_total_error = 0

    true_positives = 0

    positive_collectors = trained_collectors.query('MediaDiasAposInicioCiclo != -1')

    first_appearances = positive_collectors[positive_collectors['MediaDiasAposInicioCiclo'] == positive_collectors['MediaDiasAposInicioCiclo'].min()]

    infection_circles = []

    start_day = positive_collectors['MediaDiasAposInicioCiclo'].iloc[0]

    # North, East, South, West
    regions_days_error = [[],[],[],[]]

    true_positive = 0

    false_positive = 0

    for k in range(len(first_appearances)):

        infection_circle = Infection_Circle(
            Point(first_appearances['LongitudeDecimal'].iloc[k], first_appearances['LatitudeDecimal'].iloc[k]),
            1,
            start_day
        )

        trained_collector = trained_collectors.loc[first_appearances.index[k]]

        test_collector = test_collectors.query('id == ' + str(trained_collector.id))

        test_collectors.loc[test_collector.index[0], 'Detected'] = 1

        test_collector = test_collectors.loc[test_collector.index[0]]

        if test_collector['DiasAposInicioCiclo'] == -1:

            false_positive += 1

        else:

            true_positive += 1

            for j in range(len(TEST_PARAMS['regions'])):

                if Point(test_collector.LongitudeDecimal, test_collector.LatitudeDecimal).within(TEST_PARAMS['regions'][j]):

                    regions_days_error[j].append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

        trained_collectors.loc[first_appearances.index[k], 'Detected'] = 1
        trained_collectors.loc[first_appearances.index[k], 'color'] = 'green'
        trained_collectors.loc[first_appearances.index[k], 'discovery_day'] = start_day

        infection_circles.append(infection_circle)

    # index of the last collector that had a infection circle created
    current_collector_index = first_appearances.index[-1]

    for day in range(TEST_PARAMS['number_of_days']):

        # Loop for activating new infection circles as the days passes
        while True:
            
            if current_collector_index < len(trained_collectors):

                if trained_collectors.loc[current_collector_index, 'Detected'] == 0:

                    if start_day + day >= trained_collectors.loc[current_collector_index, 'MediaDiasAposInicioCiclo']:

                        # Time to create a new infection circle                    
                        infection_circle = Infection_Circle(
                            Point(trained_collectors['LongitudeDecimal'].iloc[current_collector_index], trained_collectors['LatitudeDecimal'].iloc[current_collector_index]),
                            1,
                            start_day + day
                        )
                        
                        # Locate the collector in the trained_collectors dataframe
                        trained_collector = trained_collectors.loc[trained_collectors.index[current_collector_index]]

                        # Locate the collector in the test_collectors dataframe using the id
                        test_collector = test_collectors.query('id == ' + str(trained_collector.id))
                        test_collector = test_collectors.loc[test_collector.index[0]]

                        # Check if the collector was detected
                        if test_collector['Detected'] == 0:

                            if test_collector['DiasAposInicioCiclo'] == -1:
                                test_collectors.loc[test_collector.id, 'color'] = 'red'
                                false_positive += 1

                            else:

                                test_collectors.loc[test_collector.id, 'color'] = 'green'

                                true_positive += 1

                                for k in range(len(TEST_PARAMS['regions'])):

                                    if Point(test_collector.LongitudeDecimal, test_collector.LatitudeDecimal).within(TEST_PARAMS['regions'][k]):

                                        regions_days_error[k].append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

                            test_collectors.loc[test_collector.id, 'Detected'] = 1
                            
                        trained_collectors.loc[current_collector_index, 'Detected'] = 1

                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error')
                            exit()

                        infection_circles.append(infection_circle)

                        current_collector_index += 1

                        if len(infection_circles) == len(trained_collectors):
                            break
                        if current_collector_index == len(trained_collectors):
                            break
                    else:
                        break
                else:
                    # If the collector was already detected, just skip it
                    current_collector_index += 1
            else:
                break

        for infection_circle in infection_circles:

            for collector in test_collectors.itertuples():

                if collector.Detected == 0:

                    if infection_circle.circle.contains(Point(collector.LongitudeDecimal, collector.LatitudeDecimal)):

                        test_collectors.loc[collector.Index, 'Detected'] = 1

                        trained_collector = trained_collectors.query('id == ' + str(collector.id))

                        trained_collector = trained_collector.loc[trained_collector.index[0]]

                        if trained_collector.id != test_collectors.loc[collector.Index, 'id']:

                            print('False')

                        if collector.Situacao == 'Com esporos':

                            test_collectors.loc[collector.Index, 'color'] = 'green'
                            true_positive += 1

                            for k in range(len(TEST_PARAMS['regions'])):

                                if Point(test_collector.LongitudeDecimal, test_collector.LatitudeDecimal).within(TEST_PARAMS['regions'][k]):

                                    regions_days_error[k].append(test_collector['DiasAposInicioCiclo'] - (start_day + day))

                        else:

                            test_collectors.loc[collector.Index, 'color'] = 'red'
                            false_positive += 1

                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error, hit + miss != len(test_collectors.query(\'Detected == 1\'))')
                            exit()

                        # check_day(test_collectors, collector, start_day + day)
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

    # All the collectors that were not detected but had spores, change their color to yellow
    for collector in test_collectors.itertuples():
            
            if collector.Detected == 0:
    
                if collector.Situacao == 'Com esporos':
    
                    test_collectors.loc[collector.Index, 'color'] = 'yellow'
                    test_collectors.loc[collector.Index, 'format_shape'] = '*'

    # plots.save_fig_on_day(_map, test_collectors, infection_circles, [], start_day, TEST_PARAMS['number_of_days'], None, None, TEST_PARAMS)

    return true_positive, false_positive, regions_days_error


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