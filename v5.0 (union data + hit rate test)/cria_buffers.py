import os
import math
from shapely.geometry import Point
from shapely.geometry import Polygon, LineString
from shapely import affinity
import coletores as col
from geopandas import GeoSeries



# Criação de Buffers a Partir de uma Topologia de Crescimento
# 
# Buffers podem ser criados para representar a area abrangida por uma
# da topologia de crescimento. 
# A seguir, alguns exemplos de como criar um buffer a partir da topologia

# ### Exemplo 1: Criando Carrapichos

# constroi um triangulo "apontando" na direcao do coletor vizinho
def calculaTrianguloExpansao(segmento, r):
    segm = segmento.seg
    largSeg = segmento.larg

    arc = LineString([segm.coords[0],segm.coords[2]])
    
    segmentoA = affinity.rotate(arc, 90, origin=segm.coords[0])
    segmentoB = affinity.rotate(arc, -90, origin=segm.coords[0])
    b1 = segmentoA.interpolate(r);
    b2 = segmentoB.interpolate(r);
    
    trianguloExpansao = Polygon([segm.coords[1], b1, b2])
    bufferExpansao = trianguloExpansao.buffer(largSeg)
    return bufferExpansao

# constroi um triangulo "apontando" na direcao do coletor vizinho
def calculaTrianguloExpansaoPontaChata(segmento, r, rPonta):
    segm = segmento.seg
    largSeg = segmento.larg

    arc = LineString([segm.coords[0],segm.coords[2]])
    segmentoA = affinity.rotate(arc, 90, origin=segm.coords[0])
    segmentoB = affinity.rotate(arc, -90, origin=segm.coords[0])
    b1 = segmentoA.interpolate(r);
    b2 = segmentoB.interpolate(r);
    
    arc2 = LineString([segm.coords[2],segm.coords[0]])  
    rPonta = r/4
    segmentoC = affinity.rotate(arc2, -90, origin=segm.coords[2])
    segmentoD = affinity.rotate(arc2, 90, origin=segm.coords[2])
    p1 = segmentoC.interpolate(rPonta);
    p2 = segmentoD.interpolate(rPonta);
    trianguloExpansao = Polygon([b1, b2,p1,p2])
    bufferExpansao = trianguloExpansao.buffer(largSeg)

    return bufferExpansao

def criaCarrapicho(gt: col.GrowthTopology, proportR: float, comPontaChata: bool, rPonta: float):
    r = gt.r * proportR
    buffer = gt.center.buffer(r)
    segs = gt.getSegments()
    for seg in segs:
        if comPontaChata:
            bufferExpansao = calculaTrianguloExpansaoPontaChata(seg,r,rPonta)
        else:
            bufferExpansao = calculaTrianguloExpansao(seg,r)
        buffer = buffer.union(bufferExpansao)  
    return buffer

def geraBuffersCarrapichos(topol_cresc, r: float, comPontaChata = False, rPonta = 0.00001):
    buffs = []
    for gt in topol_cresc:
        buf = criaCarrapicho(gt,r,comPontaChata, rPonta)
        buffs.append(buf)
    return buffs


# ### Exemplo 2: Criando Amoras


# minAspecRat: para não "achatar" a elipse em demasia
def calculaElipseExpansao(segmento,r,minAspecRat = 0.2):
    seg = segmento.seg
    largSeg = segmento.larg

    p0 = Point(seg.coords[0])
    p1 = Point(seg.coords[1])
    
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    ang = math.atan2(dy,dx)
    
    if math.fabs(dy/dx) < minAspecRat:
        dy = dx * minAspecRat
    
    #print("dx ", dx, "  dy ", dy, "   ang ", (ang * 180.0)/math.pi)
    
    distP0P1 = p0.distance(p1)
    pM = seg.interpolate(distP0P1/2)
    b = pM.buffer(distP0P1)
    (sx,sy) = (dx,dy) if dx > dy else (dy,dx) # elipse alongada na eixo x, para depois rotacionar
    elipse = affinity.scale(b,sx,sy)
    b2 = affinity.rotate(elipse,ang,use_radians=True)
    return b2

def criaAmora(gt: col.GrowthTopology, proportR: float = 0.1):
    r = gt.r * proportR
    buffer = gt.center.buffer(r)
    segs = gt.getSegments()
    for seg in segs:
        bufferExpansao = calculaElipseExpansao(seg, r)
        buffer = buffer.union(bufferExpansao)  
    return buffer

def geraBuffersAmora(topol_cresc, proportR: float):
    buffs = []
    for gt in topol_cresc:
        buf = criaAmora(gt,proportR)
        buffs.append(buf)
    return buffs

# ### Exemplo 3: Criando Esqueleto
# este tipo de buffer  e' primariamente para debug. Enfatiza os pontos de referencia
# da topologia de crescimento

def criaEsqueleto(gt: col.GrowthTopology):
    r = gt.r / 1000
    buffer = gt.center.buffer(r)
    segs = gt.getSegments()
    for (largSeg,seg) in segs:
        # apenas para marcar pontos de referencia (finalidade debug)
        p1 = Point(seg.coords[1])
        p1buf = p1.buffer(0.008)
        p2 = Point(seg.coords[2])
        p2buf = p2.buffer(0.008)
        l1buf = LineString([gt.center,p1]).buffer(0.005)
        l2buf = LineString([p1,p2]).buffer(0.001)
        
        bufferExpansao = l1buf.union(l2buf)
        bufferExpansao = bufferExpansao.union(p1buf)
        bufferExpansao = bufferExpansao.union(p2buf)
        buffer = buffer.union(bufferExpansao)
    return buffer
    
def geraBuffersEsqueleto(topol_cresc):
    buffs = []
    for gt in topol_cresc:
        buf = criaEsqueleto(gt)
        buffs.append(buf)
    return buffs


# ### Exemplo 4: Cria Boneco Michelin

def calculaBufferMembroBoneco(seg, r1,r2, npassos: int):

    p0 = Point(seg.coords[0])
    p1 = Point(seg.coords[1])
    distanciaEntreCentros = p0.distance(p1)
    dpasso = distanciaEntreCentros/npassos
    diffRaios = r1 - r2
    buffer = p1.buffer(r2)

    for i in range(1,npassos+1):
        di = i * dpasso
        dr = (diffRaios * di) / distanciaEntreCentros
        ri = r2 + dr
        distP0ci = distanciaEntreCentros - di
        ci = seg.interpolate(distP0ci)
        bufferI = ci.buffer(ri)
        buffer = buffer.union(bufferI)
    return buffer
        
def criaBonecoMichelin(gt: col.GrowthTopology, r1: float, r2: float):
    segs = gt.getSegments()
    buffer = gt.center.buffer(r1)
    for (largSeg,seg) in segs:
        p0 = Point(seg.coords[0])
        p1 = Point(seg.coords[1])
        d = p1.distance(p0)
        npassos = int(d / r2) + 1
        bufferExpansao = calculaBufferMembroBoneco(seg,r1,r2, npassos)
        bufferExpansao = bufferExpansao.buffer(largSeg)
        buffer = buffer.union(bufferExpansao)  
    return buffer

def geraBuffersBonecosMichelin(topol_cresc, r1: float, r2: float):
    buffs = []
    for gt in topol_cresc:
        buf = criaBonecoMichelin(gt, r1, r2)
        buffs.append(buf)
    return buffs




# Crescimento
def funcProduzCarrapichos(fator,comPontaChata=False,rPonta=0.000001):
    return lambda topol_cresc: geraBuffersCarrapichos(topol_cresc,fator, comPontaChata, rPonta)

def funcProduzBonecosMichelin(r1: float, r2: float):
    return lambda topol_cresc: geraBuffersBonecosMichelin(topol_cresc,r1,r2)
    
def criaBuffers(topol_crescDict, funcProduzBuffer):
 
    topol_cresc = topol_crescDict.values()
    idx =  topol_crescDict.keys()
    bufs = funcProduzBuffer(topol_cresc)
    bufs_gs = GeoSeries(bufs,idx) 
                    
    return (bufs_gs)    

def simulaCrescimento(coletores_ja_detectados : list, f, fLarg, numero_dias = 10, diasPorIntervalo=1):

    fProduzBuffers = funcProduzCarrapichos(0.05,True,0.00001)

    # TODO: trocar por dias de cada coletor
    # incremento = 1.0 + f(d)
    # incrementoLarg = 1.0 + fLarg(d)
    # coletores.expand(incremento,incrementoLarg)

    ''' TODO
    Trocar por:
    gt.growTopology(incremento, incrementoLarg) com proporcoes para cada um dos coletores que foram detectados ja
    Cada coletor vai ter uma quantidade de dias de crescimento diferentes
    '''


    return criaBuffers(coletores_ja_detectados.topologiaCrescimentoDict, fProduzBuffers)
    
    #PARA CADA COLETOR coletorDestino QUE FOR TOCADO POR ALGUM BUFFER DE ALGUM COLETOR coletorOrigem FACA
    #   topologiaColetor = GrowGeometry(Point(coletorDestino.x, coletorDestino.y), rai)  # se primeiro toque
    #   seja a reta r que passa por coletorOrigem e coletorDestino,
    #      seja p o ponto em r a uma distancia rai depois de coletorDestino
    #      seja pMax o ponto em r a uma distancia rpc depois do coletorDestino
    #   topologiaColetor.addSegment( p, pMax):
    
    
