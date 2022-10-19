import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point


gdf = gpd.read_file('Data/Maps/PR_Municipios_2021/PR_Municipios_2021.shp')
df = pd.read_csv('Data/Collectors/2021/ColetoresSafra2122.csv', sep=';', decimal=',', parse_dates=['Data_1o_Esporos'], infer_datetime_format=True).sort_values(by='Data_1o_Esporos')

def coloring():
    
    global first_apperances

    df['color'] = df['Situacao'].apply(lambda x: 'lightgreen' if x == 'Com esporos' else 'red')
    first_apperances = df[df['Data_1o_Esporos'] == df['Data_1o_Esporos'].min()]

    for i in first_apperances.index:
        df.loc[i, 'color'] = 'yellow'

def plotting():

    # Map plot
    gdf.plot(color='lightgrey', edgecolor='whitesmoke')

    # Title and labels definitions
    plt.title('Ferrugem asiática no Paraná', fontsize=20)
    plt.xlabel('Longitude', fontsize=15)
    plt.ylabel('Latitude', fontsize=15)

    plt.scatter(df['Longitude'], df['Latitude'], color=df['color'], s=50, marker='*')
    for i in range(len(df)):
        if df.loc[i, 'Situacao'] == 'Com esporos':
            plt.annotate(df['Municipio'][i], (df['Longitude'][i], df['Latitude'][i]), fontsize=7)

    for k in range(10):

        for i in range(len(first_apperances)):
            point = Point(first_apperances['Longitude'].iloc[i], first_apperances['Latitude'].iloc[i]).buffer(0.01 * k)
            x, y = point.exterior.xy
            plt.plot(x, y, color='black', linewidth=1)

    plt.show()

if __name__ == '__main__':
    coloring()
    plotting()