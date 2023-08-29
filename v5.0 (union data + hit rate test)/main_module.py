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

metrics = []

def read_basic_info(train_file, test_file):

    global root_folder, burr_buffer

    trained_collectors = None
    trained_collectors_geo_df = None

    if train_file is not None:
        # Read collectors file
        trained_collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Gridded_Data/' + train_file + '.csv', sep=',', decimal='.', infer_datetime_format=True)
        trained_geometry = [sg.Point(x,y) for x,y in zip(trained_collectors.LongitudeDecimal, trained_collectors.LatitudeDecimal)]
        trained_collectors_geo_df = gpd.GeoDataFrame(trained_collectors, geometry=trained_geometry)
        trained_collectors_geo_df['discovery_day'] = None
        trained_collectors_geo_df['circle_created'] = 0
        trained_collectors_geo_df['id'] = trained_collectors_geo_df.index

        if 'MediaDiasAposInicioCiclo' in trained_collectors_geo_df.columns:

            trained_collectors_geo_df = trained_collectors_geo_df.sort_values(by=['MediaDiasAposInicioCiclo'])
        
        else:
            trained_collectors_geo_df = trained_collectors_geo_df.sort_values(by=['DiasAposInicioCiclo'])

        trained_collectors_geo_df = utils.clean_up(trained_collectors_geo_df)
        trained_collectors_geo_df.loc[trained_collectors_geo_df['Situacao'] == 'Com esporos', 'color'] = 'green'
        trained_collectors_geo_df.loc[trained_collectors_geo_df['Situacao'] == 'Encerrado sem esporos', 'color'] = 'red'

    test_collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Gridded_Data/' + test_file + '.csv', sep=',', decimal='.', infer_datetime_format=True)
    test_geometry = [sg.Point(x,y) for x,y in zip(test_collectors.LongitudeDecimal, test_collectors.LatitudeDecimal)]
    test_collectors_geo_df = gpd.GeoDataFrame(test_collectors, geometry=test_geometry)
    test_collectors_geo_df = utils.clean_up(test_collectors_geo_df)
    test_collectors_geo_df['discovery_day'] = None
    test_collectors_geo_df['id'] = test_collectors_geo_df.index
    test_collectors_geo_df['color'] = 'black'
    test_collectors_geo_df['circle_created'] = 0

    return trained_collectors_geo_df, test_collectors_geo_df

def main(base, number_of_days, train_file, test_file, operation_mode, growth_type, number_of_starting_points, radius):

    global _map

    TEST_PARAMS = {
        'number_of_days' : number_of_days,
        'growth_function_distance' : gf.logaritmic_growth_distance,
        'growth_function_days' : gf.logaritmic_growth_days,
        'base' : base,
        'animation' : False,
        'raio_de_abrangencia_imediata' : 0.05*10,
        'raio_de_possivel_contaminacao' : 0.5*10,
        'fator_producao_carrapichos' : 0.05*10,
        'train_file' : train_file,
        'test_file' : test_file,
    }

    trained_collectors_geo_df, test_collectors_geo_df = read_basic_info(train_file, test_file)

    if operation_mode == 'parameter_search':

        true_negative_penalty = 0

        start_day = test_collectors_geo_df.query('DiasAposInicioCiclo != -1').sort_values(by=['DiasAposInicioCiclo'])['DiasAposInicioCiclo'].iloc[0]

        if growth_type == 'CGNT':

            # [SEARCHING FOR A PARAMETER TO FIT ON THE LOGARITHMIC FUNCTION] Circular Growth No Touch

            true_positive_penalty, infection_circles, method_used = \
                gt.circular_growth_no_touch(_map, test_collectors_geo_df, None, TEST_PARAMS)

        elif growth_type == 'CGT': # For now, only not learning based

            # [SEARCHING FOR A PARAMETER TO FIT ON THE LOGARITHMIC FUNCTION] Circular Growth Touch

            old_geometries = []

            true_positive_penalty, infection_circles, method_used = \
                gt.circular_growth_touch(_map, test_collectors_geo_df, old_geometries, number_of_starting_points, TEST_PARAMS)

        elif growth_type == 'MG':

            # [SEARCHING FOR A PARAMETER TO FIT ON THE LOGARITHMIC FUNCTION] Mixed Growth Touch

            true_positive_penalty, infection_circles, method_used = \
                gt.mix_growth(_map, test_collectors_geo_df, None, TEST_PARAMS)

            pass

        elif growth_type == 'TG':

            # [SEARCHING FOR A PARAMETER TO FIT ON THE LOGARITHMIC FUNCTION] Topology Test 

            trained_collectors_instance = coletores.Coletores('LongitudeDecimal', 'LatitudeDecimal', 'Primeiro_Esporo')

            trained_collectors_instance.geo_df = test_collectors_geo_df
            trained_collectors_instance.criaGrafo(test_collectors_geo_df, TEST_PARAMS['raio_de_possivel_contaminacao'])
            trained_collectors_instance.geraTopologiasCrescimento(TEST_PARAMS['raio_de_abrangencia_imediata'], TEST_PARAMS['raio_de_possivel_contaminacao'], 0.01)

            true_positive_penalty, burrs, method_used = \
                gt.topology_growth_no_touch(trained_collectors_instance, TEST_PARAMS)

        false_positive_penalty = utils.calculate_false_positives_penalty(test_collectors_geo_df, start_day + TEST_PARAMS['number_of_days'] - 1)

        false_negative_penalty = utils.calculate_false_negatives_penalty(test_collectors_geo_df, TEST_PARAMS['growth_function_days'], TEST_PARAMS['base'])

        print(f"BASE USED: {base}")
        print(f"Train file used: {train_file}")
        print(f"Test file used: {test_file}")
        print(f"True positive penalty: {true_positive_penalty}")
        print(f"True negative penalty: {true_negative_penalty}")
        print(f"False positive penalty: {false_positive_penalty}")
        print(f"False negative penalty: {false_negative_penalty}")
        print(f"Method used: {method_used}")
        if growth_type == 'CGT':
            print(f"Number of starting points: {number_of_starting_points}")

        print("\n")
        
        results_metrics = [
            method_used,
            number_of_days,
            TEST_PARAMS['growth_function_distance'].__name__,
            TEST_PARAMS['growth_function_days'].__name__,
            base,
            radius,
            train_file if train_file is not None else 'None',
            test_file,
            true_positive_penalty,
            true_negative_penalty,
            false_positive_penalty,
            false_negative_penalty,
        ]
        if growth_type == 'CGT':
            results_metrics.append(number_of_starting_points)
        if growth_type == 'TG':
            results_metrics.append(TEST_PARAMS['raio_de_abrangencia_imediata'])
            results_metrics.append(TEST_PARAMS['raio_de_possivel_contaminacao'])
            results_metrics.append(TEST_PARAMS['fator_producao_carrapichos'])

        return results_metrics

    elif operation_mode == 'test':

        if growth_type == 'CGNT':

            true_positive, false_negative, days_error = t.learning_based_CGNT_MG(trained_collectors_geo_df, test_collectors_geo_df, TEST_PARAMS, 'No touch')

        elif growth_type == 'CGT':

            true_positive, false_negative, days_error = t.normal_testing_CGT(trained_collectors_geo_df, test_collectors_geo_df, TEST_PARAMS, number_of_starting_points)

        elif growth_type == 'MG':

            true_positive, false_negative, days_error = t.learning_based_CGNT_MG(trained_collectors_geo_df, test_collectors_geo_df, TEST_PARAMS, 'Touch')

        elif growth_type == 'TG':

            trained_collectors_instance = coletores.Coletores('LongitudeDecimal', 'LatitudeDecimal', 'Primeiro_Esporo')

            trained_collectors_instance.geo_df = trained_collectors_geo_df
            trained_collectors_instance.criaGrafo(trained_collectors_geo_df, TEST_PARAMS['raio_de_possivel_contaminacao'])
            trained_collectors_instance.geraTopologiasCrescimento(TEST_PARAMS['raio_de_abrangencia_imediata'], TEST_PARAMS['raio_de_possivel_contaminacao'], 0.01)

            true_positive, false_negative, days_error = t.topology_test_TG(trained_collectors_instance, test_collectors_geo_df, TEST_PARAMS)

        else:

            print("Testing not implemented yet")
            exit(1)

        error_sum = sum(days_error)

        error_mean = error_sum / (len(days_error))

        error_max = max(days_error)

        error_min = min(days_error)

        error_std = np.std(days_error)
        
        temp_metrics = [
            growth_type,
            TEST_PARAMS['train_file'], TEST_PARAMS['test_file'], base, radius, number_of_days, true_positive, false_negative, 
            error_mean, error_std, error_max, error_min,
            len(test_collectors_geo_df.query("Situacao == \'Com esporos\'")), len(test_collectors_geo_df.query("Situacao == \'Encerrado sem esporos\'")), len(test_collectors_geo_df.query("Detected == 1 and Situacao == \'Com esporos\'")), len(test_collectors_geo_df.query("Detected == 0 and Situacao == \'Com esporos\'"))
        ]

        if growth_type == 'CGT':
            temp_metrics.append(number_of_starting_points)

        # metrics.append(
        #     growth_type,
        #     [TEST_PARAMS['train_file'], TEST_PARAMS['test_file'], base, radius, number_of_days, true_positive, false_negative, 
        #     error_mean, error_std, error_max, error_min,
        #     len(test_collectors_geo_df.query("Situacao == \'Com esporos\'")), len(test_collectors_geo_df.query("Situacao == \'Encerrado sem esporos\'")), len(test_collectors_geo_df.query("Detected == 1 and Situacao == \'Com esporos\'")), len(test_collectors_geo_df.query("Detected == 0 and Situacao == \'Com esporos\'"))]
        # )

        # if growth_type == 'CGT':
        #     metrics.append(number_of_starting_points)

        return temp_metrics

if __name__ == '__main__':
    # main(10000, 137, 'arithmetic_mean_31_23', 'coletoressafra2021_31_23', 'parameter_search', 'TG')
    main(86679601.69000001, 137, '/Trained_Data/all_together/geometric_mean_31_23', '/Test_Data/coletoressafra2122_31_23', 'test', 'TG', 4, 12938)
