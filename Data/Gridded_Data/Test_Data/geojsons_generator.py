import pandas as pd
import json
import os
from datetime import datetime, timedelta

def gerar_geojsons_safra(csv_path, ano_inicio_safra, pasta_saida_base):
    """
    Gera GeoJSONs diários de 01/Set a 01/Abr para a safra especificada.
    
    Args:
        csv_path (str): Caminho para o arquivo CSV.
        ano_inicio_safra (int): Ano de início da safra (ex: 2020 para 2020/2021).
        pasta_saida_base (str): Pasta raiz onde serão criadas as subpastas por safra.
    """
    
    # 1. Carregar os dados
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Erro ao ler {csv_path}: {e}")
        return

    # Definir nome da pasta específica para esta safra
    safra_nome = f"safra_{ano_inicio_safra}_{ano_inicio_safra+1}"
    pasta_saida = os.path.join(pasta_saida_base, safra_nome)

    # Criar pasta de saída se não existir
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # 2. Tratamento de Datas
    # O formato nos seus arquivos é DD/MM/YY (ex: 21/01/21)
    df['Primeiro_Esporo_dt'] = pd.to_datetime(df['Primeiro_Esporo'], format='%d/%m/%y', errors='coerce')

    # Definição do período da simulação (1 Setembro a 1 Abril do ano seguinte)
    data_inicio = datetime(ano_inicio_safra, 9, 1)
    data_fim = datetime(ano_inicio_safra + 1, 4, 1)
    
    data_atual = data_inicio
    
    print(f"-> Processando {safra_nome}...")
    print(f"   Arquivo: {csv_path}")
    print(f"   Período: {data_inicio.date()} até {data_fim.date()}")

    # Contador para feedback
    contador_arquivos = 0

    # 3. Loop Dia a Dia
    while data_atual <= data_fim:
        features = []
        
        # Iterar sobre cada ponto da malha
        for _, row in df.iterrows():
            # Lógica de Classificação
            # Padrão: "Sem esporo/Limpo"
            status_no_dia = "Sem esporo/Limpo"
            
            # Verifica se houve detecção de esporo em algum momento
            if pd.notnull(row['Primeiro_Esporo_dt']):
                # Se a data atual da simulação for maior ou igual à data do primeiro esporo
                if data_atual >= row['Primeiro_Esporo_dt']:
                    status_no_dia = "Com esporo"
            
            # Montar a Feature GeoJSON
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['LongitudeDecimal'], row['LatitudeDecimal']]
                },
                "properties": {
                    "data_simulacao": data_atual.strftime("%Y-%m-%d"),
                    "status": status_no_dia,
                    "situacao_original": row['Situacao'],
                    "inicio_ciclo": row['InicioCiclo'],
                    "dias_apos_inicio": row['DiasAposInicioCiclo']
                }
            }
            features.append(feature)

        # Montar o objeto FeatureCollection final
        geojson_final = {
            "type": "FeatureCollection",
            "features": features
        }

        # Nome do arquivo: safra_ANOS_DATA.json
        # Ex: safra_2020_2021_2020-09-01.json
        nome_arquivo = f"{safra_nome}_{data_atual.strftime('%Y-%m-%d')}.geojson"
        caminho_arquivo = os.path.join(pasta_saida, nome_arquivo)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(geojson_final, f, ensure_ascii=False)
            
        contador_arquivos += 1
        data_atual += timedelta(days=1)

    print(f"   Concluído! {contador_arquivos} arquivos gerados em: {pasta_saida}\n")

# --- CONFIGURAÇÃO E EXECUÇÃO ---

# Lista de arquivos e seus respectivos anos de início de safra
# Baseado na análise:
# coletoressafra2021 -> Safra 2020/2021 (Início 2020)
# coletoressafra2122 -> Safra 2021/2022 (Início 2021)
# coletoressafra2223 -> Safra 2022/2023 (Início 2022)

arquivos_para_processar = [
    ("coletoressafra2021_31_23.csv", 2020),
    ("coletoressafra2122_31_23.csv", 2021),
    ("coletoressafra2223_31_23.csv", 2022)
]

pasta_saida_geral = "geojsons_safras"

if __name__ == "__main__":
    print("Iniciando geração dos GeoJSONs...\n")
    for arquivo, ano_inicio in arquivos_para_processar:
        if os.path.exists(arquivo):
            gerar_geojsons_safra(arquivo, ano_inicio, pasta_saida_geral)
        else:
            print(f"AVISO: Arquivo '{arquivo}' não encontrado no diretório atual.\n")