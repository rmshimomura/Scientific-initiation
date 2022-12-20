import geopandas as gpd
import pandas as pd
import utils, time, math
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
    
    # Add the column 'color' to the collectors dataframe and set all values to 'red'

    _collectors['color'] = 'white'

    first_apperances = _collectors[_collectors['Data_1o_Esporos'] == _collectors['Data_1o_Esporos'].min()]

    for apperance in first_apperances.itertuples():
        _collectors.loc[apperance.Index, 'color'] = 'yellow'
        _collectors.loc[apperance.Index, 'Detected'] = 1
    
    # Set the colors of the first apperances to 'yellow'
    
    for i in first_apperances.itertuples():
        _collectors.loc[i.Index, 'color'] = 'yellow'
        _collectors.loc[i.Index, 'Detected'] = 1


TEST_PARAMS = {
    'number_of_days' : 200,
    'buffer_factor' : 0.01,
    'new_seed_threshold' : 50,
}

start_time = time.time()

_map, _collectors = read_basic_info()

read_time = time.time()

start_day = _collectors['Data_1o_Esporos'].iloc[0]
old_circles = []

coloring_collectors(_collectors)

coloring_time = time.time()

error_value, infection_circles = gt.circular_growth(_map, _collectors, first_apperances, old_circles, TEST_PARAMS)

growth_time = time.time()

print(f"TEST PARAMS: {TEST_PARAMS}")
print(f"Total error: {math.sqrt(error_value/len(_collectors))}")
print(f"Read time: {read_time - start_time}")
print(f"Coloring time: {coloring_time - read_time}")
print(f"Growth time: {growth_time - coloring_time}")
print(f"Total time: {growth_time - start_time}")

# plotting(0)