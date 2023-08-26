# Anotações de estudo IC

## A fazer:

- [x] Colocar os que nao detectaram aqui também
- [x] Pensar em como penalizar os resultados
- [x] Fazer função de penalidade
- [x] Arrumar erros no RMSE
- [x] Opção de "animação"
- [x] Gerar csv com os resultados
- [x] Transformar o csv que eu estou usando para o que o Evandro usa
- [] Crescimento dos carrapicho 
- Pensar no crescimento dinâmico
- 1. Adaptar o programa atual para aceitar o csv 2021Final ok
- 2. Rodar com o csv enriquecido com os fakes (ideia do quadriculado) os carrapichos já feitos. FAZER!

> Na hora de escolher o tamanho dos quadradinhos, calcular a menor bouding box do Paraná e a partir daí fazer vários testes com tamanhos diferentes (20x20, 20x30, 10x10...)

> Para testes, colocar os fakes somente nos quadradinhos que não tiverem coletores já reais

> Para treinamento, colocar todos os pontos centrais. Decidir também sobre se o ponto que está representando aquele quadrado está infectado ou não baseado nos coletores dentro do quadrado




## Importante para o estudo:
- Estima-se que a primeira geração de pústulas pode manter a esporulação por até quinze semanas,mesmo sob condições de baixa umidade. Para que o fungo (Phakopsora pachyrhizi) infecte a planta
    são necessárias condições favoráveis, tais como disponibilidade de água na folha, mínimo de 6
    horas de molhamento foliar e temperatura entre 15 e 25º C. Sendo assim, o clima, em especial,
    as chuvas podem favorecer a infestação da doença. Em condições favoráveis, o fungo completa o seu
    ciclo de vida de 6 a 9 dias.
- Se considerarmos um crescimento constante, isso significa que temos que ter uma multiplicacao dos esporos exponencial

## Classificação dos resultados do modelo e penalidades:

- Verdadeiro positivo: O modelo diz que tem e realmente tem (com um possível erro de dias) 

        |Data descoberta - data real|^2 = delta

- Verdadeiro negativo: não faz sentido contabilizar no erro, pois não altera o erro porque é um "acerto 100%"
    
    
- Falso positivo: O modelo diz que tem, mas não tem esporos ali

        Data final - data descoberta = delta

- Falso negativo: O modelo diz que não tem, mas existem esporos ali

        Quantidade de dias que seriam necessários para chegar até o determinado coletor partindo do coletor verdadeiro positivo mais próximo

Map length: 735.1995280519512 km
Map height: 468.1821515409006 km
Square size: 23.71611380812746 km x 20.35574571916959 km (Proporção 31_23)
Diagonal: 31.2539667553344 km

- Base ideal para chegar a um raio de 20km: 807003392603.5468 - 20.000000000000004km

- Base ideal para chegar a um raio de 25km: 3353515271.3289995 - 25.00000000000019km

- Base ideal para chegar a um raio de 30km: 86679601.69000001 - 30.000000000011944km

- Base ideal para chegar a um raio de 35km: 6366910.974999996 - 35.000000000052566km

- Base ideal para chegar a um raio de 40km: 898333.6750000002 - 40.000000001743786km

- Base ideal para chegar a um raio de 45km: 195859.48300000007 - 45.00000000739926km

- Base ideal para chegar a um raio de 50km: 57909.54299999999 - 50.00000006856275km

- Base ideal para chegar a um raio de 55km: 21368.440999999988 - 55.00000025810737km

- Base ideal para chegar a um raio de 60km: 9310.188000000004 - 60.000000041480114km

No arquivo de testes, os erros são calculados majoritariamente da seguinte forma:

test_collector['DiasAposInicioCiclo'] - (start_day + day)

Assim sendo, um valor médio de erro positivo, significa que o modelo está adiantado em relação ao real. Um valor médio de erro negativo, significa que o modelo está atrasado em relação ao real.

k escolhido para o k-CGT foi 4!

Mesma coisa:

>> print(_collectors.iloc[count])

>> print(_collectors.loc[_collectors.index[count]])