import pandas as pd
import matplotlib.pyplot as plt

def mode_picker(mode):

    if mode == "Média aritmética":
        return 'arithmetic_mean'
    elif mode == "Média geométrica":
        return 'geometric_mean'
    elif mode == "Média harmônica":
        return 'harmonic_mean'
    else:
        # Print error
        print("Error: Invalid mode")

CGNT_DATA = pd.read_csv(r'G:\My Drive\IC\Codes\Results\Growth_tests\defined_bases\CGNT.csv')
CGT_DATA = pd.read_csv(r'G:\My Drive\IC\Codes\Results\Growth_tests\defined_bases\CGT.csv')

all_harversts = ['2021', '2122', '2223']
all_names = "Média aritmética"
for i in range(3):
    harvest = all_harversts[i]
    title = all_names
    mode = mode_picker(title)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f'Colheita {harvest} - {title.title()} - Número de falsos negativos em relação ao real - CGNT vs CGT')
    ax.set_xlabel('Limites de infecção (Km)')
    ax.set_ylabel('Falsos negativos (unidades)')

    remaining_harvests = [h for h in all_harversts if h != harvest]

    cgnt_harvest = CGNT_DATA[CGNT_DATA['test_file'] == f'coletoressafra{harvest}_31_23']
    cgt_harvest = CGT_DATA[CGT_DATA['test_file'] == f'coletoressafra{harvest}_31_23']

    cgt_harvest_a = cgt_harvest[cgt_harvest['train_file'] == f'coletoressafra{remaining_harvests[0]}_31_23']
    cgt_harvest_b = cgt_harvest[cgt_harvest['train_file'] == f'coletoressafra{remaining_harvests[1]}_31_23']

    cgnt_harvest_mode = cgnt_harvest[cgnt_harvest['train_file'] == f'{mode}_31_23']
    
    ax.plot(cgnt_harvest_mode['radius'], cgnt_harvest_mode['not_detected_with_spores'], 'o-', label='CGNT média', color='red', markersize=10, markeredgecolor='black')
    # ax.plot(cgnt_harvest_mode['radius'], cgnt_harvest_mode['days_error_std_total'], 'o--', label='CGNT desvio padrão', color='red', markersize=10, markeredgecolor='black')
    ax.plot(cgt_harvest_a['radius'], cgt_harvest_a['not_detected_with_spores'], '^-', label=f'CGT 4-primeiros da colheita {remaining_harvests[0]} média', color='green', markersize=10, markeredgecolor='black')
    # ax.plot(cgt_harvest_a['radius'], cgt_harvest_a['days_error_std_total'], '^--', label=f'CGT 4-primeiros da colheita {remaining_harvests[0]} desvio padrão', color='green', markersize=10, markeredgecolor='black')
    ax.plot(cgt_harvest_b['radius'], cgt_harvest_b['not_detected_with_spores'], '*-', label=f'CGT 4-primeiros da colheita {remaining_harvests[1]} média', color='blue', markersize=10, markeredgecolor='black')
    # ax.plot(cgt_harvest_b['radius'], cgt_harvest_b['days_error_std_total'], '*--', label=f'CGT 4-primeiros da colheita {remaining_harvests[1]} desvio padrão', color='blue', markersize=10, markeredgecolor='black')
    ax.axhline(y=0, color='grey', linestyle='--')

    ax.legend()

    plt.tight_layout()

    plt.savefig(rf'G:/My Drive/IC/Codes/Results/Growth_tests/defined_bases/cgnt_vs_cgt/cgnt_cgt_comparison_{mode}_{harvest}_not_detected_with_spores.png', dpi=300, bbox_inches='tight')