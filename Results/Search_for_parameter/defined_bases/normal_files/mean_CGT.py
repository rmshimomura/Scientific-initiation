import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

cgt_data = pd.read_csv(r'G:\My Drive\IC\Codes\Results\Search_for_parameter\defined_bases\normal_files\results_CGT.csv', decimal='.', sep=',')

cgt_data = cgt_data.drop(columns=['Distance function', 'Days function', 'Train file used'])

# Set all values on TPP and FPP column that are zero 10 1e-10
cgt_data['TPP'] = cgt_data['TPP'].replace(0, 1e-10)
cgt_data['FPP'] = cgt_data['FPP'].replace(0, 1e-10)
cgt_data['FNP'] = cgt_data['FNP'].replace(0, 1e-10)

harvestA = cgt_data[cgt_data['Test file used'] == 'coletoressafra2021_31_23']
harvestB = cgt_data[cgt_data['Test file used'] == 'coletoressafra2122_31_23']
harvestC = cgt_data[cgt_data['Test file used'] == 'coletoressafra2223_31_23']

harvestA = harvestA.query('Radius >= 55')
harvestB = harvestB.query('Radius >= 55')
harvestC = harvestC.query('Radius >= 55')

print(harvestA)

# fig, ax = plt.subplots(figsize=(12, 6))

# ax.plot(harvestA['Radius'], harvestA['TPP'], 'o-', label=f'Colheita A TPP', color='red', markersize=10)
# ax.plot(harvestA['Radius'], harvestA['FPP'], '^-', label=f'Colheita A FPP', color='red', markersize=10)
# # ax.plot(harvestA['Radius'], harvestA['FNP'], '*-', label=f'Colheita A FNP', color='red', markersize=10)
# ax.plot(harvestB['Radius'], harvestB['TPP'], 'o-', label=f'Colheita B TPP', color='blue', markersize=10)
# ax.plot(harvestB['Radius'], harvestB['FPP'], '^-', label=f'Colheita B FPP', color='blue', markersize=10)
# # ax.plot(harvestB['Radius'], harvestB['FNP'], '*-', label=f'Colheita B FNP', color='blue', markersize=10)
# ax.plot(harvestC['Radius'], harvestC['TPP'], 'o-', label=f'Colheita C TPP', color='green', markersize=10)
# ax.plot(harvestC['Radius'], harvestC['FPP'], '^-', label=f'Colheita C FPP', color='green', markersize=10)
# # ax.plot(harvestC['Radius'], harvestC['FNP'], '*-', label=f'Colheita C FNP', color='green', markersize=10)

# ax.set_title(f'Comparação entre as colheitas A, B e C - CGT - Penalidade TPP e FPP - apenas válidos')
# ax.set_xlabel('Limites de infecção (Km)')
# ax.set_ylabel('Penalidade (RMSE)')
# ax.legend()
# ax.set_xticks(np.arange(55, 65, 5))
# # ax.set_yscale('log')

# plt.tight_layout()

# # Save the plot on a wide version
# plt.savefig(f'G:/My Drive/IC/Codes/Results/Search_for_parameter/defined_bases/normal_files/CGT_TPP_FPP_apenas_validos.png', dpi=300, bbox_inches='tight')