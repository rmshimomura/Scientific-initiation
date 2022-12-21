import geopandas as gpd
import pandas as pd
import utils, time, math, datetime
import growth_types as gt

def read_basic_info():
    # Read map file
    _map = gpd.read_file('G:/My Drive/IC/Codes/Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp') 

    # Read collectors file and sort them based on the date of the first spores
    _collectors = pd.read_csv('G:/My Drive/IC/Codes/Data/Collectors/2021/ColetoresSafra2122.csv', sep=';', decimal=',', parse_dates=['Data_1o_Esporos'], infer_datetime_format=True)
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
    'buffer_factor' : 0.01,
    'new_seed_threshold' : 50,
    'collector_penalty' : 50,
    'expansion_threshold' : 28,
}

start_time = time.time()

_map, _collectors = read_basic_info()

read_time = time.time()

start_day = _collectors['Data_1o_Esporos'].iloc[0]
old_circles = []

TEST_PARAMS['end_day'] = start_day + datetime.timedelta(days=TEST_PARAMS['number_of_days'] - 1)

coloring_collectors(_collectors)

coloring_time = time.time()

error_value, infection_circles = gt.circular_growth(_map, _collectors, first_apperances, old_circles, TEST_PARAMS)

growth_time = time.time()

print(f"TEST PARAMS: {TEST_PARAMS}")
print(f"Total error: {math.sqrt(error_value/len(_collectors))}")
print(f"Read time: {round(read_time - start_time, 2)}s")
print(f"Coloring time: {round(coloring_time - read_time, 2)}s")
print(f"Growth time: {round(growth_time - coloring_time, 2)}s")
print(f"Total time: {round(growth_time - start_time, 2)}s")