import pandas as pd
import matplotlib.pyplot as plt

CGNT_DATA = pd.read_csv('CGNT.csv')
CGT_DATA = pd.read_csv('CGT.csv')
MG_DATA = pd.read_csv('MG.csv')

cgnt_test_2021 = CGNT_DATA[CGNT_DATA['test_file'] == 'coletoressafra2021_31_23']

harmonic_test_2021 = cgnt_test_2021[cgnt_test_2021['train_file'] == 'harmonic_mean_31_23']
geometric_test_2021 = cgnt_test_2021[cgnt_test_2021['train_file'] == 'geometric_mean_31_23']
arithmetic_test_2021 = cgnt_test_2021[cgnt_test_2021['train_file'] == 'arithmetic_mean_31_23']

cgnt_test_2122 = CGNT_DATA[CGNT_DATA['test_file'] == 'coletoressafra2122_31_23']

harmonic_test_2122 = cgnt_test_2122[cgnt_test_2122['train_file'] == 'harmonic_mean_31_23']
geometric_test_2122 = cgnt_test_2122[cgnt_test_2122['train_file'] == 'geometric_mean_31_23']
arithmetic_test_2122 = cgnt_test_2122[cgnt_test_2122['train_file'] == 'arithmetic_mean_31_23']

cgnt_test_2223 = CGNT_DATA[CGNT_DATA['test_file'] == 'coletoressafra2223_31_23']

harmonic_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'harmonic_mean_31_23']
geometric_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'geometric_mean_31_23']
arithmetic_test_2223 = cgnt_test_2223[cgnt_test_2223['train_file'] == 'arithmetic_mean_31_23']

# fig, axs = plt.subplots(1, 3, figsize=(12, 6))  # Adjust figsize as needed

# Boxplot for arithmetic data
plt.boxplot([
    arithmetic_test_2021['days_error_mean_total'],
    arithmetic_test_2021['days_error_std_total'],
    geometric_test_2021['days_error_mean_total'],
    geometric_test_2021['days_error_std_total'],
    harmonic_test_2021['days_error_mean_total'],
    harmonic_test_2021['days_error_std_total']
], labels=['arithmetic_mean_error', 'arithmetic_std_error', 'geometric_mean_error', 'geometric_std_error', 'harmonic_mean_error', 'harmonic_std_error'])

plt.title('Harvest of 2021')
plt.axhline(y=0, color='grey', linestyle='--')
plt.tight_layout()
plt.show()