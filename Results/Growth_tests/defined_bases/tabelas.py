import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

CGNT_DATA = pd.read_csv(r'G:\Meu Drive\IC\Codes\Results\Growth_tests\defined_bases\CGNT.csv')
CGT_DATA = pd.read_csv(r'G:\Meu Drive\IC\Codes\Results\Growth_tests\defined_bases\CGT.csv')
MG_DATA = pd.read_csv(r'G:\Meu Drive\IC\Codes\Results\Growth_tests\defined_bases\MG.csv')
TG_DATA = pd.read_csv(r'G:\Meu Drive\IC\Codes\Results\Growth_tests\defined_bases\TG.csv')

# Unite all dataframes
ALL_DATA = pd.concat([CGNT_DATA, CGT_DATA, MG_DATA, TG_DATA])
ALL_DATA.reset_index(drop=True, inplace=True)

all_harversts = ['2021', '2122', '2223']
total_collectors = 504
harvests_true_positives = [126,68,98]
harvests_false_positives = [total_collectors - i for i in harvests_true_positives]

harvest = '2223'

ALL_DATA['active'] = 1
all_data_harvest = ALL_DATA.query(f"test_file == 'coletoressafra{harvest}_31_23' and (train_file == 'arithmetic_mean_31_23' or growth_type == 'CGT')")

base_lines = all_data_harvest.query("radius == 20 and growth_type == 'CGNT'")

for row in all_data_harvest.itertuples():
    if row.train_file == 'arithmetic_mean_31_23':
        if row.days_error_mean_total == base_lines.iloc[0].days_error_mean_total and row.days_error_std_total == base_lines.iloc[0].days_error_std_total:
            all_data_harvest.loc[row.Index, 'active'] = 0
    if row.train_file == 'geometric_mean_31_23':
        if row.days_error_mean_total == base_lines.iloc[1].days_error_mean_total and row.days_error_std_total == base_lines.iloc[1].days_error_std_total:
            all_data_harvest.loc[row.Index, 'active'] = 0
    if row.train_file == 'harmonic_mean_31_23':
        if row.days_error_mean_total == base_lines.iloc[2].days_error_mean_total and row.days_error_std_total == base_lines.iloc[2].days_error_std_total:
            all_data_harvest.loc[row.Index, 'active'] = 0

all_data_harvest = all_data_harvest.query("active == 1")

all_data_harvest = all_data_harvest.query('not_detected_with_spores == 0')

all_data_harvest['error_max'] = np.maximum(abs(all_data_harvest['days_error_mean_total'] + all_data_harvest['days_error_std_total']), abs(all_data_harvest['days_error_mean_total'] - all_data_harvest['days_error_std_total']))

chosen_harvest_values = (harvests_true_positives[all_harversts.index(harvest)], harvests_false_positives[all_harversts.index(harvest)])

all_data_harvest['precision'] = all_data_harvest['true_positive'] / (all_data_harvest['true_positive'] + all_data_harvest['false_positive'])
all_data_harvest['recall'] = all_data_harvest['true_positive'] / chosen_harvest_values[0]
all_data_harvest['f1_score'] = 2 * (all_data_harvest['precision'] * all_data_harvest['recall']) / (all_data_harvest['precision'] + all_data_harvest['recall'])
all_data_harvest['accuracy'] = (all_data_harvest['true_positive'] + (total_collectors - chosen_harvest_values[0])) / total_collectors

all_data_harvest = all_data_harvest.sort_values(by=['error_max'], key=abs, ascending=[True])
all_data_harvest = all_data_harvest.round(3)
best_10 = all_data_harvest[['growth_type', 'radius', 'train_file', 'days_error_mean_total', 'days_error_std_total', 'true_positive', 'false_positive', 'error_max','f1_score']].head(10)

print(f"{harvest}\n\n")

print(best_10)
print("=========================================")

# Export to csv best_10
best_10.to_csv(rf'G:\Meu Drive\IC\Codes\Results\Growth_tests\defined_bases\error_max_best_10_{harvest}.csv', index=False)