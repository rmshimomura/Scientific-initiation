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

global root_folder

root_folder = None

global metrics

metrics = []

if 'Meu Drive' in os.getcwd():
    root_folder = 'Meu Drive'
elif 'My Drive' in os.getcwd():
    root_folder = 'My Drive'

def read_basic_info(train_file, test_file):

    global root_folder, burr_buffer

    # Read collectors file
    trained_collectors = pd.read_csv('G:/' + root_folder + '/IC/Codes/Data/Gridded_Data/Trained_Data/' + train_file + '.csv', sep=',', decimal='.', infer_datetime_format=True)
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

    return _map, trained_collectors_geo_df, test_collectors_geo_df

def main(base, number_of_days, train_file, test_file):

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

    _map, trained_collectors_geo_df, test_collectors_geo_df = read_basic_info(train_file, test_file)

    true_positive, false_negative, regions_days_error = gt.test_CGNT(_map, trained_collectors_geo_df, test_collectors_geo_df, TEST_PARAMS)

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

    ''' Circular Growth No Touch Test

    old_geometries = []

    start_day = trained_collectors_geo_df.query('MediaDiasAposInicioCiclo != -1')['MediaDiasAposInicioCiclo'].iloc[0]

    true_positive_penalty, infection_circles, method_used = \
        gt.circular_growth_no_touch(_map, trained_collectors_geo_df, old_geometries, TEST_PARAMS)

    # true_positive_penalty, infection_circles, method_used = \
    #     gt.circular_growth_touch(_map, _collectors_geo_df, old_geometries, TEST_PARAMS)

    true_negative_penalty = 0

    false_positive_penalty = utils.calculate_false_positives_penalty(trained_collectors_geo_df, start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1))

    false_negative_penalty = utils.calculate_false_negatives_penalty(trained_collectors_geo_df, TEST_PARAMS['growth_function_days'], TEST_PARAMS['base'])

    PENALTIES = {
        'true_positive' : true_positive_penalty,
        'true_negative' : true_negative_penalty,
        'false_positive' : false_positive_penalty,
        'false_negative' : false_negative_penalty
    }

    print(f"TEST PARAMS: {TEST_PARAMS}")
    print(f"True positive penalty: {true_positive_penalty}")
    print(f"True negative penalty: {true_negative_penalty}")
    print(f"False positive penalty: {false_positive_penalty}")
    print(f"False negative penalty: {false_negative_penalty}")

    # utils.write_csv(TEST_PARAMS, PENALTIES, start_day, start_day + TEST_PARAMS['number_of_days'], method_used, train_file, time.time() - start_duration)

    '''

    ''' Topology Test

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

    plt.show()
    '''

if __name__ == "__main__":

    number_of_days = 137

    global _map, regions, regions_names

    _map = gpd.read_file('G:/' + root_folder + '/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    map_max_x = _map.bounds.maxx.max()
    map_min_x = _map.bounds.minx.min()
    map_max_y = _map.bounds.maxy.max()
    map_min_y = _map.bounds.miny.min()

    center_x = (map_max_x + map_min_x) / 2
    center_y = (map_max_y + map_min_y) / 2

    regions = []
    regions_names = ['north', 'east', 'south', 'west']
    regions.append(sg.Polygon([(map_min_x, map_max_y), (map_max_x, map_max_y), (center_x, center_y)]))
    regions.append(sg.Polygon([(map_max_x, map_min_y), (map_max_x, map_max_y), (center_x, center_y)]))
    regions.append(sg.Polygon([(map_min_x, map_min_y), (map_max_x, map_min_y), (center_x, center_y)]))
    regions.append(sg.Polygon([(map_min_x, map_min_y), (map_min_x, map_max_y), (center_x, center_y)]))

    for _ in range(len(regions)):
        plt.plot(*regions[_].exterior.xy, color='black', linewidth=0.5)
        plt.annotate(regions_names[_], (regions[_].centroid.x, regions[_].centroid.y), fontsize=5)

    main(990000, number_of_days, '2021-2122', 'coletoressafra2223_31_23')
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

    info = open('G:/' + root_folder + '/IC/Codes/Plots/metrics.csv', 'w', encoding='utf-8')

    info.write('train_file, test_file,base,number_of_days,true_positive,false_positive,days_error_mean_north,days_error_mean_east,days_error_mean_south,days_error_mean_west,days_error_max_north,days_error_max_east,days_error_max_south,days_error_max_west,days_error_min_north,days_error_min_east,days_error_min_south,days_error_min_west,days_error_std_north,days_error_std_east,days_error_std_south,days_error_std_west,days_error_mean_total,days_error_max_total,days_error_min_total,days_error_std_total,real_with_spores,real_without_spores,detected_with_spores,not_detected_with_spores\n')

    for _ in metrics:
        info.write(str(_).replace('[', '').replace(']', '').replace('\'', '') + '\n')
    
    info.close()