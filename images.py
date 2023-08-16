import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset

info_CGT = pd.read_csv('G:/My Drive/IC/Codes/Results/Search_for_parameter/results_Circular_Growth_no_touch.csv', sep=',', decimal='.')

info_CGT = info_CGT.drop(columns=['RAI','RPC','Test time', 'Test duration', 'Distance function', 'Days function'])

valid = info_CGT.query('FNP == 0')

valid = valid.sort_values(by=['Base'])

# Plot with lines and dots

# plt.plot(valid['Base'], valid['TPP'], 'o', color='black')
# plt.plot(valid['Base'], valid['FPP'], 'o', color='red')

plt.plot(valid['Base'], valid['TPP'], 'o', color='black')
plt.plot(valid['Base'], valid['FPP'], 'o', color='red')

plt.xlabel('Base')
plt.ylabel('TPP/FPP')
plt.legend(['TPP', 'FPP'])

plt.show()