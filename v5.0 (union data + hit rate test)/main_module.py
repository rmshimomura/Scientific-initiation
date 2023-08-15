import os
import sys
import geopandas as gpd
import pandas as pd
import utils
import growth_functions as gf
import growth_types as gt
import matplotlib.pyplot as plt
import shapely.geometry as sg
import numpy as np
import coletores, cria_buffers
import time
import datetime
import random
import testing as t

global root_folder, metrics, _map, regions, regions_names

root_folder = None

if 'Meu Drive' in os.getcwd():
    root_folder = 'Meu Drive'
elif 'My Drive' in os.getcwd():
    root_folder = 'My Drive'

number_of_days = 137

_map = gpd.read_file('G:/' + root_folder + '/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

regions, regions_names = utils.generate_regions(_map)

metrics = []

def read_basic_info(train_file, test_file):

    global root_folder, burr_buffer

    trained_collectors = None
    trained_collectors_geo_df = None

    if train_file is not None:
        # Read collectors file
        trained_collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Gridded_Data/Trained_Data/all_together/' + train_file + '.csv', sep=',', decimal='.', infer_datetime_format=True)
        trained_geometry = [sg.Point(x,y) for x,y in zip(trained_collectors.LongitudeDecimal, trained_collectors.LatitudeDecimal)]
        trained_collectors_geo_df = gpd.GeoDataFrame(trained_collectors, geometry=trained_geometry)
        trained_collectors_geo_df['discovery_day'] = None
        trained_collectors_geo_df['id'] = trained_collectors_geo_df.index
        trained_collectors_geo_df = trained_collectors_geo_df.sort_values(by=['MediaDiasAposInicioCiclo'])
        trained_collectors_geo_df = utils.clean_up(trained_collectors_geo_df)
        trained_collectors_geo_df.loc[trained_collectors_geo_df['Situacao'] == 'Com esporos', 'color'] = 'green'
        trained_collectors_geo_df.loc[trained_collectors_geo_df['Situacao'] == 'Encerrado sem esporos', 'color'] = 'red'

    test_collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Gridded_Data/Test_Data/' + test_file + '.csv', sep=',', decimal='.', infer_datetime_format=True)
    test_geometry = [sg.Point(x,y) for x,y in zip(test_collectors.LongitudeDecimal, test_collectors.LatitudeDecimal)]
    test_collectors_geo_df = gpd.GeoDataFrame(test_collectors, geometry=test_geometry)
    test_collectors_geo_df = utils.clean_up(test_collectors_geo_df)
    test_collectors_geo_df['discovery_day'] = None
    test_collectors_geo_df['id'] = test_collectors_geo_df.index
    test_collectors_geo_df['color'] = 'black'
    test_collectors_geo_df['format_shape'] = 'o'

    return trained_collectors_geo_df, test_collectors_geo_df

def main(base, number_of_days, train_file, test_file, LFP, T, CGNT, CGT, TG):

    if LFP == 1 and T == 1:
        print('Looking for parameter and testing cannot happen at the same time.')
        return -1, 'Fail mode type'
    
    if (CGNT == 1 and CGT == 1) or (CGNT == 1 and TG == 1) or (CGT == 1 and TG == 1):
        print('Only one growth type can be used at a time.')
        return -1, 'Fail growth type'

    global _map, regions, regions_names

    TEST_PARAMS = {
        'number_of_days' : number_of_days,
        'growth_function_distance' : gf.logaritmic_growth_distance,
        'growth_function_days' : gf.logaritmic_growth_days,
        'base' : base,
        'animation' : False,
        'Fake_Collectors' : False,
        'raio_de_abrangencia_imediata' : 0.05,
        'raio_de_possivel_contaminacao' : 0.5,
        'train_file' : train_file,
        'test_file' : test_file,
        'regions' : regions,
    }

    LOOKING_FOR_PARAMETER = LFP
    TESTING = T

    CIRCULAR_GROWTH_NO_TOUCH = CGNT
    CIRCULAR_GROWTH_TOUCH = CGT
    TOPOLOGY_GROWTH = TG


    trained_collectors_geo_df, test_collectors_geo_df = read_basic_info(train_file, test_file)

    if LOOKING_FOR_PARAMETER:

        true_negative_penalty = 0

        if CIRCULAR_GROWTH_NO_TOUCH:

            # [SEARCHING FOR A PARAMETER TO FIT ON THE LOGARITHMIC FUNCTION] Circular Growth No Touch

            start_day = trained_collectors_geo_df.query('MediaDiasAposInicioCiclo != -1')['MediaDiasAposInicioCiclo'].iloc[0]

            true_positive_penalty, infection_circles, method_used = \
                gt.circular_growth_no_touch(_map, trained_collectors_geo_df, old_geometries, TEST_PARAMS)

            false_positive_penalty = utils.calculate_false_positives_penalty(trained_collectors_geo_df, start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1))

            false_negative_penalty = utils.calculate_false_negatives_penalty(trained_collectors_geo_df, TEST_PARAMS['growth_function_days'], TEST_PARAMS['base'])

        elif CIRCULAR_GROWTH_TOUCH:

            # [SEARCHING FOR A PARAMETER TO FIT ON THE LOGARITHMIC FUNCTION] Circular Growth Touch

            start_day = test_collectors_geo_df.query("DiasAposInicioCiclo != -1").sort_values(by=['DiasAposInicioCiclo'])['DiasAposInicioCiclo'].iloc[0]

            old_geometries = []

            true_positive_penalty, infection_circles, method_used = \
                gt.circular_growth_touch(_map, test_collectors_geo_df, old_geometries, TEST_PARAMS)

            false_positive_penalty = utils.calculate_false_positives_penalty(test_collectors_geo_df, start_day + TEST_PARAMS['number_of_days'] - 1)

            false_negative_penalty = utils.calculate_false_negatives_penalty(test_collectors_geo_df, TEST_PARAMS['growth_function_days'], TEST_PARAMS['base'])

        elif TOPOLOGY_GROWTH:

            ''' [SEARCHING FOR A PARAMETER TO FIT ON THE LOGARITHMIC FUNCTION] Topology Test 

            old_geometries = []

            collectors_instance = coletores.Coletores('LongitudeDecimal', 'LatitudeDecimal', 'Primeiro_Esporo')
            collectors_instance.geo_df = _collectors_geo_df
            collectors_instance.criaGrafo(_collectors_geo_df, TEST_PARAMS['raio_de_possivel_contaminacao'])
            collectors_instance.geraTopologiasCrescimento(TEST_PARAMS['raio_de_abrangencia_imediata'], TEST_PARAMS['raio_de_possivel_contaminacao'], 0.01)

            # If the parameter is set to true, the buffers are generated in a weird way, that is incorrect
            buffers = cria_buffers.geraBuffersCarrapichos(collectors_instance.topologiaCrescimentoDict.values(), 0.005, True)
            _map.plot()

            for key, growth_topology in collectors_instance.topologiaCrescimentoDict.items():

                for segment in growth_topology.getSegments():

                    seg = segment.seg
                    plt.plot(*seg.xy, color='black', linewidth=0.5)

            for _ in range(len(collectors_instance.geo_df)):

                center_point = collectors_instance.geo_df.iloc[_].geometry
                plt.scatter(center_point.x, center_point.y, color=collectors_instance.geo_df.iloc[_].color, s=5)
                plt.annotate(_, (center_point.x, center_point.y), fontsize=5)

            for _ in range(len(buffers)):
                plt.plot(*buffers[_].exterior.xy, color='yellow', linewidth=0.5)

            plt.show()

            first_apperances  = _collectors_geo_df[_collectors_geo_df['DiasAposInicioCiclo'] == _collectors_geo_df['DiasAposInicioCiclo'].min()]

            true_positive_penalty, infection_circles, method_used = \
                gt.circular_growth(_map, _collectors_geo_df, first_apperances, old_geometries, TEST_PARAMS)

            gt.topology_growth(_map, collectors_instance, old_geometries, TEST_PARAMS, plt)

            '''


        PENALTIES = {
            'true_positive' : true_positive_penalty,
            'true_negative' : true_negative_penalty,
            'false_positive' : false_positive_penalty,
            'false_negative' : false_negative_penalty
        }

        print(f"BASE USED: {base}")
        print(f"Train file used: {train_file}")
        print(f"Test file used: {test_file}")
        print(f"True positive penalty: {true_positive_penalty}")
        print(f"True negative penalty: {true_negative_penalty}")
        print(f"False positive penalty: {false_positive_penalty}")
        print(f"False negative penalty: {false_negative_penalty}")

        utils.write_csv(TEST_PARAMS, PENALTIES, start_day, start_day + TEST_PARAMS['number_of_days'], method_used, train_file, -1)

    elif TESTING:

        if CIRCULAR_GROWTH_NO_TOUCH:

            true_positive, false_negative, regions_days_error = t.test_CGNT(_map, trained_collectors_geo_df, test_collectors_geo_df, TEST_PARAMS)

        else:

            print("Testing not implemented yet")
            exit(1)

        total_error_sum = sum(regions_days_error[0]) + sum(regions_days_error[1]) + sum(regions_days_error[2]) + sum(regions_days_error[3])

        total_error_mean = total_error_sum / (len(regions_days_error[0]) + len(regions_days_error[1]) + len(regions_days_error[2]) + len(regions_days_error[3]))

        total_error_max = max(max(regions_days_error[0]), max(regions_days_error[1]), max(regions_days_error[2]), max(regions_days_error[3]))

        total_error_min = min(min(regions_days_error[0]), min(regions_days_error[1]), min(regions_days_error[2]), min(regions_days_error[3]))

        total_error_std = np.std(regions_days_error[0] + regions_days_error[1] + regions_days_error[2] + regions_days_error[3])

        metrics.append(
            [TEST_PARAMS['train_file'], TEST_PARAMS['test_file'], base, number_of_days, true_positive, false_negative, 
            sum(regions_days_error[0]) / len(regions_days_error[0]), sum(regions_days_error[1]) / len(regions_days_error[1]), sum(regions_days_error[2]) / len(regions_days_error[2]), sum(regions_days_error[3]) / len(regions_days_error[3]),
            max(regions_days_error[0]), max(regions_days_error[1]), max(regions_days_error[2]), max(regions_days_error[3]),
            min(regions_days_error[0]), min(regions_days_error[1]), min(regions_days_error[2]), min(regions_days_error[3]),
            np.std(regions_days_error[0]),np.std(regions_days_error[1]),np.std(regions_days_error[2]),np.std(regions_days_error[3]),
            total_error_mean, total_error_max, total_error_min, total_error_std,
            len(test_collectors_geo_df.query("Situacao == \'Com esporos\'")), len(test_collectors_geo_df.query("Situacao == \'Encerrado sem esporos\'")), len(test_collectors_geo_df.query("Detected == 1 and Situacao == \'Com esporos\'")), len(test_collectors_geo_df.query("Detected == 0 and Situacao == \'Com esporos\'"))]
        )

        return metrics


    # return TEST_PARAMS, PENALTIES

def all_means_test(number_of_days):

    main(990000, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2021_31_23')
    main(990000, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2122_31_23')
    main(990000, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2223_31_23')

    main(990000, number_of_days, 'geometric_mean_31_23', 'coletoressafra2021_31_23')
    main(990000, number_of_days, 'geometric_mean_31_23', 'coletoressafra2122_31_23')
    main(990000, number_of_days, 'geometric_mean_31_23', 'coletoressafra2223_31_23')

    main(990000, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2021_31_23')
    main(990000, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2122_31_23')
    main(990000, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2223_31_23')


    main(99000, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2021_31_23')
    main(99000, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2122_31_23')
    main(99000, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2223_31_23')

    main(99000, number_of_days, 'geometric_mean_31_23', 'coletoressafra2021_31_23')
    main(99000, number_of_days, 'geometric_mean_31_23', 'coletoressafra2122_31_23')
    main(99000, number_of_days, 'geometric_mean_31_23', 'coletoressafra2223_31_23')

    main(99000, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2021_31_23')
    main(99000, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2122_31_23')
    main(99000, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2223_31_23')


    main(9900, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2021_31_23')
    main(9900, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2122_31_23')
    main(9900, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2223_31_23')

    main(9900, number_of_days, 'geometric_mean_31_23', 'coletoressafra2021_31_23')
    main(9900, number_of_days, 'geometric_mean_31_23', 'coletoressafra2122_31_23')
    main(9900, number_of_days, 'geometric_mean_31_23', 'coletoressafra2223_31_23')

    main(9900, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2021_31_23')
    main(9900, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2122_31_23')
    main(9900, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2223_31_23')


    main(990, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2021_31_23')
    main(990, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2122_31_23')
    main(990, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2223_31_23')

    main(990, number_of_days, 'geometric_mean_31_23', 'coletoressafra2021_31_23')
    main(990, number_of_days, 'geometric_mean_31_23', 'coletoressafra2122_31_23')
    main(990, number_of_days, 'geometric_mean_31_23', 'coletoressafra2223_31_23')

    main(990, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2021_31_23')
    main(990, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2122_31_23')
    main(990, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2223_31_23')

def pairs_test(number_of_days):

    main(99000, number_of_days, '2021-2122', 'coletoressafra2223_31_23')
    main(9900, number_of_days, '2021-2122', 'coletoressafra2223_31_23')
    main(990, number_of_days, '2021-2122', 'coletoressafra2223_31_23')
    main(99, number_of_days, '2021-2122', 'coletoressafra2223_31_23')
    main(990000, number_of_days, '2021-2223', 'coletoressafra2122_31_23')
    main(99000, number_of_days, '2021-2223', 'coletoressafra2122_31_23')
    main(9900, number_of_days, '2021-2223', 'coletoressafra2122_31_23')
    main(990, number_of_days, '2021-2223', 'coletoressafra2122_31_23')
    main(99, number_of_days, '2021-2223', 'coletoressafra2122_31_23')
    main(990000, number_of_days, '2122-2223', 'coletoressafra2021_31_23')
    main(99000, number_of_days, '2122-2223', 'coletoressafra2021_31_23')
    main(9900, number_of_days, '2122-2223', 'coletoressafra2021_31_23')
    main(990, number_of_days, '2122-2223', 'coletoressafra2021_31_23')
    main(99, number_of_days, '2122-2223', 'coletoressafra2021_31_23')