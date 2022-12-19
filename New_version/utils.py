import pandas as pd
import matplotlib.pyplot as plt

def clean_up(_collectors: pd.DataFrame)-> pd.DataFrame: 
    # Reset index
    _collectors.index = range(0, len(_collectors)) 

    # Parse dates
    for i in range(0, len(_collectors)):
        if not pd.isnull(_collectors["Data_1o_Esporos"].iloc[i]):
            _collectors.loc[i, 'Data_1o_Esporos'] = _collectors["Data_1o_Esporos"].iloc[i].strftime('%Y-%m-%d')        

    # Remove unecessary columns
    _collectors = _collectors.drop(columns=['Cultivar', 'Estadio'])
    
    _collectors['Detected'] = 0

    return _collectors

def show_detected_collectors_city_names(_collectors: pd.DataFrame, plt: plt)-> None:
    for i in range(len(_collectors)):
        # Show only cities with collectors with spores
        if _collectors.loc[i, 'Situacao'] == 'Com esporos': 
            plt.gca().annotate(_collectors['Municipio'][i], (_collectors['Longitude'][i], _collectors['Latitude'][i]), fontsize=7)