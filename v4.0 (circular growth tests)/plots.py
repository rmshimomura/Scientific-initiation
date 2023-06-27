import matplotlib.pyplot as plt
import datetime
import utils
import os
import geopandas as gpd
import pandas as pd
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('svg')

def plot_infection_circles(infection_circles: list, old_geometries: list) -> None:

    for infection_circle in infection_circles:
        old_geometries.append(plt.plot(*infection_circle.circle.exterior.xy, color='black', linewidth=0.5))

def plot_burrs(_map: gpd.GeoDataFrame, burrs: gpd.GeoSeries, old_geometries: list) -> None:

    for burr in burrs:
        geometry = burr.geometry
        x, y = geometry.exterior.xy
        old_geometries.append(plt.plot(x, y, color='black', linewidth=0.5))

def plotting(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, infection_circles: list, old_geometries: list, start_day: datetime.date, day: int, burrs: gpd.GeoSeries, fake_collectors_buffers_list: list) -> None:

    if day == 0:
        _map.plot(color='lightgrey', edgecolor='grey', linewidth=0.5)
        mng = plt.get_current_fig_manager()
        # mng.full_screen_toggle()
        plt.xlabel('Longitude Decimal', fontsize=14)
        plt.ylabel('Latitude Decimal', fontsize=14)

        # utils.show_detected_collectors_city_names(_collectors, plt)
    for geometry in old_geometries:
        geometry[0].remove()
    
    old_geometries.clear()
    
    if infection_circles is not None:

        plot_infection_circles(infection_circles, old_geometries)
    
    if burrs is not None:
        
        plot_burrs(_map, burrs, old_geometries)
    
    if fake_collectors_buffers_list is not None:
        for _list in fake_collectors_buffers_list:
            for _buffer in _list.buffer_list:
                _buffer = _buffer.line.buffer(_buffer.buffer)
                x, y = _buffer.exterior.xy
                plt.plot(x, y, color='blue', linewidth=0.5, linestyle='--')

    plt.title(f"Ferrugem asiática no Paraná - dia {(start_day + datetime.timedelta(day)).strftime('%Y-%m-%d')} ({day})", fontsize=20)
    plt.tight_layout()
    plt.scatter(_collectors['LongitudeDecimal'], _collectors['LatitudeDecimal'], color=_collectors['color'], s=100, marker='.')
    plt.pause(1)

def save_fig_on_day(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, infection_circles: list, old_geometries: list, start_day: datetime.date, day: int, burrs: gpd.GeoSeries, fake_collectors_buffers_list):

    _map.plot(color='lightgrey', edgecolor='grey', linewidth=1)

    root_folder = None

    if 'Meu Drive' in os.getcwd():
        root_folder = 'Meu Drive'
    elif 'My Drive' in os.getcwd():
        root_folder = 'My Drive'

    # utils.show_detected_collectors_city_names(_collectors, plt)

    if old_geometries is not None:

        for old_circle in old_geometries:
            old_circle[0].remove()
        
        old_geometries.clear()

    if infection_circles is not None:
        plot_infection_circles(infection_circles, old_geometries)
    
    if burrs is not None:
        for _ in burrs:
            x, y = _.geometry.exterior.xy
            plt.plot(x, y, color='black', linewidth=0.5)

    if fake_collectors_buffers_list is not None:
        for _list in fake_collectors_buffers_list:
            for _buffer in _list.buffer_list:
                _buffer = _buffer.line.buffer(1)
                x, y = _buffer.exterior.xy
                plt.plot(x, y, color='blue', linewidth=0.5, linestyle='--')

    plt.title(f"Ferrugem asiática no Paraná - dia {(start_day + datetime.timedelta(day)).strftime('%Y-%m-%d')} ({day})", fontsize=20)
    plt.scatter(_collectors['LongitudeDecimal'], _collectors['LatitudeDecimal'], color=_collectors['color'], s=100, marker='.')
    
    plt.tight_layout()
    # plt.gcf().set_size_inches(40, 30)
    plt.savefig(f'G:/' + root_folder + f"/IC/Codes/Plots/plot_{day}_{'burr' if burrs is not None else 'circles'}.svg", bbox_inches='tight')