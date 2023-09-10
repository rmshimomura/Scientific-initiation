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
MG_DATA = pd.read_csv(r'G:\My Drive\IC\Codes\Results\Growth_tests\defined_bases\MG.csv')
TG_DATA = pd.read_csv(r'G:\My Drive\IC\Codes\Results\Growth_tests\defined_bases\TG.csv')

all_harversts = ['2021', '2122', '2223']
all_names = "Média aritmética"
for i in range(3):
    harvest = all_harversts[i]
    title = all_names
    mode = mode_picker(title)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f'Colheita {harvest} - {title.title()} - Desvio padrão dos dias adiantados em relação ao real')
    ax.set_xlabel('Limites de infecção (Km)')
    ax.set_ylabel('Dias (unidades)')
    column_to_show = 'days_error_std_total'

    remaining_harvests = [h for h in all_harversts if h != harvest]

    cgnt_harvest = CGNT_DATA[CGNT_DATA['test_file'] == f'coletoressafra{harvest}_31_23']
    cgt_harvest = CGT_DATA[CGT_DATA['test_file'] == f'coletoressafra{harvest}_31_23']
    mg_harvest = MG_DATA[MG_DATA['test_file'] == f'coletoressafra{harvest}_31_23']
    tg_harvest = TG_DATA[TG_DATA['test_file'] == f'coletoressafra{harvest}_31_23']

    cgnt_harvest_mode = cgnt_harvest[cgnt_harvest['train_file'] == f'{mode}_31_23']
    cgt_harvest_a = cgt_harvest[cgt_harvest['train_file'] == f'coletoressafra{remaining_harvests[0]}_31_23']
    cgt_harvest_b = cgt_harvest[cgt_harvest['train_file'] == f'coletoressafra{remaining_harvests[1]}_31_23']
    mg_harvest_mode = mg_harvest[mg_harvest['train_file'] == f'{mode}_31_23']
    tg_harvest_mode = tg_harvest[tg_harvest['train_file'] == f'{mode}_31_23']

    
    ax.plot(cgnt_harvest_mode['radius'], cgnt_harvest_mode[column_to_show], 'o--', label='CGNT', color='red', markersize=10, markeredgecolor='black')
    ax.plot(mg_harvest_mode['radius'], mg_harvest_mode[column_to_show], '^--', label='MG', color='green', markersize=10, markeredgecolor='black')
    ax.plot(tg_harvest_mode['radius'], tg_harvest_mode[column_to_show], '*--', label='TG', color='purple', markersize=10, markeredgecolor='black')
    ax.plot(cgt_harvest_a['radius'], cgt_harvest_a[column_to_show], 'D--', label=f'CGT 4-primeiros da colheita {remaining_harvests[0]}', color='brown', markersize=10, markeredgecolor='black')
    ax.plot(cgt_harvest_b['radius'], cgt_harvest_b[column_to_show], 'p--', label=f'CGT 4-primeiros da colheita {remaining_harvests[1]}', color='blue', markersize=10, markeredgecolor='black')
    ax.axhline(y=0, color='grey', linestyle='--')

    ax.legend()

    plt.tight_layout()

    plt.savefig(rf'G:/My Drive/IC/Codes/Results/Growth_tests/defined_bases/all_vs_all/test_comparison_{mode}_{harvest}_{column_to_show}.png', dpi=300, bbox_inches='tight')