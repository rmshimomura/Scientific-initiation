import pandas as pd
import matplotlib.pyplot as plt


df2021 = pd.read_csv('./Data/Gridded_Data/Test_Data/coletoressafra2021_31_23.csv', sep=',', decimal='.', encoding='utf-8')
df2122 = pd.read_csv('./Data/Gridded_Data/Test_Data/coletoressafra2122_31_23.csv', sep=',', decimal='.', encoding='utf-8')
df2223 = pd.read_csv('./Data/Gridded_Data/Test_Data/coletoressafra2223_31_23.csv', sep=',', decimal='.', encoding='utf-8')

# Print a plot of the data, as points where x is the index and y is the column 'DiasAposInicioCiclo'

df2021 = df2021.query('DiasAposInicioCiclo != -1')
df2021 = df2021.sort_values(by=['DiasAposInicioCiclo'])
df2021.index = range(len(df2021))

df2122 = df2122.query('DiasAposInicioCiclo != -1')
df2122 = df2122.sort_values(by=['DiasAposInicioCiclo'])
df2122.index = range(len(df2122))

df2223 = df2223.query('DiasAposInicioCiclo != -1')
df2223 = df2223.sort_values(by=['DiasAposInicioCiclo'])
df2223.index = range(len(df2223))

plt.plot(df2021.index, df2021['DiasAposInicioCiclo'], 'o-', color='red')
plt.plot(df2122.index, df2122['DiasAposInicioCiclo'], '*-', color='green', markersize=10)
plt.plot(df2223.index, df2223['DiasAposInicioCiclo'], '^-', color='blue')
plt.legend(['2021', '2122', '2223'])
plt.title('Detecção dos esporos nos coletores em cada safra')
plt.xlabel('Número de coletores que detectaram esporos')
plt.ylabel('Dias após o início do ciclo')
plt.show()