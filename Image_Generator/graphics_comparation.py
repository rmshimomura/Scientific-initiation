import pandas as pd
import matplotlib.pyplot as plt

cgnt_results = pd.read_csv('G:/Meu Drive/IC/Codes/Results/Growth_tests/CGNT.csv')
mg_results = pd.read_csv('G:/Meu Drive/IC/Codes/Results/Growth_tests/MG.csv')

cgnt_results.sort_values(by=['base'], inplace=True)
mg_results.sort_values(by=['base'], inplace=True)

cgnt_data_2021 = cgnt_results[cgnt_results['test_file'] == "coletoressafra2021_31_23"]
cgnt_geom_2021 = cgnt_data_2021[cgnt_data_2021['train_file'] == "geometric_mean_31_23"]
cgnt_arit_2021 = cgnt_data_2021[cgnt_data_2021['train_file'] == "arithmetic_mean_31_23"]
cgnt_har_2021 = cgnt_data_2021[cgnt_data_2021['train_file'] == "harmonic_mean_31_23"]
cgnt_data_2122 = cgnt_results[cgnt_results['test_file'] == "coletoressafra2122_31_23"]
cgnt_geom_2122 = cgnt_data_2122[cgnt_data_2122['train_file'] == "geometric_mean_31_23"]
cgnt_arit_2122 = cgnt_data_2122[cgnt_data_2122['train_file'] == "arithmetic_mean_31_23"]
cgnt_har_2122 = cgnt_data_2122[cgnt_data_2122['train_file'] == "harmonic_mean_31_23"]
cgnt_data_2223 = cgnt_results[cgnt_results['test_file'] == "coletoressafra2223_31_23"]
cgnt_geom_2223 = cgnt_data_2223[cgnt_data_2223['train_file'] == "geometric_mean_31_23"]
cgnt_arit_2223 = cgnt_data_2223[cgnt_data_2223['train_file'] == "arithmetic_mean_31_23"]
cgnt_har_2223 = cgnt_data_2223[cgnt_data_2223['train_file'] == "harmonic_mean_31_23"]

mg_data_2021 = mg_results[mg_results['test_file'] == "coletoressafra2021_31_23"]
mg_geom_2021 = mg_data_2021[mg_data_2021['train_file'] == "geometric_mean_31_23"]
mg_arit_2021 = mg_data_2021[mg_data_2021['train_file'] == "arithmetic_mean_31_23"]
mg_har_2021 = mg_data_2021[mg_data_2021['train_file'] == "harmonic_mean_31_23"]
mg_data_2122 = mg_results[mg_results['test_file'] == "coletoressafra2122_31_23"]
mg_geom_2122 = mg_data_2122[mg_data_2122['train_file'] == "geometric_mean_31_23"]
mg_arit_2122 = mg_data_2122[mg_data_2122['train_file'] == "arithmetic_mean_31_23"]
mg_har_2122 = mg_data_2122[mg_data_2122['train_file'] == "harmonic_mean_31_23"]
mg_data_2223 = mg_results[mg_results['test_file'] == "coletoressafra2223_31_23"]
mg_geom_2223 = mg_data_2223[mg_data_2223['train_file'] == "geometric_mean_31_23"]
mg_arit_2223 = mg_data_2223[mg_data_2223['train_file'] == "arithmetic_mean_31_23"]
mg_har_2223 = mg_data_2223[mg_data_2223['train_file'] == "harmonic_mean_31_23"]


plt.figure(figsize=(10, 5))
plt.axhline(y=0, color='black', linestyle='--')
plt.title('CGNT (no touch) vs MG (touch) - 2223 - Arith')
plt.plot(cgnt_arit_2223['base'], cgnt_arit_2223['days_error_mean_total'], 'o-', label='CGNT_mean', markersize=10)
plt.plot(cgnt_arit_2223['base'], cgnt_arit_2223['days_error_std_total'], '*-', label='CGNT_std', markersize=10)
plt.plot(mg_arit_2223['base'], mg_arit_2223['days_error_mean_total'], 'D--', label='MG_mean', markersize=10)
plt.plot(mg_arit_2223['base'], mg_arit_2223['days_error_std_total'], '^--', label='MG_std', markersize=10)
plt.xlabel('Base')
plt.ylabel('Mean total error (days)')
plt.legend()
plt.show()