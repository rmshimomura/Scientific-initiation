import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from geopandas import GeoDataFrame
import numpy as np 
from shapely import affinity
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import LineString


# ## Grafo de Propagação
# 
# A partir dos dados da primeira observação nos diversos coletores, é criado um grafo G=(V,E), tal que, V são os coletores;
# (u,v) pertence a E, se foram detectados esporos primeiro no coletor u e depois no coletor v. 
# Este grafo tende a ser bastante denso. Por isso, também são definidos alguns critérios de poda de arestas.
# 

# # CONSTRUÇÃO DA MATRIZ DE ADJACÊNCIA
# 
# # Construção do Grafo
# 
# ## Pré-processamento (constroiMatriz)
# 
# - Vamos usar uma matriz de adjacência
# - Cada coletor é um nó
# - O data frame gdf é processado e a matriz é atualizada
# - i significa que a corrente invocação é a i-esima invocação, o seja, o peso de uma aresta (u,v) é a média de (i-1) iteracoes


def calcularDistanciaEntreColetores(geo_df):
    distancias = pd.DataFrame(00.0,index=geo_df.index,columns=geo_df.index)  # TODO
    for i in geo_df.index:
        for j in geo_df.index:
            p1 = geo_df.loc[i].geometry
            p2 = geo_df.loc[j].geometry
            distancias.at[i,j] = p1.distance(p2)
    return distancias

def deltaTempo(gdf,i,j,tooLarge=1000):
    row_i = gdf.loc[i]
    row_j = gdf.loc[j]
    if 'DiasAposInicioCiclo' not in gdf.columns:
        dia_i = row_i['MediaDiasAposInicioCiclo']
        dia_j = row_j['MediaDiasAposInicioCiclo']
    else:
        dia_i = row_i['DiasAposInicioCiclo'] 
        dia_j = row_j['DiasAposInicioCiclo']

    if dia_i == -1 or dia_j == -1:
        return tooLarge

    if dia_i is pd.NaT or dia_j is pd.NaT:
        print("OK: TOO LARGE")
        delta_t = tooLarge
    else:
        d = dia_j - dia_i
        delta_t = d if d >= 0 else tooLarge

    return delta_t

def calculaVelocidade(gdf,i,j,distancias,delta_t):
    
    distancia_i_j = distancias.at[i,j]
    veloc = 0.0 if delta_t == 0 else distancia_i_j / delta_t
    
    return veloc

def atualizaVelocidadeMedia(matrizAdj,i,j, k, index, veloc):
    mediaAntiga = matrizAdj.at[i,j]
    mediaNova = (mediaAntiga*(k-1) + veloc) / k
    matrizAdj.at[i,j] = mediaNova
    
def constroiMatriz(matrizAdj, k: int, geo_df: GeoDataFrame, distancias,max_delta_t=10):  
    for i in geo_df.index: 
        for j in geo_df.index:
            dt = deltaTempo(geo_df,i,j,max_delta_t + 10)
            if (dt <= max_delta_t):
                veloc = calculaVelocidade(geo_df,i,j,distancias,dt)
                atualizaVelocidadeMedia(matrizAdj,i,j, k, geo_df.index, veloc)
    return matrizAdj
            
    

# CONSTRUÇÃO DO GRAFO
# 
# Vamos construir um grafo G = (V,E)
# 
# Vértices:
# V = cjto dos coletores
# 
# **Atributos de um vértice:**
# - td: tempo de detecção (em relação à primeira detecção)
# 
# ## Arestas
# 
# - (u,v) é uma aresta de E, se foram detectados esporos em u e v: (b) u.td < v.td
#   e (b) v.td - u.td <= max_delta_t
# 
# 
#  Atributos de uma aresta:
#
# - v: velocidade de propagação. Velocidade de propagação mínima para que os esporos detectados em u 
#        sejam dissiminados até v. (distancia(v,u)/(v.td - u.td))
# 
#  Pacote para manipulação de grafos: https://networkx.org/


def constroiGrafo(matrizAdj, geo_df, distancias, raio_de_possivel_contaminacao: float):
    G = nx.DiGraph()
    
    G.add_nodes_from(matrizAdj.index)
    
    for i in matrizAdj.index:
        posicaoColetor = geo_df.loc[i].geometry
        G.nodes[i]['local'] = posicaoColetor
        G.nodes[i]['idx'] = i
        for j in matrizAdj.index:
            w = matrizAdj.at[i,j]
            distancia = distancias.at[i,j]
            if (w > 0.0) and (distancia <= raio_de_possivel_contaminacao):  # "poda" arestas muito longas
                G.add_edge(i,j,weight=w)
    return G


# COLETORES
# 
# Processa os dados dos coletores de esporos em cada uma das safras de interesse.
# Os dados de uma safra são fornecidos em um arquivo csv em que cada linha do arquivo 
# representa um coletor. Cada coletor possui os seguintes atributos:
#  
#   (a) a sua localizacao (latitude e longitude)
#   (b) a data que o primeiro esporo foi detectado


class Coletores:
    def __init__(self,nomeCampoLongitude: str , nomeCampoLatitude: str,  
                 nomeCampoDataPrimeiroEsporo: str):
        self.Longitude = nomeCampoLongitude
        self.Latitude = nomeCampoLatitude
        self.DataPrimeiroEsporo = nomeCampoDataPrimeiroEsporo
        self.InicioCiclo = "InicioCiclo"
        self.DiasAposInicioCiclo = "DiasAposInicioCiclo"
        self.geo_df = None
        self.grafoPropagacao = None
        self.topologiaCrescimentoDict = dict()
     
    def to_csv(self, coletoresfn):
        self.geo_df.to_csv(coletoresfn)
        
    def to_file(self, coletoresfn):
        self.geo_df.to_file(coletoresfn+".shp")
        
    def addColetores(self, coletoresfn, raio_de_abrangencia_imediata, raio_de_possivel_contaminacao, max_delta_t, nomeCampoLongitude: str="" , nomeCampoLatitude: str = "", 
                    nomeCampoDataPrimeiroEsporo: str = "",  
                    InicioCiclo: str = "", DiasAposInicioCiclo: str = "",
                    fake = False, safraPrefix = "s", dateFormat="%d/%m/%Y", 
                    separadorCampo=";", separadorDecimal=","):
        new_gdf = self._readColetores(coletoresfn, nomeCampoLongitude, nomeCampoLatitude,  
                                 nomeCampoDataPrimeiroEsporo, InicioCiclo, DiasAposInicioCiclo, fake,safraPrefix, 
                                 dateFormat,separadorCampo,separadorDecimal)
        print(new_gdf)
        (g,_) = self.criaGrafo(new_gdf,raio_de_possivel_contaminacao, max_delta_t,safraPrefix)

        try:
            if self.geo_df is None:
                # primeiro arquivo de coletores processados (i.e., primeira safra)
                self.geo_df = new_gdf
                self.grafoPropagacao = g
            else:
                geo_df = pd.concat([self.geo_df,new_gdf],  ignore_index=False)
                self.geo_df = geo_df
                self.grafoPropagacao = nx.disjoint_union(self.grafoPropagacao,g)
        except Exception as e:
            print(type(e))    # the exception type
            print(e)     # arguments stored in .args
            print(e)
            print("index geodf",self.geo_df['idx'])
            print("new gdf", new_gdf['idx'])
            raise
        print("addColetores: added %s  total rows: %d" % (coletoresfn, len(self.geo_df)))
        #print("SAINDO ADDCOLETORES: %s" % safraPrefix)
    
    def preencheComColetoresFake(self):
        pass
    
    def _readColetores(self, coletoresfn, nomeCampoLongitude: str , nomeCampoLatitude: str,  
                       nomeCampoDataPrimeiroEsporo: str, 
                       nomeCampoInicioCiclo: str, nomeCampoDiasAposInicioCiclo: str,
                       isFake: bool, safraPrefix: str,
                       dateFormat="%d/%m/%Y", separadorCampo=";", separadorDecimal=","):
        
        #print("ENTRANDO: readColetores %s" % safraPrefix)
        if nomeCampoDataPrimeiroEsporo != "":
            campoData = nomeCampoDataPrimeiroEsporo
        else:
            campoData = self.DataPrimeiroEsporo

        df = pd.read_csv(coletoresfn, sep=separadorCampo, decimal=separadorDecimal)
        (nlins,_) = df.shape
        idents = ["%s.%d" %(safraPrefix,n) for n in range(nlins)]

        geometry = [Point(x,y) for x,y in zip(df[self.Longitude], df[self.Latitude])]
        new_gdf = GeoDataFrame(df, geometry=geometry)
        new_gdf["idx"] = idents
        new_gdf["fake"] = isFake
        new_gdf.set_index("idx", inplace = True)
        new_gdf.flags.allows_duplicated_labels = False  # for debuging

        new_gdf[campoData] = pd.to_datetime(new_gdf[campoData], format = dateFormat)
        minData = new_gdf[campoData].min()
        new_gdf["teste"] = new_gdf[campoData] - minData
        new_gdf[self.DiasAposO0] = new_gdf["teste"].dt.days
        
        if nomeCampoLongitude != "":
            new_gdf.rename(columns={nomeCampoLongitude: self.Longitude}, inplace = True)   
        if nomeCampoLatitude != "":
            new_gdf.rename(columns={nomeCampoLatitude: self.Latitude}, inplace = True)   
        if nomeCampoDataPrimeiroEsporo != "":
            new_gdf.rename(columns={nomeCampoDataPrimeiroEsporo: self.DataPrimeiroEsporo}, inplace = True)    
        if nomeCampoInicioCiclo != "":
            new_gdf.rename(columns={nomeCampoInicioCiclo: self.InicioCiclo}, inplace = True)    
        if nomeCampoDiasAposInicioCiclo != "":
            new_gdf.rename(columns={nomeCampoDiasAposInicioCiclo: self.DiasAposInicioCiclo}, inplace = True)    

        # Seleciona apenas as colunas de interesse
        new_gdf = new_gdf[[self.Longitude, self.Latitude,self.DataPrimeiroEsporo,self.DiasAposO0, 'geometry','fake']] 
           
        #print("SAINDO: readColetores %s" % safraPrefix)
        return new_gdf
    
    # max_delta_t: um dos criterios de poda. Só acrescenta uma aresta (v,u) se o numero de dias
    # transcorridos entre a primeira deteccao de v e depois de u nao exceder a max_delta_t dias.
    def criaGrafo(self,new_gdf,raio_de_possivel_contaminacao, max_delta_t=20):
        matrizAdjacencia = pd.DataFrame(0.0,index=new_gdf.index, columns=new_gdf.index)
        distancias = calcularDistanciaEntreColetores(new_gdf)
        matrizAdjacencia = constroiMatriz(matrizAdjacencia, 1, new_gdf, distancias,max_delta_t)
        G = constroiGrafo(matrizAdjacencia,new_gdf, distancias, raio_de_possivel_contaminacao)
        self.grafoPropagacao = G
   
    def calculaSegmentoGeometria(self,localColetor: Point, localColetorVizinho: Point, raio_de_abrangencia_imediata: float, raio_de_possivel_contaminacao: float):
        arc = LineString([localColetor,localColetorVizinho])
    
        segmentoA = affinity.rotate(arc, 90, origin=localColetor)
        segmentoB = affinity.rotate(arc, -90, origin=localColetor)
        b1 = segmentoA.interpolate(raio_de_abrangencia_imediata);
        b2 = segmentoB.interpolate(raio_de_abrangencia_imediata);
    
        proporcao = arc.length / raio_de_possivel_contaminacao  # < 1, pois aresta mais extensas que raio_de_possivel_contaminacao foram "podadas" anteriormente
        dt = raio_de_abrangencia_imediata + raio_de_abrangencia_imediata * proporcao
        p = arc.interpolate(dt)
    
        return (p , localColetorVizinho)

    def geraTopologiasCrescimento(self, raio_de_abrangencia_imediata, raio_de_possivel_contaminacao,largSeg):
        G = self.grafoPropagacao
    
        for nodeColetor in G.nodes():
            localColetor = G.nodes[nodeColetor]['local']
            indiceColetor = G.nodes[nodeColetor]['idx']
            gt = GrowthTopology(localColetor, raio_de_abrangencia_imediata)

            for coletorVizinho in G.neighbors(nodeColetor):
                localColetorVizinho = G.nodes[coletorVizinho]['local']
                (p1,p2) = self.calculaSegmentoGeometria(localColetor,localColetorVizinho,raio_de_abrangencia_imediata,raio_de_possivel_contaminacao)
                gt.addSegment(p1,p2,largSeg)
            self.topologiaCrescimentoDict[indiceColetor] = gt
       
    def addTopologiaCrescimento(self,gt,indiceColetor):
        self.topologiaCrescimentoDict[indiceColetor] = gt
        
    def expand(self, proportion: float,proportionLarg):
        for gt in self.topologiaCrescimentoDict.values():
            gt.growTopology(proportion, proportionLarg)

    def expandSome(self, proportion: float, idxLst):
        pass

    def getGrowthTopology(self,idx):
        return self.topologiaCrescimentoDict[idx]     
                                
    def addBuffer(self,columnName, geoSer):
        self.geo_df[columnName] = geoSer
        
    def plotGrafo(self, withLabels=True):
        aux = self.geo_df['geometry']
        coordinates = np.column_stack((aux.geometry.x, aux.geometry.y))
        positions = dict(zip(aux.index, coordinates))
        nx.draw(self.grafoPropagacao, positions,with_labels=withLabels)


# TOPOLOGIA DE CRESCIMENTO
# 
# Considere o grafo de propagação G construído anteriormente.
# Vamos definir duas medidas: (a) área de abrangência imediata da estação (AI); (b) área de potencial contaminação direta (APC).
# 
# ## Área de Abrangência Imediata (AI)
# 
# É definida por uma circunferência de raio raio_de_abrangencia_imediata, centrada na estação de monitoramento. Esta circunferência será distorcida a fim de gerar o buffer seminal da estação.
# 
# ## Área de Potencial Contaminação Direta (APC)
# 
# É definida por uma circunferência de raio raio_de_possivel_contaminacao, centrada na estação de monitoramento. 
# Define um critério de "poda" de arestas do grafo G: arestas de comprimento superior a raio_de_possivel_contaminacao são desconsideradas.
# 
# Para cada coletor é criada uma "topologia de crescimento". 
# Esta topologia é constituída pelas coordenadas do coletor (center), 
# pelo raio de abrangência imediata (raio_de_abrangencia_imediata) e um conjunto de segmentos. 
# Cada segmento é delimitado pela coordenada do coletor (início do crescimento) e 
# pela coordenada do coletor adjacente no grafo de propagacao (crescimento máximo).
# A este segmento é associado um ponto intermediário que representa o crescimento corrente.
# Este ponto intermediário é descolado em direção do ponto de crescimento máximo na medida
# que a topologia e' "expandida"

from collections import namedtuple
Segmento = namedtuple('Segmento','larg , seg')
class GrowthTopology:
    def __init__(self, center: Point, raio_de_abrangencia_imediata: float):
        self.center = center
        self.r = raio_de_abrangencia_imediata
        self._segs = []
        
    def addSegment(self, p: Point, pMax: Point,larg: float):
        # todos segmentos tem origem no ponto central
        # ponto central deve ser sempre a primeira coordenada
        segm = LineString([self.center,p, pMax])
        seg = Segmento(larg,segm)
        self._segs.append(seg)
        
    def growTopology(self, proportionSeg: float, proportionLarg:float):
        grownSegs = []
        for _ in range(len(self._segs)):
            segmento = self._segs.pop()
            seg = segmento.seg
            larg = segmento.larg
            center = Point(seg.coords[0])
            p1 = Point(seg.coords[1])
            dist = center.distance(p1)
            newLen = dist * proportionSeg
            newP = seg.interpolate(newLen)
            newSeg = LineString([self.center,newP,seg.coords[2]])
            newLarg = larg * proportionLarg
            newSegmento = Segmento(newLarg,newSeg)
            grownSegs.append(newSegmento)
        self._segs.extend(grownSegs)
        
       
    def getSegments(self):
        return self._segs

