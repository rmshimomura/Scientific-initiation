import matplotlib.pyplot as plt
import pandas as pd

method = 'MG'

# Importing the dataset
info = pd.read_csv(f'G:/My Drive/IC/Codes/results_{method}.csv', sep=',', decimal='.')

valid = info.sort_values(by=['Base'])

fig = plt.figure(figsize=(1920/100, 1080/100))

_2021 = valid[valid['Test file used'] == "coletoressafra2021_31_23"]
_2122 = valid[valid['Test file used'] == "coletoressafra2122_31_23"]
_2223 = valid[valid['Test file used'] == "coletoressafra2223_31_23"]

# Plotting points and connecting lines for 2021 data
plt.plot(_2021['Base'], _2021['TPP'], 'o-', color='black', label='2021 TPP', markersize=10)
plt.plot(_2021['Base'], _2021['FPP'], '*-', color='black', label='2021 FPP', markersize=10)
# If any values on the column 'FNP' are not zero, plot only the values that are not zero
if _2021['FNP'].any() != 0:
    
    non_zero_points = _2021['FNP'].ne(0)
    plt.plot(_2021['Base'][non_zero_points], _2021['FNP'][non_zero_points], '^-', color='black', label='2021 FNP', markersize=10)

# Plotting points and connecting lines for 2122 data
plt.plot(_2122['Base'], _2122['TPP'], 'D-', color='red', label='2122 TPP', markersize=10)
plt.plot(_2122['Base'], _2122['FPP'], 's-', color='red', label='2122 FPP', markersize=10)
# If any values on the column 'FNP' are not zero, plot them
if _2122['FNP'].any() != 0:

    non_zero_points = _2122['FNP'].ne(0)
    plt.plot(_2122['Base'][non_zero_points], _2122['FNP'][non_zero_points], 'v-', color='red', label='2122 FNP', markersize=10)


# Plotting points and connecting lines for 2223 data
plt.plot(_2223['Base'], _2223['TPP'], 'H-', color='blue', label='2223 TPP', markersize=10)
plt.plot(_2223['Base'], _2223['FPP'], 'p-', color='blue', label='2223 FPP', markersize=10)
# If any values on the column 'FNP' are not zero, plot them
if _2223['FNP'].any() != 0:
    
    non_zero_points = _2223['FNP'].ne(0)
    plt.plot(_2223['Base'][non_zero_points], _2223['FNP'][non_zero_points], 'X-', color='blue', label='2223 FNP', markersize=10)

plt.xlabel('Base')
plt.ylabel('TPP/FPP')
plt.title(f'Parameter search for {method} method')

# Creating a legend for the colors
color_legend = plt.legend(loc='upper right', frameon=True)

# Adding the first legend back to the axes
plt.gca().add_artist(color_legend)

# plt.yscale('log')

fig.savefig(f'G:/My Drive/IC/Codes/Images/{method}_parameter_search.png', dpi=300, bbox_inches='tight')
