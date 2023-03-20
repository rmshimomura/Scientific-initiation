import matplotlib.pyplot as plt
import datetime
import utils
import geopandas as gpd
import pandas as pd
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('svg')

def plot_infection_circles(infection_circles: list, old_circles: list) -> None:

    for infection_circle in infection_circles:
        old_circles.append(plt.plot(*infection_circle.circle.exterior.xy, color='black', linewidth=0.5))

def plotting(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, infection_circles: list, old_circles: list, start_day: datetime.date, day: int) -> None:

    if day == 0:
        _map.plot(color='lightgrey', edgecolor='grey', linewidth=0.5)
        mng = plt.get_current_fig_manager()
        mng.full_screen_toggle()
        plt.xlabel('LongitudeDecimal', fontsize=14)
        plt.ylabel('LatitudeDecimal', fontsize=14)

        # utils.show_detected_collectors_city_names(_collectors, plt)

    for old_circle in old_circles:
        old_circle[0].remove()
    
    old_circles.clear()

    plot_infection_circles(infection_circles, old_circles)
    
    plt.title(f"Ferrugem asiática no Paraná - dia {(start_day + datetime.timedelta(day)).strftime('%Y-%m-%d')} ({day})", fontsize=20)
    plt.scatter(_collectors['LongitudeDecimal'], _collectors['LatitudeDecimal'], color=_collectors['color'], s=100, marker='.')
    
    # plt.tight_layout()
    # plt.gcf().set_size_inches(40, 30)
    # plt.savefig(f'G:/My Drive/IC/Codes/Plots/plot_{day}.svg')
    plt.pause(0.1)

def save_fig_on_day(_map: gpd.GeoDataFrame, _collectors: pd.DataFrame, infection_circles: list, old_circles: list, start_day: datetime.date, day: int) -> None:

    # if day == 0:
    _map.plot(color='lightgrey', edgecolor='grey', linewidth=0.5)
    plt.xlabel('LongitudeDecimal', fontsize=14)
    plt.ylabel('LatitudeDecimal', fontsize=14)

    utils.show_detected_collectors_city_names(_collectors, plt)

    for old_circle in old_circles:
        old_circle[0].remove()
    
    old_circles.clear()

    plot_infection_circles(infection_circles, old_circles)
    
    plt.title(f"Ferrugem asiática no Paraná - dia {(start_day + datetime.timedelta(day)).strftime('%Y-%m-%d')} ({day})", fontsize=20)
    plt.scatter(_collectors['LongitudeDecimal'], _collectors['LatitudeDecimal'], color=_collectors['color'], s=100, marker='.')
    
    plt.tight_layout()
    plt.gcf().set_size_inches(40, 30)
    plt.savefig(f'G:/My Drive/IC/Codes/Plots/plot_{day}.svg')