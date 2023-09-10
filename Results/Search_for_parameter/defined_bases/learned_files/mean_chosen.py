import pandas as pd
import matplotlib.pyplot as plt

CGNT = pd.read_csv(r'G:/My Drive/IC/Codes/Results/Search_for_parameter/defined_bases/learned_files/results_CGNT.csv'.replace('//', '/'))
MG = pd.read_csv(r'G:/My Drive/IC/Codes/Results/Search_for_parameter/defined_bases/learned_files/results_MG.csv'.replace('//', '/'))
TG = pd.read_csv(r'G:/My Drive/IC/Codes/Results/Search_for_parameter/defined_bases/learned_files/results_TG.csv'.replace('//', '/'))

arit = MG[MG['Test file used'] == 'arithmetic_mean_31_23']
geom = MG[MG['Test file used'] == 'geometric_mean_31_23']
harm = MG[MG['Test file used'] == 'harmonic_mean_31_23']

# Create a figure and plot the data on it
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(arit['Radius'], arit['TPP'], 'o-', label=f'Média aritmética TPP', color='red', markersize=10)
ax.plot(arit['Radius'], arit['FPP'], '^-', label=f'Média aritmética FPP', color='red', markersize=10)
ax.plot(arit['Radius'], arit['FNP'], '*-', label=f'Média aritmética FNP', color='red', markersize=10)
ax.plot(geom['Radius'], geom['TPP'], 'o-', label=f'Média geométrica TPP', color='blue', markersize=10)
ax.plot(geom['Radius'], geom['FPP'], '^-', label=f'Média geométrica FPP', color='blue', markersize=10)
ax.plot(geom['Radius'], geom['FNP'], '*-', label=f'Média geométrica FNP', color='blue', markersize=10)
ax.plot(harm['Radius'], harm['TPP'], 'o-', label=f'Média harmônica TPP', color='green', markersize=10)
ax.plot(harm['Radius'], harm['FPP'], '^-', label=f'Média harmônica FPP', color='green', markersize=10)
ax.plot(harm['Radius'], harm['FNP'], '*-', label=f'Média harmônica FNP', color='green', markersize=10)

ax.set_title(f'Comparação entre as médias aritmética, geométrica e harmônica - MG')
ax.set_xlabel('Limites de infecção (Km)')
ax.set_ylabel('Penalidade (RMSE)')
ax.legend()

plt.tight_layout()

# Save the plot on a wide version
plt.savefig(f'G:/My Drive/IC/Codes/Results/Search_for_parameter/defined_bases/learned_files/means_comparison_MG.png', dpi=300, bbox_inches='tight')