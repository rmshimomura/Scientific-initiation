import pandas as pd
from infection_circle import Infection_Circle
from shapely.geometry import Point

def learning_based(trained_collectors: pd.DataFrame, test_collectors: pd.DataFrame, TEST_PARAMS: dict, mode):

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

                        if mode == 'Touch':
                            new_infection_circle = Infection_Circle(
                                Point(collector.LongitudeDecimal, collector.LatitudeDecimal),
                                1, 
                                start_day + day
                            )

                            trained_collectors.loc[trained_collector.index[0], 'Detected'] = 1

                            infection_circles.append(new_infection_circle)
        
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
