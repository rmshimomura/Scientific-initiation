import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_csv('./Results/Search_for_parameter/results_CGT.csv', sep=',', decimal='.')

data.sort_values(by=['number_of_starting_points'], inplace=True)

data = data[data['Base'] == 9310.188000000004]

data_2021 = data[data['Test file used'] == 'coletoressafra2021_31_23']
data_2122 = data[data['Test file used'] == 'coletoressafra2122_31_23']
data_2223 = data[data['Test file used'] == 'coletoressafra2223_31_23']

fig = plt.figure(figsize=(1920/100, 1080/100))

plt.plot(data_2021['number_of_starting_points'], data_2021['TPP'], '*-.', label='TPP-2021', markersize=10)
plt.plot(data_2122['number_of_starting_points'], data_2122['TPP'], '*-.', label='TPP-2122', markersize=10)
plt.plot(data_2223['number_of_starting_points'], data_2223['TPP'], '*-.', label='TPP-2223', markersize=10, color='black')

plt.plot(data_2021['number_of_starting_points'], data_2021['FPP'], 'o-', label='FPP-2021')
plt.plot(data_2122['number_of_starting_points'], data_2122['FPP'], 'o-', label='FPP-2122')
plt.plot(data_2223['number_of_starting_points'], data_2223['FPP'], 'o-', label='FPP-2223')

plt.plot(data_2021['number_of_starting_points'], data_2021['FNP'], 'o--', label='FNP-2021')
plt.plot(data_2122['number_of_starting_points'], data_2122['FNP'], 'o--', label='FNP-2122')
plt.plot(data_2223['number_of_starting_points'], data_2223['FNP'], 'o--', label='FNP-2223', color='darkblue')

plt.xlabel('Number of starting points')
plt.ylabel('Penalty')

plt.title('Circular Growth Touch - Max radius of 60km')

plt.plot([3], [0], 'o', color='red', fillstyle='none', markersize=25, markeredgewidth=3)
plt.annotate('Point where all collectors\nhave been found (FNP == 0)', xy=(3, 0), xytext=(3, 20), arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='center', verticalalignment='top')
plt.axvspan(3.9, 4.1, alpha=0.3, color='red', hatch='//')
plt.annotate('Chosen k', xy=(4.1, 10), xytext=(5, 10.7), arrowprops=dict(facecolor='black', shrink=0.05), horizontalalignment='center', verticalalignment='top')

plt.legend()
fig.savefig('./Results/Search_for_parameter/CGT_results.png', dpi=100, bbox_inches='tight')