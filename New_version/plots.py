import matplotlib.pyplot as plt
import datetime
import utils
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

def plotting(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, infection_circles: list, old_geometries: list, start_day: datetime.date, day: int, burrs: gpd.GeoSeries) -> None:

    if day == 0:
        _map.plot(color='lightgrey', edgecolor='grey', linewidth=0.5)
        # mng = plt.get_current_fig_manager()
        # mng.full_screen_toggle()
        plt.xlabel('LongitudeDecimal', fontsize=14)
        plt.ylabel('LatitudeDecimal', fontsize=14)

        # utils.show_detected_collectors_city_names(_collectors, plt)
    for geometry in old_geometries:
        geometry[0].remove()
    
    old_geometries.clear()
    
    if infection_circles is not None:

        plot_infection_circles(infection_circles, old_geometries)
    
    if burrs is not None:
        
        plot_burrs(_map, burrs, old_geometries)
    
    plt.title(f"Ferrugem asiática no Paraná - dia {(start_day + datetime.timedelta(day)).strftime('%Y-%m-%d')} ({day})", fontsize=20)
    plt.scatter(_collectors['LongitudeDecimal'], _collectors['LatitudeDecimal'], color=_collectors['color'], s=100, marker='.')
    plt.pause(4)

def save_fig_on_day(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, infection_circles: list, old_geometries: list, start_day: datetime.date, day: int, burrs: gpd.GeoSeries) -> None:

    _map.plot(color='lightgrey', edgecolor='grey', linewidth=0.5)
    plt.xlabel('LongitudeDecimal', fontsize=14)
    plt.ylabel('LatitudeDecimal', fontsize=14)

    utils.show_detected_collectors_city_names(_collectors, plt)

    if old_geometries is not None:

        for old_circle in old_geometries:
            old_circle[0].remove()
        
        old_geometries.clear()

        plot_infection_circles(infection_circles, old_geometries)
    
    if burrs is not None:
        burrs.plot(color='black', linewidth=0.5)

    plt.title(f"Ferrugem asiática no Paraná - dia {(start_day + datetime.timedelta(day)).strftime('%Y-%m-%d')} ({day})", fontsize=20)
    plt.scatter(_collectors['LongitudeDecimal'], _collectors['LatitudeDecimal'], color=_collectors['color'], s=100, marker='.')
    
    plt.tight_layout()
    plt.gcf().set_size_inches(40, 30)
    plt.savefig(f'G:/My Drive/IC/Codes/Plots/plot_{day}.svg')