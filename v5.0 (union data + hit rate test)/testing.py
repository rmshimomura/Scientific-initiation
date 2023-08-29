import pandas as pd
from infection_circle import Infection_Circle
from shapely.geometry import Point
import coletores, cria_buffers

def learning_based_CGNT_MG(trained_collectors: pd.DataFrame, test_collectors: pd.DataFrame, TEST_PARAMS: dict, mode):

    trained_collectors.sort_values(by=['MediaDiasAposInicioCiclo'], inplace=True)
    positive_collectors = trained_collectors.query('MediaDiasAposInicioCiclo != -1')
    first_appearances = positive_collectors[positive_collectors['MediaDiasAposInicioCiclo'] == positive_collectors['MediaDiasAposInicioCiclo'].min()]
    infection_circles = []
    start_day = positive_collectors['MediaDiasAposInicioCiclo'].iloc[0]

    days_error = []

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

            days_error.append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

        trained_collectors.loc[first_appearances.index[k], 'Detected'] = 1
        trained_collectors.loc[first_appearances.index[k], 'circle_created'] = 1
        trained_collectors.loc[first_appearances.index[k], 'color'] = 'green'
        trained_collectors.loc[first_appearances.index[k], 'discovery_day'] = start_day

        infection_circles.append(infection_circle)

    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        while True:
            
            if count < len(positive_collectors):

                current_collector_index = positive_collectors.index[count]

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
                        test_collector = test_collectors.loc[trained_collector.id]

                        # Check if the collector was detected
                        if test_collector['Detected'] == 0:

                            if test_collector['DiasAposInicioCiclo'] == -1:

                                test_collectors.loc[test_collector.id, 'color'] = 'red'
                                false_positive += 1

                            else:

                                test_collectors.loc[test_collector.id, 'color'] = 'green'

                                true_positive += 1

                                days_error.append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

                            test_collectors.loc[test_collector.id, 'Detected'] = 1
                            
                        trained_collectors.loc[current_collector_index, 'Detected'] = 1

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


                        trained_collector = trained_collectors.query('id == ' + str(collector.id))
                        trained_collector_index = trained_collector.index[0]
                        trained_collector = trained_collectors.loc[trained_collector_index]

                        if trained_collector.id == collector.id:
                            pass
                        else:
                            print('Error')
                            print(trained_collector.id, collector.id)
                            exit()

                        if collector.Situacao == 'Com esporos': # True positive

                            test_collectors.loc[collector.Index, 'color'] = 'green'
                            true_positive += 1

                            days_error.append(test_collector['DiasAposInicioCiclo'] - (start_day + day))

                        else: # False positive

                            test_collectors.loc[collector.Index, 'color'] = 'red'
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

                            trained_collectors.loc[trained_collector_index, 'Detected'] = 1


                            infection_circles.append(new_infection_circle)

                        if trained_collectors.loc[trained_collector_index,'id'] != trained_collector.id:
                            print('Error')
                            exit()
        
        for infection_circle in infection_circles:

            infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

    # All the collectors that were not detected but had spores, change their color to yellow
    for collector in test_collectors.itertuples():
            
            if collector.Detected == 0:
    
                if collector.Situacao == 'Com esporos':
    
                    test_collectors.loc[collector.Index, 'color'] = 'yellow'
                    test_collectors.loc[collector.Index, 'format_shape'] = '*'

    # plots.save_fig_on_day(_map, test_collectors, infection_circles, [], start_day, TEST_PARAMS['number_of_days'], None, None, TEST_PARAMS)

    return true_positive, false_positive, days_error

def normal_testing_CGT(base_collectors: pd.DataFrame, test_collectors: pd.DataFrame, TEST_PARAMS: dict, number_of_starting_points=4):

    base_collectors.sort_values(by=['DiasAposInicioCiclo'], inplace=True)
    positive_collectors = base_collectors.query('DiasAposInicioCiclo != -1')
    first_k_appearances = positive_collectors[0:number_of_starting_points]
    infection_circles = []
    start_day = positive_collectors['DiasAposInicioCiclo'].iloc[0]

    # North, East, South, West
    days_error = []
    true_positive = 0
    false_positive = 0

    count = 0

    for day in range(TEST_PARAMS['number_of_days']):

        # Create the k first infection circles on the correct day
        while True:

            if count < len(first_k_appearances):

                current_collector_index = first_k_appearances.index[count]

                if base_collectors.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= base_collectors.loc[current_collector_index, 'DiasAposInicioCiclo']:

                        infection_circle = Infection_Circle(
                            Point(base_collectors.loc[current_collector_index, 'LongitudeDecimal'], base_collectors.loc[current_collector_index,'LatitudeDecimal']),
                            1,
                            start_day + day
                        )

                        base_collector = base_collectors.loc[current_collector_index]

                        test_collector = test_collectors.loc[base_collector.id]

                        if test_collector['Detected'] == 0:

                            if test_collector['DiasAposInicioCiclo'] == -1:
                                test_collectors.loc[test_collector.id, 'color'] = 'red'    
                                false_positive += 1
                            else:
                                test_collectors.loc[test_collector.id, 'color'] = 'green'

                                true_positive += 1

                                days_error.append(test_collector['DiasAposInicioCiclo'] - base_collector['DiasAposInicioCiclo'])

                            test_collectors.loc[test_collector.id, 'Detected'] = 1
                        
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

                        base_collector = base_collectors.query('id == ' + str(collector.id))
                        base_collector_index = base_collector.index[0]
                        base_collector = base_collectors.loc[base_collector_index]

                        if base_collector.id == collector.id:
                            pass
                        else:
                            print('Error')
                            print(base_collector.id, collector.id)
                            exit()
                        
                        if collector.Situacao == 'Com esporos': # True positive

                            test_collectors.loc[collector.Index, 'color'] = 'green'
                            true_positive += 1
                            days_error.append(test_collector['DiasAposInicioCiclo'] - (start_day + day))
                        else:
                            test_collectors.loc[collector.Index, 'color'] = 'red'
                            false_positive += 1
                        
                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error, hit + miss != len(test_collectors.query(\'Detected == 1\'))')
                            exit()

                        new_infection_circle = Infection_Circle(
                            Point(collector.LongitudeDecimal, collector.LatitudeDecimal),
                            1, 
                            start_day + day
                        )

                        base_collectors.loc[base_collector_index, 'Detected'] = 1

                        infection_circles.append(new_infection_circle)

                        if base_collectors.loc[base_collector_index,'id'] != base_collector.id:
                            print('Error')
                            exit()
        
        for infection_circle in infection_circles:
                
                infection_circle.grow(TEST_PARAMS['growth_function_distance'], TEST_PARAMS['base'])

    # All the collectors that were not detected but had spores, change their color to yellow
    for collector in test_collectors.itertuples():
                
        if collector.Detected == 0:

            if collector.Situacao == 'Com esporos':

                test_collectors.loc[collector.Index, 'color'] = 'yellow'
                test_collectors.loc[collector.Index, 'format_shape'] = '*'
                
    return true_positive, false_positive, days_error

def topology_test_TG(trained_collectors: coletores.Coletores, test_collectors: pd.DataFrame, TEST_PARAMS: dict):

    trained_collectors.geo_df.sort_values(by=['MediaDiasAposInicioCiclo'], inplace=True)
    positive_collectors = trained_collectors.geo_df.query('MediaDiasAposInicioCiclo != -1')
    first_appearances = positive_collectors[positive_collectors['MediaDiasAposInicioCiclo'] == positive_collectors['MediaDiasAposInicioCiclo'].min()]
    start_day = positive_collectors['MediaDiasAposInicioCiclo'].iloc[0]
    burrs = dict()
    growth_topology_dict = trained_collectors.topologiaCrescimentoDict
    days_error = []
    buffer_production_function = cria_buffers.funcProduzCarrapichos(TEST_PARAMS['fator_producao_carrapichos'],False,0.00001)


    true_positive = 0
    false_positive = 0


    for k in range(len(first_appearances)):

        burr = growth_topology_dict[first_appearances.index[k]]
            
        trained_collector = trained_collectors.geo_df.loc[first_appearances.index[k]]

        test_collector = test_collectors.query('id == ' + str(trained_collector.id))

        test_collectors.loc[test_collector.index[0], 'Detected'] = 1

        test_collector = test_collectors.loc[test_collector.index[0]]

        if test_collector['DiasAposInicioCiclo'] == -1:

            false_positive += 1

        else:

            true_positive += 1

            days_error.append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

        trained_collectors.geo_df.loc[first_appearances.index[k], 'Detected'] = 1
        trained_collectors.geo_df.loc[first_appearances.index[k], 'circle_created'] = 1
        trained_collectors.geo_df.loc[first_appearances.index[k], 'color'] = 'green'
        trained_collectors.geo_df.loc[first_appearances.index[k], 'discovery_day'] = start_day
        trained_collectors.geo_df.loc[first_appearances.index[k], 'life_time'] = 1

        burrs[first_appearances.index[k]] = burr
    
    count = len(first_appearances)

    for day in range(TEST_PARAMS['number_of_days']):

        while True: 

            if count < len(positive_collectors):

                current_collector_index = positive_collectors.index[count]

                if trained_collectors.geo_df.loc[current_collector_index, 'circle_created'] == 0:

                    if start_day + day >= trained_collectors.geo_df.loc[current_collector_index, 'MediaDiasAposInicioCiclo']:

                        burr = growth_topology_dict[current_collector_index]
                        
                        trained_collector = trained_collectors.geo_df.loc[current_collector_index]

                        test_collector = test_collectors.loc[trained_collector.id]

                        if test_collector['Detected'] == 0:

                            if test_collector['DiasAposInicioCiclo'] == -1:

                                test_collectors.loc[test_collector.id, 'color'] = 'red'
                                false_positive += 1

                            else:

                                test_collectors.loc[test_collector.id, 'color'] = 'green'

                                true_positive += 1

                                days_error.append(test_collector['DiasAposInicioCiclo'] - trained_collector['MediaDiasAposInicioCiclo'])

                            test_collectors.loc[test_collector.id, 'Detected'] = 1
                            
                        trained_collectors.geo_df.loc[current_collector_index, 'Detected'] = 1
                        trained_collectors.geo_df.loc[current_collector_index, 'circle_created'] = 1
                        trained_collectors.geo_df.loc[current_collector_index, 'color'] = 'green'
                        trained_collectors.geo_df.loc[current_collector_index, 'discovery_day'] = start_day + day
                        trained_collectors.geo_df.loc[current_collector_index, 'life_time'] = 1


                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error')
                            exit()

                        burrs[current_collector_index] = burr

                        count += 1

                        if len(burrs) == len(trained_collectors.geo_df):
                            break
                        if count == len(trained_collectors.geo_df):
                            break
                    else:
                        break
                else:
                    count += 1
            else:
                break

        current_day_burrs = cria_buffers.criaBuffers(burrs,buffer_production_function)
        
        for burr in current_day_burrs:

            for collector in test_collectors.itertuples():

                if collector.Detected == 0:

                    collector_point = Point(collector.LongitudeDecimal, collector.LatitudeDecimal)

                    if collector_point.within(burr):

                        test_collectors.loc[collector.Index, 'Detected'] = 1

                        trained_collector = trained_collectors.geo_df.query('id == ' + str(collector.id))
                        trained_collector_index = trained_collector.index[0]
                        trained_collector = trained_collectors.geo_df.loc[trained_collector_index]

                        if trained_collector.id == collector.id:
                            pass
                        else:
                            print('Error')
                            print(trained_collector.id, collector.id)
                            exit()

                        if collector.Situacao == 'Com esporos':

                            test_collectors.loc[collector.Index, 'color'] = 'green'
                            true_positive += 1

                            days_error.append(test_collector['DiasAposInicioCiclo'] - (start_day + day))
                        else:
                            test_collectors.loc[collector.Index, 'color'] = 'red'
                            false_positive += 1

                        if true_positive + false_positive != len(test_collectors.query('Detected == 1')):
                            print('Error, hit + miss != len(test_collectors.query(\'Detected == 1\'))')
                            exit()

        for burr in burrs.values():

            key = list(burrs.keys())[list(burrs.values()).index(burr)]

            life_time = trained_collectors.geo_df.loc[key, 'life_time']

            proportionSeg = 1 + TEST_PARAMS['growth_function_distance'](life_time, TEST_PARAMS['base'])

            proportionLarge = 1 + TEST_PARAMS['growth_function_distance'](life_time, TEST_PARAMS['base'])/2

            burr.growTopology(proportionSeg, proportionLarge)

            trained_collectors.geo_df.loc[key, 'life_time'] += 1

    # All the collectors that were not detected but had spores, change their color to yellow
    for collector in test_collectors.itertuples():

        if collector.Detected == 0:

            if collector.Situacao == 'Com esporos':

                test_collectors.loc[collector.Index, 'color'] = 'yellow'
                test_collectors.loc[collector.Index, 'format_shape'] = '*'

    return true_positive, false_positive, days_error

