import matplotlib.pyplot as plt
from IPython.display import set_matplotlib_formats
set_matplotlib_formats('png')

def plot_def_circles(_map, _collectors, infection_circles, start_day, day):

    _map.plot(color='white', edgecolor='grey', linewidth=0.3, alpha=0.5)

    # for infection_circle in infection_circles:
    #     plt.plot(*infection_circle.circle.exterior.xy, color='black', linewidth=0.6, alpha=1, linestyle='--')
    
    for collector in _collectors.itertuples():

        if collector.Detected == 1:

            if collector.Situacao == 'Encerrado sem esporos':
                plt.scatter(collector.LongitudeDecimal, collector.LatitudeDecimal, color='red', s=100, marker='.', alpha=0.2)
            elif collector.Situacao == 'Com esporos':
                value = (100/137) * abs(collector.DiasAposInicioCiclo - collector.discovery_day)
                plt.scatter(collector.LongitudeDecimal, collector.LatitudeDecimal, color='green', s=100, marker='.', alpha=(100-(value))/100)
            else:
                print(f"ERROR - {collector.Situacao}")
                exit()
        else:
            
            plt.scatter(collector.LongitudeDecimal, collector.LatitudeDecimal, color='black', s=40, marker='.', alpha=0.1)

    plt.title(f"Ferrugem asiática no Paraná - dia {day + 1}", fontsize=20)
    plt.tight_layout()

    plt.savefig(f'./{day + 1}.png', bbox_inches='tight')

    plt.clf()

def plot_def_topologies(_map, _collectors, topologies, buffers, start_day, day):

    _map.plot(color='white', edgecolor='grey', linewidth=0.3, alpha=0.5)

    # for topology in topologies:

    #     segments = topology.getSegments()

    #     for segment in segments:

    #         seg = segment.seg

    #         plt.plot(*seg.xy, color='black', linewidth=0.6, alpha=1)

    for collector in _collectors.itertuples():

        if collector.Detected == 1:

            if collector.Situacao == 'Encerrado sem esporos':
                plt.scatter(collector.LongitudeDecimal, collector.LatitudeDecimal, color='red', s=100, marker='.', alpha=0.2)
            elif collector.Situacao == 'Com esporos':
                value = (100/137) * abs(collector.DiasAposInicioCiclo - collector.discovery_day)
                plt.scatter(collector.LongitudeDecimal, collector.LatitudeDecimal, color='green', s=100, marker='.', alpha=(100-(value))/100)
            else:
                print(f"ERROR - {collector.Situacao}")
                exit()
        else:

            plt.scatter(collector.LongitudeDecimal, collector.LatitudeDecimal, color='black', s=40, marker='.', alpha=0.1)
        
    # for buffer in buffers:

    #     plt.plot(*buffer.exterior.xy, color='black', linewidth=0.6, alpha=1, linestyle='--')

    
    plt.title(f"Ferrugem asiática no Paraná - dia {day + 1}", fontsize=20)
    plt.tight_layout()

    plt.savefig(f'./{day + 1}_final.png', bbox_inches='tight')