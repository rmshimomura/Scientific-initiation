# Anotações de estudo IC
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


Sobre os coletores carrapichos, se cria_buffers.criaCarrapicho(growth_topology, 0.2, False, 0) vira circulo.

USANDO 0.05
Inicio teste
Train file used: /Trained_Data/all_together/geometric_mean_31_23
Test file used: /Test_Data/coletoressafra2021_31_23
Base used: 86679601.69000001
Radius used: 30
Number of days used: 137
True positive: 126
False positive: 40
Error mean: 7.898220655689253
Error std: 16.414976445943108
Error max: 66.2601009909181
Error min: -24.49913494550748

USANDO 0.1
Inicio teste
Train file used: /Trained_Data/all_together/geometric_mean_31_23
Test file used: /Test_Data/coletoressafra2021_31_23
Base used: 86679601.69000001
Radius used: 30
Number of days used: 137
True positive: 126
False positive: 40
Error mean: 7.898220655689253
Error std: 16.414976445943108
Error max: 66.2601009909181
Error min: -24.49913494550748


Para comparar, utilizaremos TG_106_104




# RESULTADOS DOS TESTES

## Qual média usar?
Guiando-se pelos resultados testes de penalidades, obtive que a média __ARITMÉTICA__ é a melhor para o modelo em 5 dos 6 casos (CGNT - TPP e FPP, MG - TPP e FPP, TG - TPP). Os gráficos em relação aos modelos CGNT e MG ficaram "comportados" enquanto os gráficos de TG ficaram "instáveis" em alguns pontos.

## CGT observações:
Sobre o _Circular Growth touch_, o único raio que conseguiu detectar todos os coletores nos 6 casos ("treina" A - testa B e C, "treina" B - testa A e C e "treina" C - testa A e B) foi de __60KM__, então tenho que saber se os gráficos comparativos devem ser feitos com esse raio ou com o raio de __25~30KM__, que é o que eu estou usando para os outros modelos.

## TG observações:
Sobre o _Topology Growth_, percebi que ele começa a dar resultantes diferentes do base line apenas a partir de __30km__ de raio. Novamente, tenho que saber se os gráficos comparativos devem ser feitos com esse raio ou com o raio de __25~30KM__, que é o que eu estou usando para os outros modelos.

## No geral:

- Como devo fazer para construir um ranking?
1. Ordenar os resultados por erro médio?
2. Ordenar os resultados por desvio padrão?
3. Devo considerar as observações mostradas nos dois tópicos acima?

Pensei em fazer os seguintes gráficos:
- Número de falsos positivos, comparando CGNT, MG e TG, porque daí ficaria mais fácil de ver que por conta do formato da topologia ser aprendido, o TG tem __menos__ falsos positivos em relação aos outros dois modelos.
- Erro médio junto com desvio padrão usando média aritmética dos modelos CGNT, MG e TG e CGT? Acho que fique muito bagunçado...

Tabelas:
Dependem da resposta da pergunta sobre o ranking.

> Mas, pensei em comparar 2 a 2 (CGNT vs MG, CGNT vs TG, CGNT vs CGT):

### O que cada tabela conseguiria mostrar?
- CGNT vs MG: Mostrar se a ideia de misturar propagação por toque e propagação por data é melhor do que apenas por data
- CGNT vs TG: Mostrar se a ideia de utilizar uma topologia com a forma aprendida previamente (TG) é melhor do que apenas um círculo simples (que é o que eu estou usando para o CGNT)
- CGNT vs CGT: Mostrar a diferença entre utilizar aprendizado de datas (CGNT) e apenas utilizar propagação por toque (CGT)
