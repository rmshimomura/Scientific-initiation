import pandas as pd
import matplotlib.pyplot as plt

cgnt_test_data = pd.read_csv('G:/My Drive/IC/Codes/Results/Growth_tests/CGNT.csv', sep=',', decimal='.')

cgnt_test_data = cgnt_test_data.sort_values(by=['base'])

data_2021 = cgnt_test_data[cgnt_test_data['test_file'] == "coletoressafra2021_31_23"]

geom_2021 = data_2021[data_2021['train_file'] == "geometric_mean_31_23"]
arit_2021 = data_2021[data_2021['train_file'] == "arithmetic_mean_31_23"]
har_2021 = data_2021[data_2021['train_file'] == "harmonic_mean_31_23"]

data_2122 = cgnt_test_data[cgnt_test_data['test_file'] == "coletoressafra2122_31_23"]

geom_2122 = data_2122[data_2122['train_file'] == "geometric_mean_31_23"]
arit_2122 = data_2122[data_2122['train_file'] == "arithmetic_mean_31_23"]
har_2122 = data_2122[data_2122['train_file'] == "harmonic_mean_31_23"]

data_2223 = cgnt_test_data[cgnt_test_data['test_file'] == "coletoressafra2223_31_23"]

geom_2223 = data_2223[data_2223['train_file'] == "geometric_mean_31_23"]
arit_2223 = data_2223[data_2223['train_file'] == "arithmetic_mean_31_23"]
har_2223 = data_2223[data_2223['train_file'] == "harmonic_mean_31_23"]


arit_2223 = arit_2223.reindex(arit_2223['days_error_mean_total'].abs().sort_values().index)
best_mean_2223 = arit_2223[['base', 'days_error_mean_total', 'days_error_std_total']].head(10)

arit_2223 = arit_2223.reindex(arit_2223['days_error_std_total'].abs().sort_values().index)
best_std_2223 = arit_2223[['base', 'days_error_mean_total', 'days_error_std_total']].head(10)

fig1, ax1 = plt.subplots(figsize=(8,6))
ax1.axis('off')

fig2, ax2 = plt.subplots(figsize=(8,6))
ax2.axis('off')

table_mean = []
table_std = []

for i in range(10):
    table_mean.append([best_mean_2223.iloc[i]['base'], best_mean_2223.iloc[i]['days_error_mean_total'], best_mean_2223.iloc[i]['days_error_std_total']])
    table_std.append([best_std_2223.iloc[i]['base'], best_std_2223.iloc[i]['days_error_mean_total'], best_std_2223.iloc[i]['days_error_std_total']])

ax1.table(cellText=table_mean, colLabels=['Base', 'Mean error', 'Std error'], loc='center')
ax1.set_title('Best results for 2223 data considering days error mean using CGNT method with arithmetic mean')
fig1.savefig('table_CGNT_arit_2223_best_mean.png', dpi=300, bbox_inches='tight')

ax2.table(cellText=table_std, colLabels=['Base', 'Mean error', 'Std error'], loc='center')
ax2.set_title('Best results for 2223 data considering days error std using CGNT method with arithmetic mean')
fig2.savefig('table_CGNT_arit_2223_best_std.png', dpi=300, bbox_inches='tight')

# fig = plt.figure(figsize=(1920/100, 1080/100))
# plt.xlabel('Base')
# plt.ylabel('Days error')
# plt.xticks(data_2223['base'])
# # Put vertical lines on the x axis
# x_values = data_2223['base']
# for x in x_values:
#     plt.axvline(x=x, color='grey', linestyle='--', linewidth=0.5)

# plt.axhline(y=0, color='black', linestyle='--')
# plt.title('MG method using harmonic mean - for 2223 data')
# plt.plot(har_2223['base'], har_2223['days_error_mean_total'], 'o-', color='black', label='Mean error', markersize=10)
# plt.plot(har_2223['base'], har_2223['days_error_std_total'], '*-', color='blue', label='Std error', markersize=10)
# plt.legend(loc='upper right', frameon=True)
# fig.savefig('G:/My Drive/IC/Codes/Images/MG_har_2223.png', dpi=300, bbox_inches='tight')
# # plt.show()