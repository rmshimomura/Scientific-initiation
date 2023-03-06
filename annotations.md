# Anotações de estudo IC

## A fazer:

- [x] Colocar os que nao detectaram aqui também
- [x] Pensar em como penalizar os resultados
- [x] Fazer função de penalidade
- [x] Arrumar erros no RMSE
- [x] Opção de "animação"
- [x] Gerar csv com os resultados
- [ ] Transformar o csv que eu estou usando para o que o Evandro usa
- 1. Adaptar o programa atual para aceitar o csv 2021Final
- 2. Rodar com o csv enriquecido com os fakes (ideia do quadriculado) os carrapichos já feitos.

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
    
## Modelos que temos:

- Modelo dummy (crescimento em círculos)
    - 2 e 6 seeds (hard coded)
        - Crescimento em progressão e outro em linear
            - Geração dos infection circles no dia certo
            - Geração dos infection circles todos de uma vez
    
# Problemas na integração com os novos buffers

- Os arquivos de dados usados são diferentes (ColetoresSafra2122.csv e ColetoresSafra2021Final.csv)
- Isso significa que os buffers gerados são diferentes
- As coordenadas estão um pouco diferentes
- Como iniciar o modelo? A partir de qual(is) coletor(es)?

### Tentativa

Localizar coletores pelos centroids dos polígonos e compará-los com os centroids dos coletores:

```python

teste_buffer = gpd.GeoSeries.from_file('G:/' + root_folder + '/IC/Codes/buffers-seminais/15-005-safra2021-buffer-seminais-carrap.shp')
hit = 0

for polygon in teste_buffer:
    
    for _ in _collectors.itertuples():
        if round(polygon.centroid.x, 1) == round(_.Longitude, 1) and round(polygon.centroid.y, 1) == round(_.Latitude, 1):
            hit += 1
            break
print(f"hit vs total: {hit} vs {len(_collectors)}")

```

#### Resultados

round(x):

- 6: 4 vs 235
- 5: 5 vs 235
- 4: 6 vs 235
- 3: 9 vs 235
- 2: 29 vs 235

De 4 casas decimais para menos, temos uma precisão muito menor. Isso significa que os buffers gerados são diferentes dos coletores.

### O que fazer?

- Gerar novos buffers com os coletores do mesmo arquivo?
- Alterar o código para usar os novos coletores?