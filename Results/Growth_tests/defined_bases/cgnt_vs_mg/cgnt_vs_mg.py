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
MG_DATA = pd.read_csv(r'G:\My Drive\IC\Codes\Results\Growth_tests\defined_bases\MG.csv')

all_harversts = ['2021', '2122', '2223']
all_names = "Média aritmética"
for i in range(3):
    harvest = all_harversts[i]
    title = all_names
    mode = mode_picker(title)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f'Colheita {harvest} - {title.title()} - Número de falsos positivos em relação ao real - CGNT vs MG')
    ax.set_xlabel('Limites de infecção (Km)')
    ax.set_ylabel('Falsos positivos (unidades)')
    column_to_show = 'false_positive'

    cgnt_harvest = CGNT_DATA[CGNT_DATA['test_file'] == f'coletoressafra{harvest}_31_23']
    mg_harvest = MG_DATA[MG_DATA['test_file'] == f'coletoressafra{harvest}_31_23']

    cgnt_harvest_mode = cgnt_harvest[cgnt_harvest['train_file'] == f'{mode}_31_23']
    mg_harvest_mode = mg_harvest[mg_harvest['train_file'] == f'{mode}_31_23']
    
    ax.plot(cgnt_harvest_mode['radius'], cgnt_harvest_mode[column_to_show], 'o-', label='CGNT', color='red', markersize=10, markeredgecolor='black')
    ax.plot(mg_harvest_mode['radius'], mg_harvest_mode[column_to_show], '^-', label='MG', color='green', markersize=10, markeredgecolor='black')
    ax.axhline(y=0, color='grey', linestyle='--')

    ax.legend()

    plt.tight_layout()

    plt.savefig(rf'G:/My Drive/IC/Codes/Results/Growth_tests/defined_bases/cgnt_vs_mg/cgnt_mg_comparison_{mode}_{harvest}_{column_to_show}.png', dpi=300, bbox_inches='tight')