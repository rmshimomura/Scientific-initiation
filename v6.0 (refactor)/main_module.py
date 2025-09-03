import os
import geopandas as gpd
import pandas as pd
import utils
import growth_functions as gf
import growth_types as gt
import shapely.geometry as sg
import numpy as np
import coletores
import testing as t

global metrics, _map, regions, regions_names




#OBSERVAÇÃO MARCOS, APÓS ALGUNS ANOS SEM RODAR O CODIGO ALGUMAS LIBS PASSARAM A SOLTAR MUITOS WARNINGS,...
#ENTÃO OPTEI POR COLOCAR ESSE FILTRO PARA NÃO POLUIR TANTO O OUTPUT, MAS SE QUISEREM VER OS WARNINGS OU O,...
#CODIGO PARAR DE FUNCIONAR, É SÓ REMOVER ESSA LINHA E VERIFICAR OS WARNINGS PARA ATTS. DE METODOS
import warnings

warnings.filterwarnings('ignore')

_map = gpd.read_file(r'../Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

metrics = []

def read_basic_info(train_file, test_file):

    global burr_buffer

    trained_collectors = None
    trained_collectors_geo_df = None

    if train_file is not None:
        # Read collectors file
        trained_collectors = pd.read_csv(rf"{train_file}", sep=',', decimal='.', infer_datetime_format=True)

        # Used with topologies
        trained_geometry = [sg.Point(x,y) for x,y in zip(trained_collectors.LongitudeDecimal, trained_collectors.LatitudeDecimal)]
        trained_collectors_geo_df = gpd.GeoDataFrame(trained_collectors, geometry=trained_geometry)
        
        trained_collectors_geo_df['discovery_day'] = None
        trained_collectors_geo_df['circle_created'] = 0

        if 'MediaDiasAposInicioCiclo' in trained_collectors_geo_df.columns:

            trained_collectors_geo_df = trained_collectors_geo_df.sort_values(by=['MediaDiasAposInicioCiclo'])
        
        else:
            trained_collectors_geo_df = trained_collectors_geo_df.sort_values(by=['DiasAposInicioCiclo'])

        trained_collectors_geo_df = utils.clean_up(trained_collectors_geo_df)
        trained_collectors_geo_df.loc[trained_collectors_geo_df['Situacao'] == 'Com esporos', 'color'] = 'green'
        trained_collectors_geo_df.loc[trained_collectors_geo_df['Situacao'] == 'Encerrado sem esporos', 'color'] = 'red'

    test_collectors = pd.read_csv(rf"{test_file}", sep=',', decimal='.', infer_datetime_format=True)
    test_geometry = [sg.Point(x,y) for x,y in zip(test_collectors.LongitudeDecimal, test_collectors.LatitudeDecimal)]
    test_collectors_geo_df = gpd.GeoDataFrame(test_collectors, geometry=test_geometry)
    test_collectors_geo_df = utils.clean_up(test_collectors_geo_df)
    test_collectors_geo_df['discovery_day'] = None
    test_collectors_geo_df['color'] = 'black'
    test_collectors_geo_df['circle_created'] = 0

    return trained_collectors_geo_df, test_collectors_geo_df

def main(base, number_of_days, train_file, test_file, operation_mode, growth_type, number_of_starting_points, radius, proportion_seg, proportion_larg):

    global _map

    TEST_PARAMS = {
        'number_of_days' : number_of_days,
        'growth_function_distance' : gf.logaritmic_growth_distance,
        'growth_function_days' : gf.logaritmic_growth_days,
        'base' : base,
        'train_file' : train_file,
        'test_file' : test_file,
        'number_of_starting_points' : number_of_starting_points,
        'proportionSeg' : proportion_seg,
        'proportionLarg' : proportion_larg,
        'expansion_days_limit' : 105,
        'larg_seg' : 0.01
    }

    if growth_type == 'TG':

        TEST_PARAMS['raio_de_abrangencia_imediata'] = TEST_PARAMS['growth_function_distance'](2, TEST_PARAMS['base'])
        TEST_PARAMS['raio_de_possivel_contaminacao'] = TEST_PARAMS['growth_function_distance'](TEST_PARAMS['expansion_days_limit'], TEST_PARAMS['base'])

    trained_collectors_geo_df, test_collectors_geo_df = read_basic_info(train_file, test_file)

    if operation_mode == 'parameter_search':

        true_negative_penalty = 0

        days_column = 'DiasAposInicioCiclo' if 'DiasAposInicioCiclo' in test_collectors_geo_df.columns else 'MediaDiasAposInicioCiclo'

        start_day = test_collectors_geo_df.query(f'{days_column} != -1').sort_values(by=[days_column])[days_column].iloc[0]

        if growth_type == 'CGNT':

            true_positive_penalty, method_used = gt.circular_growth_no_touch(test_collectors_geo_df, TEST_PARAMS)

        elif growth_type == 'CGT':

            true_positive_penalty, method_used = gt.circular_growth_touch(test_collectors_geo_df, number_of_starting_points, TEST_PARAMS)

        elif growth_type == 'MG':

            true_positive_penalty, method_used = gt.mix_growth(test_collectors_geo_df, None, TEST_PARAMS)

        elif growth_type == 'TG':

            test_collectors_instance = coletores.Coletores('LongitudeDecimal', 'LatitudeDecimal', 'Primeiro_Esporo')

            test_collectors_instance.geo_df = test_collectors_geo_df
            test_collectors_instance.criaGrafo(test_collectors_geo_df, TEST_PARAMS['raio_de_possivel_contaminacao'])
            test_collectors_instance.geraTopologiasCrescimento(TEST_PARAMS['raio_de_abrangencia_imediata'], TEST_PARAMS['raio_de_possivel_contaminacao'], TEST_PARAMS['larg_seg'])

            true_positive_penalty, method_used = gt.topology_growth_no_touch(test_collectors_instance, TEST_PARAMS, _map)

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
            results_metrics.append(proportion_seg)
            results_metrics.append(proportion_larg)

        return results_metrics

    elif operation_mode == 'test':

        if growth_type == 'CGNT':

            true_positive, false_positive, days_error = t.learning_based_CGNT_MG(_map, trained_collectors_geo_df, test_collectors_geo_df, TEST_PARAMS, 'No touch')

        elif growth_type == 'CGT':

            true_positive, false_positive, days_error = t.normal_testing_CGT(_map, trained_collectors_geo_df, test_collectors_geo_df, TEST_PARAMS, number_of_starting_points)

        elif growth_type == 'MG':

            true_positive, false_positive, days_error = t.learning_based_CGNT_MG(_map, trained_collectors_geo_df, test_collectors_geo_df, TEST_PARAMS, 'Touch')

        elif growth_type == 'TG':

            trained_collectors_instance = coletores.Coletores('LongitudeDecimal', 'LatitudeDecimal', 'Primeiro_Esporo')

            trained_collectors_instance.geo_df = trained_collectors_geo_df
            trained_collectors_instance.criaGrafo(trained_collectors_geo_df, TEST_PARAMS['raio_de_possivel_contaminacao'])
            trained_collectors_instance.geraTopologiasCrescimento(TEST_PARAMS['raio_de_abrangencia_imediata'], TEST_PARAMS['raio_de_possivel_contaminacao'], TEST_PARAMS['larg_seg'])

            true_positive, false_positive, days_error, debug = t.topology_test_TG(_map, trained_collectors_instance, test_collectors_geo_df, TEST_PARAMS)

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
            TEST_PARAMS['train_file'].split('\\')[-1].split('.')[0], TEST_PARAMS['test_file'].split('\\')[-1].split('.')[0], base, radius, number_of_days, true_positive, false_positive, 
            error_mean, error_std, error_max, error_min,
            len(test_collectors_geo_df.query("Situacao == \'Com esporos\'")), len(test_collectors_geo_df.query("Situacao == \'Encerrado sem esporos\'")), len(test_collectors_geo_df.query("Detected == 1 and Situacao == \'Com esporos\'")), len(test_collectors_geo_df.query("Detected == 0 and Situacao == \'Com esporos\'"))
        ]

        if growth_type == 'CGT':
            temp_metrics.append(number_of_starting_points)
        
        if growth_type == 'TG':
            temp_metrics.append(proportion_seg)
            temp_metrics.append(proportion_larg)

        print(f"Train file used: {temp_metrics[1]}")
        print(f"Test file used: {temp_metrics[2]}")
        print(f"Base used: {temp_metrics[3]}")
        print(f"Radius used: {temp_metrics[4]}")
        print(f"Number of days used: {temp_metrics[5]}")
        print(f"True positive: {temp_metrics[6]}")
        print(f"False positive: {temp_metrics[7]}")
        print(f"Error mean: {temp_metrics[8]}")
        print(f"Error std: {temp_metrics[9]}")
        print(f"Error max: {temp_metrics[10]}")
        print(f"Error min: {temp_metrics[11]}")
        print()
        return temp_metrics

if __name__ == '__main__':
    main(30606342.505, 137, r'../Data/Gridded_Data/Trained_Data/all_together/arithmetic_mean_31_23.csv', r'../Data/Gridded_Data/Test_Data/coletoressafra2021_31_23.csv', 'parameter_search', 'TG', 1, 30, 1.06, 1.04)
    # main(12110.717000000004, 137, r'../Data/Gridded_Data/Test_Data/coletoressafra2122_31_23.csv', r'../Data/Gridded_Data/Test_Data/coletoressafra2021_31_23.csv', 'test', 'CGT', 4, 55, 1.06, 1.04)
    # main(961554092.8640003, 137, None, r'../Data/Gridded_Data/Trained_Data/all_together/arithmetic_mean_31_23.csv', 'parameter_search', 'TG', 1, 25, 1.05, 1.04)