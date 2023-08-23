import pandas as pd
import matplotlib.pyplot as plt

mg_test_data = pd.read_csv('G:/My Drive/IC/Codes/Results/Growth_tests/MG.csv', sep=',', decimal='.')

mg_test_data = mg_test_data.sort_values(by=['base'])

data_2021 = mg_test_data[mg_test_data['test_file'] == "coletoressafra2021_31_23"]

geom_2021 = data_2021[data_2021['train_file'] == "geometric_mean_31_23"]
arit_2021 = data_2021[data_2021['train_file'] == "arithmetic_mean_31_23"]
har_2021 = data_2021[data_2021['train_file'] == "harmonic_mean_31_23"]

data_2122 = mg_test_data[mg_test_data['test_file'] == "coletoressafra2122_31_23"]

geom_2122 = data_2122[data_2122['train_file'] == "geometric_mean_31_23"]
arit_2122 = data_2122[data_2122['train_file'] == "arithmetic_mean_31_23"]
har_2122 = data_2122[data_2122['train_file'] == "harmonic_mean_31_23"]

data_2223 = mg_test_data[mg_test_data['test_file'] == "coletoressafra2223_31_23"]

geom_2223 = data_2223[data_2223['train_file'] == "geometric_mean_31_23"]
arit_2223 = data_2223[data_2223['train_file'] == "arithmetic_mean_31_23"]
har_2223 = data_2223[data_2223['train_file'] == "harmonic_mean_31_23"]



fig = plt.figure(figsize=(1920/100, 1080/100))
plt.xlabel('Base')
plt.ylabel('Days error')
plt.xticks(data_2223['base'])
# Put vertical lines on the x axis
x_values = data_2223['base']
for x in x_values:
    plt.axvline(x=x, color='grey', linestyle='--', linewidth=0.5)

plt.axhline(y=0, color='black', linestyle='--')
plt.title('MG method using harmonic mean - for 2223 data')
plt.plot(har_2223['base'], har_2223['days_error_mean_total'], 'o-', color='black', label='Mean error', markersize=10)
plt.plot(har_2223['base'], har_2223['days_error_std_total'], '*-', color='blue', label='Std error', markersize=10)
plt.legend(loc='upper right', frameon=True)
fig.savefig('G:/My Drive/IC/Codes/Images/MG_har_2223.png', dpi=300, bbox_inches='tight')
# plt.show()