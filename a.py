import pandas as pd
import matplotlib.pyplot as plt

cgnt_data = pd.read_csv('results_CGNT.csv', sep=',', decimal='.')
mg_data = pd.read_csv('results_MG.csv', sep=',', decimal='.')

cgnt_data.sort_values(by=['Radius'], inplace=True)
mg_data.sort_values(by=['Radius'], inplace=True)

cgnt_data_2021 = cgnt_data[cgnt_data['Test file used'] == 'coletoressafra2021_31_23']
cgnt_data_2122 = cgnt_data[cgnt_data['Test file used'] == 'coletoressafra2122_31_23']
cgnt_data_2223 = cgnt_data[cgnt_data['Test file used'] == 'coletoressafra2223_31_23']

mg_data_2021 = mg_data[mg_data['Test file used'] == 'coletoressafra2021_31_23']
mg_data_2122 = mg_data[mg_data['Test file used'] == 'coletoressafra2122_31_23']
mg_data_2223 = mg_data[mg_data['Test file used'] == 'coletoressafra2223_31_23']

fig = plt.figure(figsize=(10, 6))

# plt.plot(cgnt_data_2021['Radius'], cgnt_data_2021['TPP'], '*-', label='CGNT-TPP-2021', markersize=10)
# plt.plot(cgnt_data_2122['Radius'], cgnt_data_2122['TPP'], '*-', label='CGNT-TPP-2122', markersize=10)
plt.plot(cgnt_data_2223['Radius'], cgnt_data_2223['TPP'], '*-', label='CGNT-TPP-2223', markersize=10)

# plt.plot(mg_data_2021['Radius'], mg_data_2021['TPP'], '^--', label='MG-TPP-2021', markersize=10)
# plt.plot(mg_data_2122['Radius'], mg_data_2122['TPP'], '^--', label='MG-TPP-2122', markersize=10)
plt.plot(mg_data_2223['Radius'], mg_data_2223['TPP'], '^--', label='MG-TPP-2223', markersize=10)

# plt.plot(cgnt_data_2021['Radius'], cgnt_data_2021['FPP'], 'o-', label='CGNT-FPP-2021')
# plt.plot(cgnt_data_2122['Radius'], cgnt_data_2122['FPP'], 'o-', label='CGNT-FPP-2122')
plt.plot(cgnt_data_2223['Radius'], cgnt_data_2223['FPP'], 'o-', label='CGNT-FPP-2223')

# plt.plot(mg_data_2021['Radius'], mg_data_2021['FPP'], 'o--', label='MG-FPP-2021')
# plt.plot(mg_data_2122['Radius'], mg_data_2122['FPP'], 'o--', label='MG-FPP-2122')
plt.plot(mg_data_2223['Radius'], mg_data_2223['FPP'], 'o--', label='MG-FPP-2223')

plt.xlabel('Max radius (km)')
plt.ylabel('Penalty')

plt.title('Penalties:\nCircular Growth Touch vs Mixed Growth (2223)')

plt.legend()
fig.savefig('CGNT_VS_MG_penalties_2223.png', dpi=300, bbox_inches='tight')