import pandas as pd
from infection_circle import Infection_Circle
from shapely.geometry import Point
import coletores, cria_buffers, plots
import geopandas as gpd

def learning_based_CGNT_MG(_map, trained_collectors: pd.DataFrame, test_collectors: pd.DataFrame, TEST_PARAMS: dict, mode):

    trained_collectors.sort_values(by=['MediaDiasAposInicioCiclo'], inplace=True)
    positive_collectors = trained_collectors.query('MediaDiasAposInicioCiclo != -1')
    first_appearances = positive_collectors[positive_collectors['MediaDiasAposInicioCiclo'] == positive_collectors['MediaDiasAposInicioCiclo'].min()]
    infection_circles = []
    start_day = positive_collectors['MediaDiasAposInicioCiclo'].iloc[0]
    # plot_days = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 137]
    plot_days = [137]
    days_error = []

    true_positive = 0
    false_positive = 0

    for k in range(len(first_appearances)):

        infection_circle = Infection_Circle(
            Point(first_appearances['LongitudeDecimal'].iloc[k], first_appearances['LatitudeDecimal'].iloc[k]),
            1,
            start_day
        )


        trained_collector = trained_collectors.loc[first_appearances.iloc[k].name]

        test_collector = test_collectors.loc[trained_collector.name]

        test_collectors.loc[test_collector.name, 'Detected'] = 1
        test_collectors.loc[test_collector.name, 'discovery_day'] = start_day

        test_collector = test_collectors.loc[test_collector.name]

        if test_collector['DiasAposInicioCiclo'] == -1:

            false_positive += 1

        else:

            true_positive += 1

            days_error.append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

        trained_collectors.loc[first_appearances.iloc[k].name, 'Detected'] = 1
        trained_collectors.loc[first_appearances.iloc[k].name, 'circle_created'] = 1
        trained_collectors.loc[first_appearances.iloc[k].name, 'color'] = 'green'
        trained_collectors.loc[first_appearances.iloc[k].name, 'discovery_day'] = start_day

        infection_circles.append(infection_circle)

    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        while True:
            
            if count < len(positive_collectors):

                current_collector_index = positive_collectors.iloc[count].name

                if trained_collectors.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= trained_collectors.loc[current_collector_index, 'MediaDiasAposInicioCiclo']:

                        # Time to create a new infection circle                    
                        infection_circle = Infection_Circle(
                            Point(trained_collectors.loc[current_collector_index, 'LongitudeDecimal'], trained_collectors.loc[current_collector_index,'LatitudeDecimal']),
                            1,
                            start_day + day
                        )
                        
                        # Locate the collector in the trained_collectors dataframe
                        trained_collector = trained_collectors.loc[current_collector_index]

                        # Locate the collector in the test_collectors dataframe using the id
                        test_collector = test_collectors.loc[trained_collector.name]

                        # Check if the collector was detected
                        if test_collector['Detected'] == 0:

                            if test_collector['DiasAposInicioCiclo'] == -1:

                                test_collectors.loc[test_collector.name, 'color'] = 'red'
                                test_collectors.loc[test_collector.name, 'discovery_day'] = start_day + day
                                false_positive += 1

                            else:

                                test_collectors.loc[test_collector.name, 'color'] = 'green'
                                test_collectors.loc[test_collector.name, 'discovery_day'] = start_day + day

                                true_positive += 1

                                days_error.append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

                            test_collectors.loc[test_collector.name, 'Detected'] = 1
                            
                        trained_collectors.loc[current_collector_index, 'Detected'] = 1
                        trained_collectors.loc[current_collector_index, 'circle_created'] = 1
                        trained_collectors.loc[current_collector_index, 'color'] = 'green'
                        trained_collectors.loc[current_collector_index, 'discovery_day'] = start_day + day

                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error')
                            exit()

                        infection_circles.append(infection_circle)

                        count += 1

                        if len(infection_circles) == len(trained_collectors):
                            break
                        if count == len(trained_collectors):
                            break
                    else:
                        break
                else:
                    # If the collector was already detected, just skip it
                    count += 1
            else:
                break

        for infection_circle in infection_circles:

            for collector in test_collectors.itertuples():

                if collector.Detected == 0:

                    if infection_circle.circle.contains(Point(collector.LongitudeDecimal, collector.LatitudeDecimal)):

                        test_collectors.loc[collector.Index, 'Detected'] = 1

                        trained_collector = trained_collectors.loc[collector.Index]

                        if trained_collector.name == collector.Index:
                            pass
                        else:
                            print('Error')
                            print(trained_collector.name, collector.Index)
                            exit()

                        if collector.Situacao == 'Com esporos': # True positive

                            test_collectors.loc[collector.Index, 'color'] = 'green'
                            test_collectors.loc[collector.Index, 'discovery_day'] = start_day + day
                            true_positive += 1

                            days_error.append(test_collectors.loc[collector.Index, 'DiasAposInicioCiclo'] - (start_day + day))

                        else: # False positive

                            test_collectors.loc[collector.Index, 'color'] = 'red'
                            test_collectors.loc[collector.Index, 'discovery_day'] = start_day + day
                            false_positive += 1

                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error, hit + miss != len(test_collectors.query(\'Detected == 1\'))')
                            exit()

                        if mode == 'Touch':
                            new_infection_circle = Infection_Circle(
                                Point(collector.LongitudeDecimal, collector.LatitudeDecimal),
                                1, 
                                start_day + day
                            )

                            trained_collectors.loc[collector.Index, 'Detected'] = 1


                            infection_circles.append(new_infection_circle)
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        # if day + 1 in plot_days:
        #     plots.plot_def_circles(_map, test_collectors, infection_circles, start_day, day)

    # All the collectors that were not detected but had spores, change their color to yellow
    for collector in test_collectors.itertuples():
            
            if collector.Detected == 0:
    
                if collector.Situacao == 'Com esporos':
    
                    test_collectors.loc[collector.Index, 'color'] = 'yellow'
                    test_collectors.loc[collector.Index, 'format_shape'] = '*'

    # plots.save_fig_on_day(_map, test_collectors, infection_circles, [], start_day, TEST_PARAMS['number_of_days'], None, None, TEST_PARAMS)

    return true_positive, false_positive, days_error

def normal_testing_CGT(_map, base_collectors: pd.DataFrame, test_collectors: pd.DataFrame, TEST_PARAMS: dict, number_of_starting_points=4):

    base_collectors.sort_values(by=['DiasAposInicioCiclo'], inplace=True)
    positive_collectors = base_collectors.query('DiasAposInicioCiclo != -1')
    first_k_appearances = positive_collectors[0:number_of_starting_points]
    infection_circles = []
    start_day = positive_collectors['DiasAposInicioCiclo'].iloc[0]

    # plot_days = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 137]
    plot_days = [137]
    days_error = []
    true_positive = 0
    false_positive = 0

    count = 0

    for day in range(TEST_PARAMS['number_of_days']):

        # Create the k first infection circles on the correct day
        while True:

            if count < len(first_k_appearances):

                current_collector_index = first_k_appearances.iloc[count].name

                if base_collectors.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= base_collectors.loc[current_collector_index, 'DiasAposInicioCiclo']:

                        infection_circle = Infection_Circle(
                            Point(base_collectors.loc[current_collector_index, 'LongitudeDecimal'], base_collectors.loc[current_collector_index,'LatitudeDecimal']),
                            1,
                            start_day + day
                        )

                        base_collector = base_collectors.loc[current_collector_index]

                        test_collector = test_collectors.loc[base_collector.name]

                        if test_collector['Detected'] == 0:

                            if test_collector['DiasAposInicioCiclo'] == -1:
                                test_collectors.loc[test_collector.name, 'color'] = 'red'
                                test_collectors.loc[test_collector.name, 'discovery_day'] = start_day + day
                                false_positive += 1
                            else:
                                test_collectors.loc[test_collector.name, 'color'] = 'green'
                                test_collectors.loc[test_collector.name, 'discovery_day'] = start_day + day

                                true_positive += 1

                                days_error.append(test_collector['DiasAposInicioCiclo'] - base_collector['DiasAposInicioCiclo'])

                            test_collectors.loc[test_collector.name, 'Detected'] = 1
                        
                        base_collectors.loc[current_collector_index, 'Detected'] = 1

                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error')
                            exit()

                        infection_circles.append(infection_circle)
                        
                        count += 1

                        if count == len(first_k_appearances) or len(infection_circles) == len(base_collectors):
                            break
                    else:
                        break
                else:
                    count += 1
            else:
                break

        for infection_circle in infection_circles:

            for collector in test_collectors.itertuples():

                if collector.Detected == 0:

                    if infection_circle.circle.contains(Point(collector.LongitudeDecimal, collector.LatitudeDecimal)):

                        test_collectors.loc[collector.Index, 'Detected'] = 1

                        base_collector = base_collectors.loc[collector.Index]


                        if base_collector.name == collector.Index:
                            pass
                        else:
                            print('Error')
                            print(base_collector.name, collector.Index)
                            exit()
                        
                        if collector.Situacao == 'Com esporos': # True positive

                            test_collectors.loc[collector.Index, 'color'] = 'green'
                            test_collectors.loc[collector.Index, 'discovery_day'] = start_day + day
                            true_positive += 1
                            days_error.append(base_collectors.loc[collector.Index, 'DiasAposInicioCiclo'] - (start_day + day))
                        else:
                            test_collectors.loc[collector.Index, 'color'] = 'red'
                            test_collectors.loc[collector.Index, 'discovery_day'] = start_day + day
                            false_positive += 1
                        
                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error, hit + miss != len(test_collectors.query(\'Detected == 1\'))')
                            exit()

                        new_infection_circle = Infection_Circle(
                            Point(collector.LongitudeDecimal, collector.LatitudeDecimal),
                            1, 
                            start_day + day
                        )

                        base_collectors.loc[collector.Index, 'Detected'] = 1

                        infection_circles.append(new_infection_circle)
        
        for infection_circle in infection_circles:
                
                infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

        # if day + 1 in plot_days:
        #     plots.plot_def_circles(_map, test_collectors, infection_circles, start_day, day)

    # All the collectors that were not detected but had spores, change their color to yellow
    for collector in test_collectors.itertuples():
                
        if collector.Detected == 0:

            if collector.Situacao == 'Com esporos':

                test_collectors.loc[collector.Index, 'color'] = 'yellow'
                test_collectors.loc[collector.Index, 'format_shape'] = '*'
                
    return true_positive, false_positive, days_error

def topology_test_TG(_map, trained_collectors: coletores.Coletores, test_collectors: pd.DataFrame, TEST_PARAMS: dict):

    trained_collectors.geo_df.sort_values(by=['MediaDiasAposInicioCiclo'], inplace=True)
    positive_collectors = trained_collectors.geo_df.query('MediaDiasAposInicioCiclo != -1')
    first_appearances = positive_collectors[positive_collectors['MediaDiasAposInicioCiclo'] == positive_collectors['MediaDiasAposInicioCiclo'].min()]
    start_day = positive_collectors['MediaDiasAposInicioCiclo'].iloc[0]
    current_day_growth_topologies = dict()
    growth_topology_dict = trained_collectors.topologiaCrescimentoDict
    days_error = []

    last_result = []
    # plot_days = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 137]
    plot_days = [137]

    proportionSeg = TEST_PARAMS['proportionSeg']
    proportionLarg = TEST_PARAMS['proportionLarg']

    true_positive = 0
    false_positive = 0


    for k in range(len(first_appearances)):

        growth_topology = growth_topology_dict[first_appearances.index[k]]
            
        trained_collector = trained_collectors.geo_df.loc[first_appearances.index[k]]

        test_collector = test_collectors.loc[trained_collector.name]

        test_collectors.loc[test_collector.name, 'Detected'] = 1
        test_collectors.loc[test_collector.name, 'discovery_day'] = start_day

        test_collector = test_collectors.loc[test_collector.name]

        if test_collector['DiasAposInicioCiclo'] == -1:

            false_positive += 1

        else:

            true_positive += 1

            days_error.append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

        trained_collectors.geo_df.loc[first_appearances.iloc[k].name, 'Detected'] = 1
        trained_collectors.geo_df.loc[first_appearances.iloc[k].name, 'circle_created'] = 1
        trained_collectors.geo_df.loc[first_appearances.iloc[k].name, 'color'] = 'green'
        trained_collectors.geo_df.loc[first_appearances.iloc[k].name, 'discovery_day'] = start_day
        trained_collectors.geo_df.loc[first_appearances.iloc[k].name, 'life_time'] = 1

        current_day_growth_topologies[first_appearances.iloc[k].name] = growth_topology
    
    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        while True: 

            if count < len(positive_collectors):

                current_collector_index = positive_collectors.iloc[count].name

                if trained_collectors.geo_df.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= trained_collectors.geo_df.loc[current_collector_index, 'MediaDiasAposInicioCiclo']:

                        growth_topology = growth_topology_dict[current_collector_index]

                        current_day_growth_topologies[current_collector_index] = growth_topology
                        
                        trained_collector = trained_collectors.geo_df.loc[current_collector_index]

                        test_collector = test_collectors.loc[trained_collector.name]

                        if test_collector['Detected'] == 0:

                            if test_collector['DiasAposInicioCiclo'] == -1:

                                test_collectors.loc[test_collector.name, 'color'] = 'red'
                                test_collectors.loc[test_collector.name, 'discovery_day'] = start_day + day
                                false_positive += 1

                            else:

                                test_collectors.loc[test_collector.name, 'color'] = 'green'
                                test_collectors.loc[test_collector.name, 'discovery_day'] = start_day + day

                                true_positive += 1

                                days_error.append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

                            test_collectors.loc[test_collector.name, 'Detected'] = 1
                            
                        trained_collectors.geo_df.loc[current_collector_index, 'Detected'] = 1
                        trained_collectors.geo_df.loc[current_collector_index, 'circle_created'] = 1
                        trained_collectors.geo_df.loc[current_collector_index, 'color'] = 'green'
                        trained_collectors.geo_df.loc[current_collector_index, 'discovery_day'] = start_day + day
                        trained_collectors.geo_df.loc[current_collector_index, 'life_time'] = 1

                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error')
                            exit()

                        count += 1

                        if len(current_day_growth_topologies) == len(trained_collectors.geo_df):
                            break
                        if count == len(trained_collectors.geo_df):
                            break
                    else:
                        break
                else:
                    count += 1
            else:
                break

        pairs = current_day_growth_topologies.items()
        # All burrs
        burrs = []
        appended_indexes = []

        for pair in pairs:

            key = pair[0]
            growth_topology = pair[1]
            life_time = trained_collectors.geo_df.loc[key, 'life_time']
            life_time += 1

            if len(growth_topology.getSegments()) == 0:
                continue

            burr = cria_buffers.criaCarrapicho(growth_topology, 0.1, False, 0)
            burrs.append(burr)
            appended_indexes.append(key)
        
        burrs = gpd.GeoSeries(burrs, index=appended_indexes)
        
        for burr in burrs:

            for collector in test_collectors.itertuples():

                if collector.Detected == 0:

                    collector_point = Point(collector.LongitudeDecimal, collector.LatitudeDecimal)

                    if collector_point.within(burr):

                        test_collectors.loc[collector.Index, 'Detected'] = 1

                        trained_collector = trained_collectors.geo_df.loc[collector.Index]

                        if trained_collector.name == collector.Index:
                            pass
                        else:
                            print('Error')
                            print(trained_collector.name, collector.Index)
                            exit()

                        if collector.Situacao == 'Com esporos':

                            test_collectors.loc[collector.Index, 'color'] = 'green'
                            test_collectors.loc[collector.Index, 'discovery_day'] = start_day + day
                            true_positive += 1

                            days_error.append(test_collectors.loc[collector.Index, 'DiasAposInicioCiclo'] - (start_day + day))
                        else:
                            test_collectors.loc[collector.Index, 'color'] = 'red'
                            test_collectors.loc[collector.Index, 'discovery_day'] = start_day + day
                            false_positive += 1

                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error, hit + miss != len(test_collectors.query(\'Detected == 1\'))')
                            exit()

        for index, growth_topology in current_day_growth_topologies.items():

            key = index

            growth_topology.growTopology(proportionSeg, proportionLarg)

            trained_collectors.geo_df.loc[key, 'life_time'] += 1
        
        # if day + 1 in plot_days:
            # plots.plot_def_topologies(_map, test_collectors, current_day_growth_topologies.values(), burrs, start_day, day)

        # If it is the last day, assign a copy of burrs to last_result
        if day == TEST_PARAMS['number_of_days'] - 1:
            last_result = burrs.copy()

    # All the collectors that were not detected but had spores, change their color to yellow
    for collector in test_collectors.itertuples():

        if collector.Detected == 0:

            if collector.Situacao == 'Com esporos':

                test_collectors.loc[collector.Index, 'color'] = 'yellow'
                test_collectors.loc[collector.Index, 'format_shape'] = '*'

    return true_positive, false_positive, days_error, last_result

