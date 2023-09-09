import pandas as pd
import matplotlib.pyplot as plt

collectors_2021 = pd.read_csv(r'G:\My Drive\IC\Codes\Data\Gridded_Data\Test_Data\coletoressafra2021_31_23.csv')
collectors_2122 = pd.read_csv(r'G:\My Drive\IC\Codes\Data\Gridded_Data\Test_Data\coletoressafra2122_31_23.csv')
collectors_2223 = pd.read_csv(r'G:\My Drive\IC\Codes\Data\Gridded_Data\Test_Data\coletoressafra2223_31_23.csv')

collectors_2021 = collectors_2021.query('DiasAposInicioCiclo != -1')
collectors_2122 = collectors_2122.query('DiasAposInicioCiclo != -1')
collectors_2223 = collectors_2223.query('DiasAposInicioCiclo != -1')

collectors_2021.sort_values(by=['DiasAposInicioCiclo'], inplace=True)
collectors_2122.sort_values(by=['DiasAposInicioCiclo'], inplace=True)
collectors_2223.sort_values(by=['DiasAposInicioCiclo'], inplace=True)

fig, ax = plt.subplots(figsize=(12, 6))

# sequence beggining on 1 up to the number of collectors
xlim_2021 = [i for i in range(1, len(collectors_2021) + 1)]
xlim_2122 = [i for i in range(1, len(collectors_2122) + 1)]
xlim_2223 = [i for i in range(1, len(collectors_2223) + 1)]

ax.plot(xlim_2021, collectors_2021['DiasAposInicioCiclo'], 'o-', label=f'2021', color='red', markersize=5)
ax.plot(xlim_2122, collectors_2122['DiasAposInicioCiclo'], '*-', label=f'2122', color='green', markersize=8)
ax.plot(xlim_2223, collectors_2223['DiasAposInicioCiclo'], '^-', label=f'2223', color='blue', markersize=5)


ax.plot()
ax.set_title(f'Dispersão do número de coletores que detectaram esporos e a quantidade de dias após o início do ciclo')
ax.set_xlabel('Número de coletores')
ax.set_ylabel('Dias após o início do ciclo')
ax.legend()

plt.tight_layout()
plt.savefig(r'G:/My Drive/IC/Codes/Results/Growth_tests/collectors_dispersion.png', dpi=300, bbox_inches='tight')
