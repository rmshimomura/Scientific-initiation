import geopandas as gpd
import pandas as pd
import utils, time, math, datetime
import growth_types as gt

def read_basic_info():
    # Read map file
    _map = gpd.read_file('G:/Meu Drive/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    # Read collectors file and sort them based on the date of the first spores
    _collectors = pd.read_csv('G:/Meu Drive/IC/Codes/Data/Collectors/2021/ColetoresSafra2122.csv', sep=';', decimal=',', parse_dates=['Data_1o_Esporos'], infer_datetime_format=True)
    _collectors = _collectors.sort_values(by=['Data_1o_Esporos'])
            
    _collectors = utils.clean_up(_collectors)

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
    'new_seed_threshold' : 50,
    'collector_penalty' : 50,
}

_map, _collectors = read_basic_info()

start_day = _collectors['Data_1o_Esporos'].iloc[0]
old_circles = []
number_of_valid_collectors = utils.count_valid_collectors(_collectors)

coloring_collectors(_collectors)

error_value, infection_circles, invalid_collectors = gt.circular_growth(_map, _collectors, first_apperances, old_circles, TEST_PARAMS)

print(f"TEST PARAMS: {TEST_PARAMS}")
print(f"Total error (considering only valid collectors): {math.sqrt(error_value/number_of_valid_collectors)}")
print(f"False positives percentage: {invalid_collectors/len(_collectors)*100}%")
print(f"Discovered collectors percentage: {len(infection_circles)/len(_collectors)*100}%")