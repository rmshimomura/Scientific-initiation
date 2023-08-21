import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
info_CGT = pd.read_csv('G:/My Drive/IC/Codes/results_CGNT.csv', sep=',', decimal='.')

valid = info_CGT.sort_values(by=['Base'])

_2021 = valid[valid['Test file used'] == "coletoressafra2021_31_23"]
_2122 = valid[valid['Test file used'] == "coletoressafra2122_31_23"]
_2223 = valid[valid['Test file used'] == "coletoressafra2223_31_23"]

# Plotting points and connecting lines for 2021 data
plt.plot(_2021['Base'], _2021['TPP'], 'o-', color='black', label='2021 TPP', markersize=10)
plt.plot(_2021['Base'], _2021['FPP'], '*-', color='black', label='2021 FPP', markersize=10)


# Plotting points and connecting lines for 2122 data
plt.plot(_2122['Base'], _2122['TPP'], 'D-', color='red', label='2122 TPP', markersize=10)
plt.plot(_2122['Base'], _2122['FPP'], 's-', color='red', label='2122 FPP', markersize=10)

# Plotting points and connecting lines for 2223 data
plt.plot(_2223['Base'], _2223['TPP'], 'H-', color='blue', label='2223 TPP', markersize=10)
plt.plot(_2223['Base'], _2223['FPP'], 'p-', color='blue', label='2223 FPP', markersize=10)

plt.xlabel('Base')
plt.ylabel('TPP/FPP')

# Creating a legend for the colors
color_legend = plt.legend(loc='upper right', frameon=True)

# Adding the first legend back to the axes
plt.gca().add_artist(color_legend)

# plt.yscale('log')

plt.show()
