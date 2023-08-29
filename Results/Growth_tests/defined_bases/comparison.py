import pandas as pd
import matplotlib.pyplot as plt

CGNT_DATA = pd.read_csv('CGNT.csv')
CGT_DATA = pd.read_csv('CGT.csv')
MG_DATA = pd.read_csv('MG.csv')

# fig, axs = plt.subplots(1, 3, figsize=(10, 10))

cgnt_test_2223 = CGNT_DATA[CGNT_DATA['test_file'] == 'coletoressafra2223_31_23']

harmonic_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'harmonic_mean_31_23']
geometric_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'geometric_mean_31_23']
arithmetic_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'arithmetic_mean_31_23']

plt.plot(harmonic_test_2223['radius'], harmonic_test_2223['days_error_mean_total'], 'o-', label='harmonic_mean_error', markersize=8, color='red')
plt.plot(harmonic_test_2223['radius'], harmonic_test_2223['days_error_std_total'], 'o--', label='harmonic_std_error', markersize=8, color='red')
plt.plot(geometric_test_2223['radius'], geometric_test_2223['days_error_mean_total'], '*-', label='geometric_mean_error', markersize=8, color='blue')
plt.plot(geometric_test_2223['radius'], geometric_test_2223['days_error_std_total'], '*--', label='geometric_std_error', markersize=8, color='blue')
plt.plot(arithmetic_test_2223['radius'], arithmetic_test_2223['days_error_mean_total'], '^-', label='arithmetic_mean_error', markersize=8, color='green')
plt.plot(arithmetic_test_2223['radius'], arithmetic_test_2223['days_error_std_total'], '^--', label='arithmetic_std_error', markersize=8, color='green')

# Put vertical lines on each x value
for x in harmonic_test_2223['radius']:
    # Put 0.3 opacity grey lines
    plt.axvline(x=x, color='grey', linestyle='--', alpha=0.3)

plt.title('CGNT - Harvest of 2223')
plt.xlabel('Radius')
plt.ylabel('Days error')
plt.axhline(y=0, color='black', linestyle='-')
plt.legend()

cgnt_test_2223.sort_values(by=['days_error_std_total'], inplace=True)

# print(cgnt_test_2021['train_file'].head(5))

# axs[0].plot(harmonic_test_2021['radius'], harmonic_test_2021['days_error_mean_total'], 'o-', label='harmonic_mean_error', markersize=8)
# axs[0].plot(harmonic_test_2021['radius'], harmonic_test_2021['days_error_std_total'], 'o--', label='harmonic_std_error', markersize=8)
# axs[0].plot(geometric_test_2021['radius'], geometric_test_2021['days_error_mean_total'], '*-', label='geometric_mean_error', markersize=8)
# axs[0].plot(geometric_test_2021['radius'], geometric_test_2021['days_error_std_total'], '*--', label='geometric_std_error', markersize=8)
# axs[0].plot(arithmetic_test_2021['radius'], arithmetic_test_2021['days_error_mean_total'], '^-', label='arithmetic_mean_error', markersize=8)
# axs[0].plot(arithmetic_test_2021['radius'], arithmetic_test_2021['days_error_std_total'], '^--', label='arithmetic_std_error', markersize=8)

# axs[0].set_title('Harvest of 2021')
# axs[0].set_xlabel('Radius')
# axs[0].set_ylabel('Days error')
# axs[0].axhline(y=0, color='grey', linestyle='--')
# axs[0].legend()


# cgnt_test_2122 = CGNT_DATA[CGNT_DATA['test_file'] == 'coletoressafra2122_31_23']

# harmonic_test_2122 = cgnt_test_2122[cgnt_test_2122['train_file'] == 'harmonic_mean_31_23']
# geometric_test_2122 = cgnt_test_2122[cgnt_test_2122['train_file'] == 'geometric_mean_31_23']
# arithmetic_test_2122 = cgnt_test_2122[cgnt_test_2122['train_file'] == 'arithmetic_mean_31_23']

# axs[1].plot(harmonic_test_2122['radius'], harmonic_test_2122['days_error_mean_total'], 'o-', label='harmonic_mean_error', markersize=8)
# axs[1].plot(harmonic_test_2122['radius'], harmonic_test_2122['days_error_std_total'], 'o--', label='harmonic_std_error', markersize=8)
# axs[1].plot(geometric_test_2122['radius'], geometric_test_2122['days_error_mean_total'], '*-', label='geometric_mean_error', markersize=8)
# axs[1].plot(geometric_test_2122['radius'], geometric_test_2122['days_error_std_total'], '*--', label='geometric_std_error', markersize=8)
# axs[1].plot(arithmetic_test_2122['radius'], arithmetic_test_2122['days_error_mean_total'], '^-', label='arithmetic_mean_error', markersize=8)
# axs[1].plot(arithmetic_test_2122['radius'], arithmetic_test_2122['days_error_std_total'], '^--', label='arithmetic_std_error', markersize=8)

# axs[1].set_title('Harvest of 2122')
# axs[1].set_xlabel('Radius')
# axs[1].set_ylabel('Days error')
# axs[1].axhline(y=0, color='grey', linestyle='--')
# axs[1].legend()

# cgnt_test_2223 = CGNT_DATA[CGNT_DATA['test_file'] == 'coletoressafra2223_31_23']

# harmonic_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'harmonic_mean_31_23']
# geometric_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'geometric_mean_31_23']
# arithmetic_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'arithmetic_mean_31_23']

# axs[2].plot(harmonic_test_2223['radius'], harmonic_test_2223['days_error_mean_total'], 'o-', label='harmonic_mean_error', markersize=8)
# axs[2].plot(harmonic_test_2223['radius'], harmonic_test_2223['days_error_std_total'], 'o--', label='harmonic_std_error', markersize=8)
# axs[2].plot(geometric_test_2223['radius'], geometric_test_2223['days_error_mean_total'], '*-', label='geometric_mean_error', markersize=8)
# axs[2].plot(geometric_test_2223['radius'], geometric_test_2223['days_error_std_total'], '*--', label='geometric_std_error', markersize=8)
# axs[2].plot(arithmetic_test_2223['radius'], arithmetic_test_2223['days_error_mean_total'], '^-', label='arithmetic_mean_error', markersize=8)
# axs[2].plot(arithmetic_test_2223['radius'], arithmetic_test_2223['days_error_std_total'], '^--', label='arithmetic_std_error', markersize=8)

# axs[2].set_title('Harvest of 2223')
# axs[2].set_xlabel('Radius')
# axs[2].set_ylabel('Days error')
# axs[2].axhline(y=0, color='grey', linestyle='--')
# axs[2].legend()

# fig.suptitle('Comparison of CGNT data with different means', fontsize=16)
# plt.tight_layout()
plt.show()