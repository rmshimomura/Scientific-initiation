# Comandos importantes do Pandas
## O que é?
Pandas é uma biblioteca de análise de dados que fornece estruturas de dados de alto desempenho e fáceis de usar e ferramentas de análise de dados para a linguagem de programação Python.
Ele trabalha com dados do tipo DataFrame, que é uma estrutura de dados bidimensional com colunas de tipos potencialmente diferentes trabalhando com arquivos de diferentes formatos, como csv, excel por exemplo.

## Considere o seguinte código:
```python
import matplotlib.pyplot as plt
import pandas as pd

# Lendo um arquivo csv, especificando qual o separador de colunas e o separador decimal
cgt_data = pd.read_csv(r'G:\My Drive\IC\Codes\Results\Search_for_parameter\defined_bases\normal_files\results_CGT.csv', decimal='.', sep=',')
```

## Mostrando as primeiras linhas do DataFrame
`print(cgt_data.head())`

```
                  Method  Number of Days          Base  Radius            Test file used           TPP  TNP           FPP           FNP  number_of_starting_points
0  Circular Growth touch             137  1.693235e+11      20  coletoressafra2021_31_23  1.000000e-10    0  1.000000e-10  1.032028e+04                          4
1  Circular Growth touch             137  1.693235e+11      20  coletoressafra2122_31_23  1.000000e-10    0  1.000000e-10  7.932991e+06                          4
2  Circular Growth touch             137  1.693235e+11      20  coletoressafra2223_31_23  1.000000e-10    0  1.000000e-10  2.946784e+06                          4
3  Circular Growth touch             137  9.615541e+08      25  coletoressafra2021_31_23  6.254758e+01    0  4.663223e+01  1.268093e+03                          4
4  Circular Growth touch             137  9.615541e+08      25  coletoressafra2122_31_23  6.787857e+01    0  4.680507e+01  2.484843e+05                          4
```

## Mostrando a DataFrame inteiro
`print(cgt_data)`

```
                   Method  Number of Days          Base  Radius            Test file used           TPP  TNP           FPP           FNP  number_of_starting_points
0   Circular Growth touch             137  1.693235e+11      20  coletoressafra2021_31_23  1.000000e-10    0  1.000000e-10  1.032028e+04                          4
1   Circular Growth touch             137  1.693235e+11      20  coletoressafra2122_31_23  1.000000e-10    0  1.000000e-10  7.932991e+06                          4
2   Circular Growth touch             137  1.693235e+11      20  coletoressafra2223_31_23  1.000000e-10    0  1.000000e-10  2.946784e+06                          4
3   Circular Growth touch             137  9.615541e+08      25  coletoressafra2021_31_23  6.254758e+01    0  4.663223e+01  1.268093e+03                          4
4   Circular Growth touch             137  9.615541e+08      25  coletoressafra2122_31_23  6.787857e+01    0  4.680507e+01  2.484843e+05                          4
5   Circular Growth touch             137  9.615541e+08      25  coletoressafra2223_31_23  3.733482e+01    0  4.727975e+01  1.000496e+05                          4
6   Circular Growth touch             137  3.060634e+07      30  coletoressafra2021_31_23  5.463813e+01    0  5.787640e+01  3.365484e+02                          4
7   Circular Growth touch             137  3.060634e+07      30  coletoressafra2122_31_23  4.685517e+01    0  5.388803e+01  9.883293e+03                          4
8   Circular Growth touch             137  3.060634e+07      30  coletoressafra2223_31_23  3.918386e+01    0  5.172604e+01  1.060261e+04                          4
9   Circular Growth touch             137  2.608614e+06      35  coletoressafra2021_31_23  5.696827e+01    0  5.930543e+01  1.761053e+02                          4
10  Circular Growth touch             137  2.608614e+06      35  coletoressafra2122_31_23  3.691041e+01    0  5.695363e+01  2.401994e+03                          4
11  Circular Growth touch             137  2.608614e+06      35  coletoressafra2223_31_23  4.687844e+01    0  5.634826e+01  2.792975e+03                          4
12  Circular Growth touch             137  4.114893e+05      40  coletoressafra2021_31_23  4.687807e+01    0  6.317204e+01  1.099963e+02                          4
13  Circular Growth touch             137  4.114893e+05      40  coletoressafra2122_31_23  3.840373e+01    0  6.520131e+01  1.108652e+03                          4
14  Circular Growth touch             137  4.114893e+05      40  coletoressafra2223_31_23  4.505097e+01    0  5.943411e+01  1.348898e+03                          4
15  Circular Growth touch             137  9.784552e+04      45  coletoressafra2021_31_23  3.942599e+01    0  7.082976e+01  2.508992e+01                          4
16  Circular Growth touch             137  9.784552e+04      45  coletoressafra2122_31_23  3.822802e+01    0  7.188519e+01  5.116174e+02                          4
17  Circular Growth touch             137  9.784552e+04      45  coletoressafra2223_31_23  4.141797e+01    0  6.714242e+01  7.935818e+01                          4
18  Circular Growth touch             137  3.100893e+04      50  coletoressafra2021_31_23  3.266133e+01    0  7.879987e+01  1.000000e-10                          4
19  Circular Growth touch             137  3.100893e+04      50  coletoressafra2122_31_23  4.036654e+01    0  7.691439e+01  7.161798e+00                          4
20  Circular Growth touch             137  3.100893e+04      50  coletoressafra2223_31_23  4.219520e+01    0  7.461690e+01  1.435299e+01                          4
21  Circular Growth touch             137  1.211072e+04      55  coletoressafra2021_31_23  2.856241e+01    0  8.502136e+01  1.000000e-10                          4
22  Circular Growth touch             137  1.211072e+04      55  coletoressafra2122_31_23  4.113792e+01    0  8.246111e+01  1.000000e-10                          4
23  Circular Growth touch             137  1.211072e+04      55  coletoressafra2223_31_23  4.479469e+01    0  8.100197e+01  1.000000e-10                          4
24  Circular Growth touch             137  5.532299e+03      60  coletoressafra2021_31_23  2.736622e+01    0  9.138013e+01  1.000000e-10                          4
25  Circular Growth touch             137  5.532299e+03      60  coletoressafra2122_31_23  4.362572e+01    0  8.682216e+01  1.000000e-10                          4
26  Circular Growth touch             137  5.532299e+03      60  coletoressafra2223_31_23  4.787495e+01    0  8.686268e+01  1.000000e-10                          4
```

## Mostrando as colunas do Dataframe
`print(cgt_data.columns)`

```
Index(['Method', 'Number of Days', 'Base', 'Radius', 'Test file used', 'TPP',
    'TNP', 'FPP', 'FNP', 'number_of_starting_points'],
    dtype='object')
```

## Mostrando o formato do Dataframe (linhas x colunas):
`print(cgt_data.shape)`

```
(27, 10)
```

## Removendo algumas colunas do DataFrame
`cgt_data = cgt_data.drop(columns=['Distance function', 'Days function', 'Train file used'])`

## Alterando valores de uma coluna específica em todas as linhas do Dataframe
`cgt_data['TPP'] = cgt_data['TPP'].replace(0, 1e-10)`

`cgt_data['FPP'] = cgt_data['FPP'].replace(0, 1e-10)`

`cgt_data['FNP'] = cgt_data['FNP'].replace(0, 1e-10)`

## Filtrando o DataFrame por valores de uma coluna específica
`harvestA = cgt_data[cgt_data['Test file used'] == 'coletoressafra2021_31_23']`

## Outra maneira de fazer um filtro, aqui utilizando a função `.query(<condições>)`

`print(harvestA.head())`

```
                   Method  Number of Days          Base  Radius            Test file used           TPP  TNP           FPP           FNP  number_of_starting_points
0   Circular Growth touch             137  1.693235e+11      20  coletoressafra2021_31_23  1.000000e-10    0  1.000000e-10  10320.282989                          4
3   Circular Growth touch             137  9.615541e+08      25  coletoressafra2021_31_23  6.254758e+01    0  4.663223e+01   1268.093015                          4
6   Circular Growth touch             137  3.060634e+07      30  coletoressafra2021_31_23  5.463813e+01    0  5.787640e+01    336.548436                          4
9   Circular Growth touch             137  2.608614e+06      35  coletoressafra2021_31_23  5.696827e+01    0  5.930543e+01    176.105266                          4
12  Circular Growth touch             137  4.114893e+05      40  coletoressafra2021_31_23  4.687807e+01    0  6.317204e+01    109.996305                          4
```

`harvestA = harvestA.query('Radius >= 55')`

`print(harvestA.head())`


```
                   Method  Number of Days       Base  Radius            Test file used        TPP  TNP        FPP           FNP  number_of_starting_points
21  Circular Growth touch             137  12110.717      55  coletoressafra2021_31_23  28.562414    0  85.021365  1.000000e-10                          4
24  Circular Growth touch             137   5532.299      60  coletoressafra2021_31_23  27.366217    0  91.380129  1.000000e-10                          4
```

## Utilizando comandos de localização como `iloc` e `loc` (linhas específicas do DataFrame)

`print(harvestA.iloc[0])`

```
Method                          Circular Growth touch
Number of Days                                    137
Base                                        12110.717
Radius                                             55
Test file used               coletoressafra2021_31_23
TPP                                         28.562414
TNP                                                 0
FPP                                         85.021365
FNP                                               0.0
number_of_starting_points                           4
Name: 21, dtype: object
```

`print(harvestA.loc[21])`

```
Method                          Circular Growth touch
Number of Days                                    137
Base                                        12110.717
Radius                                             55
Test file used               coletoressafra2021_31_23
TPP                                         28.562414
TNP                                                 0
FPP                                         85.021365
FNP                                               0.0
number_of_starting_points                           4
Name: 21 <-- Este valor! , dtype: object
```

Perceba que harvestA.iloc[0] e harvestA.loc[21] retornam o **mesmo** resultado, isso acontece pelo fato que iloc retorna o valor da linha pelo seu índice, enquanto loc retorna o valor da linha pelo seu rótulo (name, por exemplo) mostrado na tabela acima.

Para conseguir esse valor, podemos fazer também da seguinte forma:

`print(harvestA.index[0])`

```
21
```

`print(harvestA.index[1])`

```
24
```

Isso recupera o índice da linha 0 do DataFrame harvestA.

## Como mudar o valor de uma célula específica do DataFrame?

**Não** funciona fazer:

```harvestA.loc[21]['TPP'] = 0.0``` 

```harvestA.iloc[0]['TPP'] = 0.0```

Recebemos o seguinte aviso:

```
SettingWithCopyWarning:
A value is trying to be set on a copy of a slice from a DataFrame

See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  harvestA.loc[21]['TPP'] = 0.0
```

```
SettingWithCopyWarning:
A value is trying to be set on a copy of a slice from a DataFrame

See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
  harvestA.iloc[0]['TPP'] = 0.0
```

### Jeito correto:

```harvestA.loc[21, 'TPP'] = 1.5```

```
------------------ANTES:
Method                          Circular Growth touch
Number of Days                                    137
Base                                        12110.717
Radius                                             55
Test file used               coletoressafra2021_31_23
TPP                                         28.562414
TNP                                                 0
FPP                                         85.021365
FNP                                               0.0
number_of_starting_points                           4
Name: 21, dtype: object

------------------DEPOIS:
Method                          Circular Growth touch
Number of Days                                    137
Base                                        12110.717
Radius                                             55
Test file used               coletoressafra2021_31_23
TPP                                               1.5 <-- Valor alterado!
TNP                                                 0
FPP                                         85.021365
FNP                                               0.0
number_of_starting_points                           4
Name: 21, dtype: object
```

A diferença está na maneira de acessar a linha e coluna, juntamente com utilizar somente o comando ```loc``` para realizar alterações no DataFrame.