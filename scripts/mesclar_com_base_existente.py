#!/usr/bin/env python3
"""
Script para mesclar as inscrições processadas com a base existente do Google Sheets
Usa fuzzy matching para encontrar servidores e atualizar seus dados
"""

import csv
import sys
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, Optional, List
import re


def normalizar_nome(nome: str) -> str:
    """Normaliza um nome para comparação"""
    if not nome:
        return ""
    # Remove acentos, converte para maiúsculas, remove múltiplos espaços
    nome = nome.upper().strip()
    nome = re.sub(r'\s+', ' ', nome)
    return nome


def calcular_similaridade_nome(nome1: str, nome2: str) -> float:
    """Calcula similaridade entre dois nomes (0.0 a 1.0)"""
    n1 = normalizar_nome(nome1)
    n2 = normalizar_nome(nome2)
    return SequenceMatcher(None, n1, n2).ratio()


def carregar_inscricoes_processadas(csv_path: str) -> Dict[str, Dict]:
    """
    Carrega as inscrições processadas
    Retorna: {nome_normalizado: {dados...}}
    """
    inscricoes = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for linha in reader:
            nome = linha['nome'].strip()
            if nome:
                nome_norm = normalizar_nome(nome)
                inscricoes[nome_norm] = linha

    return inscricoes


def carregar_base_existente(csv_content: str) -> List[Dict]:
    """Carrega a base existente do Google Sheets como lista de dicts"""
    linhas = csv_content.strip().split('\n')
    reader = csv.DictReader(linhas)
    return list(reader)


def buscar_inscricao_por_nome(nome: str, inscricoes_proc: Dict[str, Dict]) -> Optional[Dict]:
    """
    Busca uma inscrição processada pelo nome usando fuzzy matching
    """
    nome_norm = normalizar_nome(nome)

    # Tenta match exato primeiro
    if nome_norm in inscricoes_proc:
        return inscricoes_proc[nome_norm]

    # Tenta fuzzy matching
    melhor_match = None
    melhor_score = 0.0

    for nome_proc_norm, dados in inscricoes_proc.items():
        score = calcular_similaridade_nome(nome, dados['nome'])
        if score > melhor_score:
            melhor_score = score
            melhor_match = dados

    # Só retorna se o score for muito alto (95%+)
    if melhor_score >= 0.95:
        return melhor_match

    return None


def mesclar_dados(base_existente_content: str, inscricoes_proc_path: str, output_path: str):
    """
    Mescla os dados processados com a base existente
    """
    print("🔄 Mesclando dados...")
    print(f"📁 Base existente: (conteúdo fornecido)")
    print(f"📁 Inscrições processadas: {inscricoes_proc_path}")
    print(f"📁 Saída: {output_path}\n")

    # Carrega inscrições processadas
    inscricoes_proc = carregar_inscricoes_processadas(inscricoes_proc_path)
    print(f"✅ Carregadas {len(inscricoes_proc)} inscrições processadas\n")

    # Carrega base existente
    base_existente = carregar_base_existente(base_existente_content)
    print(f"✅ Carregada base existente com {len(base_existente)} registros\n")

    # Estatísticas
    atualizados = 0
    nao_encontrados = []

    # Mescla dados
    resultado = []

    for registro in base_existente:
        nome = registro['nome'].strip()

        # Busca inscrição processada
        inscricao = buscar_inscricao_por_nome(nome, inscricoes_proc)

        if inscricao:
            # Atualiza com dados reais
            registro['escolha_anexo1'] = inscricao['escolha_anexo1']
            registro['escolha_anexo2'] = inscricao['escolha_anexo2']
            registro['posicao_lista_classificatoria'] = inscricao['posicao_lista_classificatoria']
            registro['data_alteracao'] = '08/12/2025'
            registro['alterado_por'] = 'SISTEMA'

            print(f"✅ Atualizado: {nome}")
            print(f"   Posição: {inscricao['posicao_lista_classificatoria']}")
            print(f"   Anexo I: {inscricao['escolha_anexo1']}")
            print(f"   Anexo II: {inscricao['escolha_anexo2']}\n")

            atualizados += 1
        else:
            print(f"⚠️  Não encontrado: {nome}")
            nao_encontrados.append(nome)

        resultado.append(registro)

    # Salva resultado
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        if resultado:
            writer = csv.DictWriter(f, fieldnames=resultado[0].keys())
            writer.writeheader()
            writer.writerows(resultado)

    print("\n" + "="*80)
    print("📊 RESUMO DA MESCLAGEM")
    print("="*80)
    print(f"✅ Registros atualizados: {atualizados}/{len(base_existente)}")
    print(f"⚠️  Não encontrados: {len(nao_encontrados)}")

    if nao_encontrados:
        print("\n🔍 Servidores não encontrados nas inscrições processadas:")
        for nome in nao_encontrados:
            print(f"  - {nome}")

    print(f"\n✅ Arquivo gerado: {output_path}")


if __name__ == '__main__':
    # Conteúdo da base existente (fornecido pelo usuário)
    BASE_EXISTENTE = """nome,matricula,data_admissao,lotacao_atual,escolha_anexo1,escolha_anexo2,data_inscricao,registrado_por,alterado_por,data_alteracao,posicao_lista_classificatoria
Americo Mendes Flores,260729,09/06/2022,A2-353,A1-067,A2-159,08/12/2025 00:22,(41) 99781-3606,(41) 99781-3606,08/12/2025 00:22,1052
Fabricio Pereira dos Santos,285500,18/07/2022,A2-035,A1-091,A2-005,03/12/2025 19:57,(41) 99781-3606,(41) 99781-3606,03/12/2025 19:57,1087
Simone Kelly do Nascimento,285546,21/07/2022,A2-229,A1-053,A2-091,27/11/2025 23:39,,,,1099
Guilherme Cravetz Assumpcao Marques,21294,26/11/2021,A2-376,A1-069,A2-130,07/12/2025 21:19,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:19,991
João Marcelo Thomaz Mendes,284330,13/04/2022,A2-368,A1-003,A2-312,28/11/2025 20:49,,,,1042
Jackson da Rocha,13313,03/09/2012,A2-177,A1-036,A2-200,08/12/2025 02:45,(45) 98404-7070,(45) 98404-7070,08/12/2025 02:45,585
Júlia de Souza Camargo,285976,15/08/2022,A2-516,A1-161,A2-318,28/11/2025 16:20,,,,1155
Carlos Eduardo Fernandes Martins,52590,10/07/2014,A2-099,A1-015,A2-027,28/11/2025 01:01,,,,941
Gonçalo Faiçal Valim,15113,16/08/2010,A2-348,A1-124,A2-232,05/12/2025 18:55,(41) 99781-3606,(41) 99781-3606,05/12/2025 18:55,216
Alan Torchi,51704,29/11/2012,A2-273,A1-136,A2-275,28/11/2025 20:47,,,,646
Josemar Douglas Carneiro,51985,28/06/2013,A2-491,A1-186,A2-213,28/11/2025 00:04,,,,754
Michelli de Souza Zanon,52121,11/11/2013,A2-481,A1-127,A2-510,28/11/2025 00:05,,,,798
Leiya Leika Nita Escobar de Oliveira,52686,28/07/2014,A2-354,A1-219,A2-188,07/12/2025 15:33,(41) 99781-3606,(41) 99781-3606,07/12/2025 15:33,966
Pedro Lucchese Piovesan,286006,26/09/2022,A2-257,A1-081,A2-110,08/12/2025 01:51,(41) 99852-6855,(41) 99852-6855,08/12/2025 01:51,1190
Silvana das Graças Borba Plugge Nowicki,50081,25/10/2010,A2-129,A1-077,,28/11/2025 00:09,,,,252
Pauliane Galdino Ribeiro,13862,22/07/2008,A2-406,A1-216,,28/11/2025 00:16,,,,105
Caroline Akemi Kumata,52285,05/05/2014,A2-130,A1-079,A2-109,03/12/2025 21:27,(41) 99781-3606,(41) 99781-3606,03/12/2025 21:27,855
Rodrigo Hilgemberg Daloski,14092,01/08/2008,A2-342,A1-078,A2-152,28/11/2025 00:22,,,,126
Wilian Jorge de Oliveira,13917,21/07/2008,A2-517,A1-095,A2-480,28/11/2025 00:25,,,,98
Andre de Araujo Moralles,51671,21/11/2012,A2-242,A1-123,A2-505,28/11/2025 00:25,,,,638
Cecília dos Santos Kenski Boroski,15131,10/08/2010,A2-501,A1-074,A2-141,28/11/2025 20:52,,,,207
Leandro Xavier Silva,219093,03/10/2023,A2-353,A1-008,A2-004,28/11/2025 00:29,,,,1250
Alessandra Costa Radunz,51029,16/11/2011,A2-199,,A2-202,28/11/2025 00:36,,,,484
Tatiane Maffini,281795,11/11/2021,A2-315,A1-126,,07/12/2025 21:23,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:23,998
Maria Valéria Panek,51627,17/10/2012,A2-049,A1-084,A2-158,28/11/2025 00:39,,,,626
Ricardo Ali Nageib Bark,285632,19/08/2022,A2-299,A1-049,A2-321,28/11/2025 00:41,,,,1163
Silvia Denise Klein Paludo,50848,13/06/2011,A2-060,A1-038,A2-065,28/11/2025 00:42,,,,441
Jean Carlo Toaldo,270690,04/07/2022,A2-024,A1-013,,28/11/2025 00:46,,,,1061
Vanessa Bizetto Bueno Ferreira,14443,12/02/2014,A2-159,A1-083,,28/11/2025 01:09,,,,830
Claudiney Martins Lecheta,52710,31/07/2014,A2-228,,A2-229,28/11/2025 00:54,,,,970
Gislaine Maria da Silva,51066,10/11/2011,A2-406,A1-217,A2-410,28/11/2025 00:56,,,,481
Aristoteles Fernandes Bandeira de Oliveira,285520,25/07/2022,A2-110,A1-063,,28/11/2025 00:57,,,,1101
Flavio Pereira Leite,50013,09/09/2010,A2-406,A1-129,A2-261,28/11/2025 00:59,,,,232
Michelle Helena Marangoni,285681,18/07/2022,A2-083,A1-044,,28/11/2025 17:52,,,,1086
Augusto de Oliveira Bressan,284074,04/04/2022,A2-352,A1-161,A2-184,06/12/2025 01:41,(41) 99781-3606,(41) 99781-3606,06/12/2025 01:41,1036
Vinicius Blasi Marchiori,13370,05/11/2007,A2-184,,A2-481,28/11/2025 13:09,,,,56
Bianca Stocco Nicoli,13222,15/10/2007,A2-335,A1-176,,28/11/2025 15:11,,,,38
Alline Filete Rodriguez,282495,03/12/2021,A2-292,A1-081,A2-166,05/12/2025 01:25,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:25,1003
Thais Mise Yanagui,51937,22/04/2013,A2-159,A1-079,,28/11/2025 17:10,,,,735
Giovanni Morais dos Santos,51139,02/04/2012,A2-285,A1-179,A2-544,07/12/2025 23:08,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:08,510
Aline Alves Esperança,13535,30/01/2008,A2-390,A1-133,A2-264,04/12/2025 17:28,(41) 99781-3606,(41) 99781-3606,04/12/2025 17:28,74
Fernanda Cavalet,281797,03/11/2021,A2-286,A1-035,,28/11/2025 20:32,,,,993
Valeska Miranda,52715,28/07/2014,A2-011,A1-142,,28/11/2025 20:36,,,,967
Ana Paula Santana Hey,52212,24/02/2014,A2-194,A1-171,,28/11/2025 20:38,,,,835
Camila de Souza Silva,285630,19/07/2022,A2-011,A1-080,A2-093,07/12/2025 16:03,(41) 99781-3606,(41) 99781-3606,07/12/2025 16:03,1096
Marli Oliveira Ribeiro,50395,25/11/2010,A2-327,A1-084,,02/12/2025 23:44,(41) 99781-3606,(41) 99781-3606,02/12/2025 23:44,291
Ana Claudia Wingert Correa,291936,25/10/2023,A2-352,A1-025,A2-046,29/11/2025 01:53,(41) 99781-3606,(41) 99781-3606,29/11/2025 01:53,1254
Gislene Maria Nuernberg Dalmolin,51303,18/06/2012,A2-374,A1-098,A2-317,07/12/2025 21:21,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:21,539
Lucas Cesar Rego,15017,06/08/2010,A2-102,,A2-472,29/11/2025 12:47,(41) 99781-3606,(41) 99781-3606,29/11/2025 12:47,197
Marcio Dantas Pinheiro,284110,04/04/2022,A2-367,A1-095,A2-177,30/11/2025 16:33,(41) 99781-3606,(41) 99781-3606,30/11/2025 16:33,1033
Jocieli Sander Mendes Acordi,52680,17/07/2014,A2-396,,A2-213,01/12/2025 02:55,(41) 99781-3606,(41) 99781-3606,01/12/2025 02:55,952
Andrezza Naima Attuy Schmitt,52167,07/01/2014,A2-087,A1-123,A2-241,05/12/2025 01:28,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:28,822
Bruna do Nascimento Tulio Balmant,285535,25/07/2022,A2-035,A1-061,A2-150,08/12/2025 01:41,(41) 99659-1926,(41) 99659-1926,08/12/2025 01:41,1105
Mahielly Ribeiro,286031,05/09/2022,A2-325,A1-104,A2-197,06/12/2025 02:24,(42) 99999-4903,(42) 99999-4903,06/12/2025 02:24,1181
Victória Kinaski Gonçalves,269905,04/07/2022,A2-168,A1-076,A2-130,07/12/2025 15:54,(41) 99781-3606,(41) 99781-3606,07/12/2025 15:54,1058
Manoella Rosane da Silva,51552,04/09/2012,A2-408,,A2-582,01/12/2025 15:46,(41) 99781-3606,(41) 99781-3606,01/12/2025 15:46,589
Monica Harumi Yabiku,282503,10/01/2022,A2-296,A1-148,,01/12/2025 16:29,(41) 99781-3606,(41) 99781-3606,01/12/2025 16:29,1018
Yves Ritondim Toregeani,50069,25/10/2010,A2-256,A1-133,A2-267,07/12/2025 23:09,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:09,253
Kelly Cristina Ferri,284337,03/06/2022,A2-352,A1-061,A2-159,07/12/2025 11:41,(41) 98798-1984,(41) 99781-3606,07/12/2025 11:41,1050
Débora Maria Sampaio Wojakevicz,282481,16/12/2021,A2-387,,A2-361,01/12/2025 17:10,(47) 98846-3737,(47) 98846-3737,01/12/2025 17:10,1017
Daniel Kummer de Oliveira,21293,26/10/2021,A2-286,A1-037,,03/12/2025 21:28,(45) 99980-1630,(41) 99781-3606,03/12/2025 21:28,992
Dayane Bianca Surek,15015,09/08/2010,A2-048,A1-075,A2-149,02/12/2025 16:47,(41) 99781-3606,(41) 99781-3606,02/12/2025 16:47,201
Daiane Eloisa da Trindade,51784,10/01/2013,A2-062,A1-034,,01/12/2025 18:29,(41) 99781-3606,(41) 99781-3606,01/12/2025 18:29,678
Almir das Neves,288911,14/03/2023,A2-337,,A2-543,05/12/2025 19:28,(41) 99781-3606,(42) 99982-5296,05/12/2025 19:28,1199
Maira Cristina Barcos de Araújo Daros,52001,16/07/2013,A2-330,A1-028,A2-152,01/12/2025 18:58,(41) 99781-3606,(41) 99781-3606,01/12/2025 18:58,758
Simone Benevenuto Andrade Araujo,286007,05/08/2022,A2-214,A1-165,A2-200,08/12/2025 02:44,(51) 99865-4686,(42) 99999-4903,08/12/2025 02:44,1138
Thaise Fernanda Dias de Figueiredo,52529,23/06/2014,A2-255,A1-132,A2-267,02/12/2025 12:41,(44) 98405-9858,(41) 99781-3606,02/12/2025 12:41,910
Priscilla Cristina dos Santos de Oliveira,14041,05/08/2008,A2-262,A1-134,,02/12/2025 13:44,(41) 99781-3606,(41) 99781-3606,02/12/2025 13:44,130
Marcia Regina de Santana,10200,08/08/2000,A2-067,A1-033,,02/12/2025 16:48,(41) 99781-3606,(41) 99781-3606,02/12/2025 16:48,17
Elisangela Cristine Ercole Stec,14793,25/01/2010,A2-385,A1-084,,02/12/2025 16:48,(41) 99781-3606,(41) 99781-3606,02/12/2025 16:48,186
Jullianny Lima dos Reis,289214,03/04/2023,A2-325,A1-061,A2-121,06/12/2025 21:55,(41) 99781-3606,(41) 99781-3606,06/12/2025 21:55,1218
Harryson Alves da Cruz,52068,08/10/2013,A2-093,A1-083,A2-161,06/12/2025 15:59,(41) 99781-3606,(41) 99781-3606,06/12/2025 15:59,784
Jacqueline de Fatima Percegona,50411,30/11/2010,A2-321,A1-068,A2-142,02/12/2025 17:54,(41) 99781-3606,(41) 99781-3606,02/12/2025 17:54,300
Andreia Cardoso da Silva,13244,10/10/2007,A2-267,A1-132,,02/12/2025 17:55,(41) 99781-3606,(41) 99781-3606,02/12/2025 17:55,36
Anna Carolina Imbelloni Brandalise,51591,05/10/2012,A2-351,A1-023,A2-129,02/12/2025 17:56,(41) 99781-3606,(41) 99781-3606,02/12/2025 17:56,614
Vinicius Barbosa Franco,50551,03/01/2011,A2-166,A1-092,,02/12/2025 17:58,(41) 99781-3606,(41) 99781-3606,02/12/2025 17:58,372
Aline Moreira,52320,20/05/2014,A2-030,,A2-369,02/12/2025 17:59,(41) 99781-3606,(41) 99781-3606,02/12/2025 17:59,858
João Victor Santos Nogueira,51702,28/11/2012,A2-235,A1-056,A2-514,02/12/2025 23:38,(41) 99781-3606,(41) 99781-3606,02/12/2025 23:38,644
Maribel Canali,51805,21/01/2013,A2-044,A1-066,,02/12/2025 19:45,(41) 99781-3606,(41) 99781-3606,02/12/2025 19:45,685
Magno Andre Miranda Januario,288901,31/03/2023,A2-328,,A2-385,02/12/2025 23:39,(41) 99781-3606,(41) 99781-3606,02/12/2025 23:39,1213
Monica Mendes Costa,286000,24/10/2022,A2-324,A1-164,A2-323,02/12/2025 23:41,(41) 99781-3606,(41) 99781-3606,02/12/2025 23:41,1195
Vinicius Colares do Vale,285468,02/08/2022,A2-244,,A2-489,07/12/2025 18:20,(85) 99924-7334,(41) 99781-3606,07/12/2025 18:20,1132
Josinéia de Lucas Volpato,51197,02/05/2012,A2-366,A1-126,,03/12/2025 17:16,(41) 99781-3606,(41) 99781-3606,03/12/2025 17:16,516
Gleice Vian da Silva,285997,15/08/2022,A2-028,A1-071,A2-134,03/12/2025 17:17,(41) 99781-3606,(41) 99781-3606,03/12/2025 17:17,1157
Giseli Caroline Leonardi,15030,10/08/2010,A2-159,A1-078,,04/12/2025 01:16,(41) 99852-6855,(41) 99781-3606,04/12/2025 01:16,204
Thiago Lucas Penteado Dutra,51696,28/11/2012,A2-336,,A2-340,03/12/2025 19:59,(41) 99781-3606,(41) 99781-3606,03/12/2025 19:59,643
Rafael Casagrande,50594,10/01/2011,A2-063,A1-038,A2-066,04/12/2025 13:10,(41) 99781-3606,(41) 99781-3606,04/12/2025 13:10,380
Gabriel Adão Faedo,50366,10/12/2010,A2-185,A1-035,A2-072,03/12/2025 21:27,(41) 99781-3606,(41) 99781-3606,03/12/2025 21:27,335
Ernesto Mataran Neto,291945,11/09/2023,A2-485,A1-162,A2-482,04/12/2025 16:59,(41) 99781-3606,(41) 99781-3606,04/12/2025 16:59,1248
Josane Salete Sebben,8906,26/07/2000,A2-457,A1-105,A2-487,04/12/2025 17:00,(41) 99781-3606,(41) 99781-3606,04/12/2025 17:00,16
Adilson Carvalho,51722,26/11/2012,A2-311,A1-156,,04/12/2025 18:40,(41) 99781-3606,(41) 99781-3606,04/12/2025 18:40,640
Wagner Verschoor,52278,22/04/2014,A2-305,A1-062,A2-167,07/12/2025 21:17,(42) 99915-1717,(41) 99781-3606,07/12/2025 21:17,852
Urbano Santana de Oliveira Júnior,284333,25/07/2022,A2-189,A1-122,A2-250,04/12/2025 22:10,(17) 98222-6188,(17) 98222-6188,04/12/2025 22:10,1103
Kamila Anne Carvalho da Silva,285540,29/08/2022,A2-035,A1-052,A2-159,08/12/2025 02:39,(41) 99624-8850,(41) 99624-8850,08/12/2025 02:39,1178
Meiri Angela Fernandes dos Reis,51833,05/02/2013,A2-232,,A2-505,05/12/2025 01:18,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:18,695
Vania Costa Gusmão,51016,08/11/2011,A2-399,A1-136,,05/12/2025 01:19,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:19,478
Luana Ines Reichow,13848,21/07/2008,A2-159,A1-069,A2-155,05/12/2025 01:20,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:20,101
Ana Carolina Brostolin,50766,27/05/2011,A2-381,A1-076,A2-150,05/12/2025 01:21,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:21,420
Cris Everton Maia Helleis,13481,02/01/2008,A2-423,A1-104,,05/12/2025 01:22,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:22,71
Thomas Gabriel Tanaka,285504,23/08/2022,A2-328,A1-164,,05/12/2025 01:23,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:23,1169
Emanuelly Ludwig de Athayde,10585,07/10/2002,A2-063,A1-105,A2-285,05/12/2025 01:24,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:24,23
Marcelo Henrique Colossi,52337,26/05/2014,A2-396,A1-175,A2-334,07/12/2025 23:09,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:09,867
Patricia Harumi Arai,13143,02/05/2007,A2-239,A1-124,,05/12/2025 01:26,(41) 99781-3606,(41) 99781-3606,05/12/2025 01:26,33
Gustavo Henrique Bach,280902,29/07/2022,A2-404,A1-174,A2-334,07/12/2025 23:34,(42) 99802-3435,(41) 99781-3606,07/12/2025 23:34,1120
Yumi Rocha Hashimoto,291951,08/01/2024,A2-041,A1-089,A2-538,05/12/2025 12:59,(41) 99781-3606,(41) 99781-3606,05/12/2025 12:59,1263
Rodrigo Kawashima Gomes,285742,08/08/2022,A2-398,A1-211,,05/12/2025 15:25,(41) 99781-3606,(41) 99781-3606,05/12/2025 15:25,1145
Alisson Bacchi de Oliveira,51778,13/12/2012,A2-539,,A2-544,05/12/2025 15:28,(41) 99781-3606,(41) 99781-3606,05/12/2025 15:28,669
Rafael Marcato,52537,24/06/2014,A2-060,,A2-457,05/12/2025 15:31,(41) 99781-3606,(41) 99781-3606,05/12/2025 15:31,914
Luiz Pereira Rocha,285511,25/07/2022,A2-064,A1-094,A2-182,05/12/2025 15:33,(41) 99781-3606,(41) 99781-3606,05/12/2025 15:33,1102
Otavio Augusto Oliveira da Silva Albuquerque,289201,31/03/2023,A2-074,A1-069,,06/12/2025 15:57,(41) 98868-2140,(41) 99781-3606,06/12/2025 15:57,1215
Junia Flavia Azevedo Sampaio,52137,29/11/2013,A2-047,,A2-204,05/12/2025 17:13,(41) 99781-3606,(41) 99781-3606,05/12/2025 17:13,810
Larissa Maria Kiil da Silva Ferraz,50809,30/05/2011,A2-087,A1-053,A2-092,05/12/2025 17:14,(41) 99781-3606,(41) 99781-3606,05/12/2025 17:14,422
Greiciane Inocence Marques Burbello,278488,27/07/2022,A2-079,A1-069,A2-149,05/12/2025 17:15,(41) 99781-3606,(41) 99781-3606,05/12/2025 17:15,1110
Ana Carolina Baratieri,50733,10/03/2011,A2-109,A1-071,A2-137,05/12/2025 17:23,(41) 99781-3606,(41) 99781-3606,05/12/2025 17:23,413
Perpetua Machado,14805,22/01/2010,A2-481,,A2-186,05/12/2025 17:23,(41) 99781-3606,(41) 99781-3606,05/12/2025 17:23,185
Claudia Josiani dos Santos Zaltrão,51777,14/12/2012,A2-129,A1-084,A2-119,07/12/2025 21:20,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:20,671
Pedro Henrique Tadra,51463,13/08/2012,A2-351,A1-054,,05/12/2025 17:43,(41) 99663-2845,(41) 99663-2845,05/12/2025 17:43,580
Juliana Goellner,285934,26/09/2022,A2-354,A1-083,A2-121,05/12/2025 17:49,(41) 99781-3606,(41) 99781-3606,05/12/2025 17:49,1191
Rodolfo Ferreira de Pinho dos Santos,282499,07/12/2021,A2-288,A1-225,A2-273,07/12/2025 02:52,(21) 99043-2004,(41) 99781-3606,07/12/2025 02:52,1008
Dalva Pereira de Mendonca,285547,08/08/2022,A2-225,A1-137,,05/12/2025 20:15,(41) 99781-3606,(41) 99781-3606,05/12/2025 20:15,1140
Elton Jose de Lima,282480,14/01/2022,A2-402,A1-155,,05/12/2025 20:16,(41) 99781-3606,(41) 99781-3606,05/12/2025 20:16,1023
Mailson Block Bueno,50822,01/06/2011,A2-334,A1-176,,05/12/2025 21:37,(41) 99781-3606,(41) 99781-3606,05/12/2025 21:37,424
Paula Nicolau,285653,12/07/2022,A2-296,A1-148,A2-295,05/12/2025 21:38,(41) 99781-3606,(41) 99781-3606,05/12/2025 21:38,1070
Gislene Soares de Almeida,50221,17/11/2010,A2-327,A1-084,A2-161,06/12/2025 01:33,(41) 99781-3606,(41) 99781-3606,06/12/2025 01:33,282
Geanete Aparecida Caldas,51821,30/01/2013,A2-197,A1-064,A2-121,06/12/2025 01:40,(42) 99974-6557,(41) 99781-3606,06/12/2025 01:40,691
Israel Moreira Gonçalves Feltrin Thimoteo,274900,12/07/2022,A2-410,A1-037,,06/12/2025 01:34,(41) 99781-3606,(41) 99781-3606,06/12/2025 01:34,1077
Ana Paula Picolo Pecuch,50130,29/10/2010,A2-121,A1-084,,06/12/2025 01:36,(41) 99781-3606,(41) 99781-3606,06/12/2025 01:36,263
Angela Mayumi Nagata Farias,52545,07/07/2014,A2-271,A1-164,,06/12/2025 01:37,(41) 99781-3606,(41) 99781-3606,06/12/2025 01:37,982
Silvia Cristine Martins Inaba,14840,05/02/2010,A2-273,A1-131,A2-275,07/12/2025 00:20,(41) 99781-3606,(44) 98409-5131,07/12/2025 00:20,190
Gabriel Mudrey Vieira Pedroso,282938,21/09/2022,A2-297,A1-067,A2-167,07/12/2025 02:54,(41) 99781-3606,(41) 99781-3606,07/12/2025 02:54,1189
Adriana Sayuri Ikeno,284068,11/04/2022,A2-188,A1-135,A2-264,07/12/2025 21:59,(44) 99945-9999,(41) 99781-3606,07/12/2025 21:59,1039
Madalena Ferreira de Castilhos,10250,01/02/2001,A2-200,A1-077,A2-156,06/12/2025 19:53,(41) 99852-6855,(41) 99781-3606,06/12/2025 19:53,18
Eliseu Souza,286040,09/08/2022,A2-189,A1-162,A2-164,06/12/2025 15:55,(41) 99781-3606,(41) 99781-3606,06/12/2025 15:55,1151
Júlio Ubiraí Geraldo Gomes,51566,20/09/2012,A2-021,A1-120,,06/12/2025 15:56,(41) 99781-3606,(41) 99781-3606,06/12/2025 15:56,599
Luciana Iácono Marino Paleo,51031,18/11/2011,A2-302,A1-126,,06/12/2025 15:56,(41) 99781-3606,(41) 99781-3606,06/12/2025 15:56,486
Rafael Plinta,284332,02/05/2022,A2-054,A1-201,A2-385,07/12/2025 21:18,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:18,1044
Luana da Cruz Souza Plinta,281800,16/11/2021,A2-054,A1-201,A2-386,07/12/2025 21:18,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:18,999
Raphael Victor Gatto Costa,284070,04/04/2022,A2-404,A1-083,A2-157,08/12/2025 02:48,(41) 99781-3606,(41) 99663-2845,08/12/2025 02:48,1034
Vivian Ettore Fernandes,286009,22/08/2022,A2-163,A1-070,,06/12/2025 19:54,(41) 99781-3606,(41) 99781-3606,06/12/2025 19:54,1168
David Augusto de Oliveira Morais,286050,09/08/2022,A2-521,A1-033,A2-406,07/12/2025 21:17,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:17,1149
Heidy Cristine Arendt,52633,07/07/2014,A2-189,A1-029,A2-164,06/12/2025 21:38,(41) 99781-3606,(41) 99781-3606,06/12/2025 21:38,928
Karina Teresinha Muehlbauer,289205,30/03/2023,A2-230,A1-090,,07/12/2025 21:54,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:54,1212
Renan Celso Maksemiv Machado,50325,30/11/2010,A2-004,A1-065,,06/12/2025 21:40,(41) 99781-3606,(41) 99781-3606,06/12/2025 21:40,301
Sonia Maria Morandini Pereira,14138,18/08/2008,A2-187,,A2-481,06/12/2025 21:41,(41) 99781-3606,(41) 99781-3606,06/12/2025 21:41,134
Marcelo Bisinella,50675,01/02/2011,A2-334,A1-176,,07/12/2025 02:55,(41) 99781-3606,(41) 99781-3606,07/12/2025 02:55,395
Danilo Antonio Dutra,261602,22/08/2022,A2-527,A1-084,A2-323,07/12/2025 02:57,(41) 99781-3606,(41) 99781-3606,07/12/2025 02:57,1167
João Manoel Araujo Mazetto,15014,06/08/2010,A2-450,A1-027,,07/12/2025 11:32,(41) 99781-3606,(41) 99781-3606,07/12/2025 11:32,198
Lucas Cavalheiro Ferreira Bueno,51353,11/07/2012,A2-088,A1-188,A2-137,07/12/2025 23:36,(41) 99852-6855,(41) 99781-3606,07/12/2025 23:36,548
Jussara Barbosa de Souza Santos,51909,22/03/2013,A2-020,A1-124,A2-249,07/12/2025 15:32,(41) 99781-3606,(41) 99781-3606,07/12/2025 15:32,723
Ercília Vieira Leonel Lima,50331,26/11/2010,A2-385,A1-038,,07/12/2025 15:35,(41) 99781-3606,(41) 99781-3606,07/12/2025 15:35,297
Renata Maurente Rodrigues,275968,12/09/2022,A2-224,A1-075,,07/12/2025 15:37,(41) 99781-3606,(41) 99781-3606,07/12/2025 15:37,1186
Wilson Ebsen,50018,20/08/2010,A2-389,,A2-392,07/12/2025 15:38,(41) 99781-3606,(41) 99781-3606,07/12/2025 15:38,222
Iris Lindbeck Guimaraes,14332,18/12/2008,A2-070,A1-082,,07/12/2025 17:01,(41) 99781-3606,(41) 99781-3606,07/12/2025 17:01,148
Daphne Raiocovitch Tostes,291937,01/11/2023,A2-303,A1-134,,07/12/2025 17:20,(41) 99781-3606,(41) 99781-3606,07/12/2025 17:20,1256
Paulo Henrique Rodrigues,286032,29/08/2022,A2-188,A1-029,A2-053,07/12/2025 17:21,(41) 99781-3606,(41) 99781-3606,07/12/2025 17:21,1176
Matheus Coli Pires,285938,08/08/2022,A2-218,A1-012,A2-020,07/12/2025 18:27,(41) 99781-3606,(43) 99919-6949,07/12/2025 18:27,1152
Natália Prandi Manzano,51665,07/11/2012,A2-295,A1-137,A2-275,07/12/2025 17:24,(41) 99781-3606,(41) 99781-3606,07/12/2025 17:24,959
Joelsio Jose Rottini,52631,09/07/2014,A2-503,A1-043,A2-564,07/12/2025 22:43,(46) 98827-4385,(46) 98827-4385,07/12/2025 22:43,937
Paulo Henrique Pietrangelo Lima,13952,28/07/2008,A2-270,A1-136,A2-279,07/12/2025 21:13,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:13,112
Francielle Men Boaretto,14810,03/02/2010,A2-262,,A2-278,07/12/2025 23:17,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:17,188
Claudio Laurindo Granja,50091,20/10/2010,A2-159,,A2-473,07/12/2025 23:39,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:39,243
Heverton Crystian Matozo,52572,07/07/2014,A2-533,A1-069,A2-473,07/12/2025 21:26,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:26,933
Bruna Maran Rosa,50919,03/08/2011,A2-421,A1-138,,07/12/2025 21:42,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:42,590
Kenny Tsushima,50025,02/09/2010,A2-452,,A2-473,07/12/2025 21:43,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:43,231
Sueli Barbosa Rufino Michelan,14135,29/07/2008,A2-273,A1-136,A2-277,07/12/2025 21:44,(41) 99781-3606,(41) 99781-3606,07/12/2025 21:44,119
Luciana Almeida Tomé,51107,15/02/2012,A2-386,A1-201,,07/12/2025 23:04,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:04,503
Carlos Frederico Loureiro Bracarense Costa,285470,14/07/2022,A2-245,,A2-505,07/12/2025 23:06,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:06,1079
Yara Pacheco dos Santos,51068,05/12/2011,A2-088,A1-072,A2-133,07/12/2025 23:37,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:37,495
Cristiano dos Santos Badluk,288905,17/03/2023,A2-351,A1-076,,07/12/2025 23:12,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:12,1202
Anderson José Rodrigues da Silva,52015,18/07/2013,A2-108,A1-132,,07/12/2025 23:12,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:12,760
Tatiana Riccomini Munhoz,51325,15/06/2012,A2-256,A1-136,A2-271,07/12/2025 23:41,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:41,536
Matheus Antonio Diaz Motta,222460,05/08/2022,A2-371,A1-201,,07/12/2025 23:36,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:36,1139
Luciane da Cruz Rodrigues da Silva,51908,25/03/2013,A2-113,A1-072,,07/12/2025 23:39,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:39,724
Rubia Souza Pimenta de Padua,52385,02/06/2014,A2-250,A1-124,,07/12/2025 23:40,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:40,883
Marco Antonio Moreira de Araujo,281786,14/01/2022,A2-311,,A2-304,07/12/2025 23:47,(41) 99781-3606,(41) 99781-3606,07/12/2025 23:47,1024"""

    script_dir = Path(__file__).parent
    inscr_proc_path = script_dir / 'inscricoes_reais_processadas.csv'
    output_path = script_dir / 'base_atualizada.csv'

    if not inscr_proc_path.exists():
        print(f"❌ Arquivo não encontrado: {inscr_proc_path}")
        sys.exit(1)

    mesclar_dados(BASE_EXISTENTE, str(inscr_proc_path), str(output_path))
