import geopandas as gpd
import pandas as pd
import utils, time, math, datetime
import growth_types as gt
import growth_functions as gf

def read_basic_info():
    # Read map file
    _map = gpd.read_file('G:/My Drive/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    # Read collectors file and sort them based on the date of the first spores
    _collectors = pd.read_csv('G:/My Drive/IC/Codes/Data/Collectors/2021/ColetoresSafra2122.csv', sep=';', decimal=',', parse_dates=['Data_1o_Esporos'], infer_datetime_format=True)
    _collectors = _collectors.sort_values(by=['Data_1o_Esporos'])
            
    _collectors = utils.clean_up(_collectors)

    _collectors['discovery_day'] = None

    return _map, _collectors

def coloring_collectors(_collectors):

    global first_apperances

    _collectors['color'] = 'white'

    first_apperances = _collectors[_collectors['Data_1o_Esporos'] == _collectors['Data_1o_Esporos'].min()]

    for apperance in first_apperances.itertuples():
        _collectors.loc[apperance.Index, 'color'] = 'yellow'
        _collectors.loc[apperance.Index, 'Detected'] = 1
    
    for i in first_apperances.itertuples():
        _collectors.loc[i.Index, 'color'] = 'yellow'
        _collectors.loc[i.Index, 'Detected'] = 1

TEST_PARAMS = {
    'number_of_days' : 200,
}

_map, _collectors = read_basic_info()

start_day = _collectors['Data_1o_Esporos'].iloc[0]
old_circles = []
number_of_valid_collectors = utils.count_valid_collectors(_collectors)

coloring_collectors(_collectors)

true_positive_penalty, infection_circles = gt.circular_growth(_map, _collectors, first_apperances, old_circles, TEST_PARAMS, gf.base_50_div_2_logarithmic_growth_distance)

true_negative_penalty = 0

false_positive_penalty = utils.calculate_false_positives_penalty(_collectors, start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1))

false_negative_penalty = utils.calculate_false_negatives_penalty(_collectors, gf.base_50_div_2_logarithmic_growth_days)

total_error = true_positive_penalty + true_negative_penalty + false_positive_penalty + false_negative_penalty

print(f"TEST PARAMS: {TEST_PARAMS}")
print(f"True positive penalty: {true_positive_penalty}")
print(f"True negative penalty: {true_negative_penalty}")
print(f"False positive penalty: {false_positive_penalty}")
print(f"False negative penalty: {false_negative_penalty}")
print(f"Total error {math.sqrt(total_error/len(_collectors))}\n\n")

for i in range(len(infection_circles)):
    print(f"Circle {i} has {infection_circles[i].buffer * 111.045} km of radius and {infection_circles[i].life_span} life span")