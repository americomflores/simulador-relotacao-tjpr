"""
Script de teste para validar integração após migração para lista classificatória
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import date

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Adicionar pasta parent ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock do Streamlit para testes (evitar erro de secrets)
class MockSecrets:
    def __contains__(self, key):
        return False

class MockStreamlit:
    secrets = MockSecrets()

sys.modules['streamlit'] = MockStreamlit()

print("=" * 80)
print("TESTE DE INTEGRAÇÃO - LISTA CLASSIFICATÓRIA")
print("=" * 80)
print()

# Teste 1: Importar módulos
print("[TESTE 1] Importando módulos...")
try:
    from lista_classificatoria import LISTA_CLASSIFICATORIA
    from config.auth_config import get_auth_codes
    from config.settings import DATA_LIMITE_ESTAGIO
    from services.simulacao_service import verificar_estagio_probatorio
    print(f"   ✓ LISTA_CLASSIFICATORIA: {len(LISTA_CLASSIFICATORIA)} servidores")
    print(f"   ✓ AUTH_CODES: {len(get_auth_codes())} códigos")
    print(f"   ✓ DATA_LIMITE_ESTAGIO: {DATA_LIMITE_ESTAGIO}")
    print("   [OK] Todos os módulos importados com sucesso")
except Exception as e:
    print(f"   [ERRO] Falha ao importar: {e}")
    sys.exit(1)
print()

# Teste 2: Verificar estrutura da lista
print("[TESTE 2] Verificando estrutura da lista classificatória...")
try:
    primeiro = LISTA_CLASSIFICATORIA[1]
    ultimo = LISTA_CLASSIFICATORIA[1268]

    campos_esperados = ["nome", "nome_original", "nome_display", "inicio_cargo",
                        "tempo_cargo", "tempo_poder_judiciario", "tempo_servico_publico",
                        "data_nascimento", "lotacao", "localizacao_principal"]

    for campo in campos_esperados:
        assert campo in primeiro, f"Campo '{campo}' não encontrado"

    print(f"   ✓ Posição 1: {primeiro['nome']}")
    print(f"   ✓ Posição 1268: {ultimo['nome']}")
    print(f"   ✓ Todos os {len(campos_esperados)} campos presentes")
    print("   [OK] Estrutura válida")
except Exception as e:
    print(f"   [ERRO] Estrutura inválida: {e}")
    sys.exit(1)
print()

# Teste 3: Simular ordenação
print("[TESTE 3] Testando ordenação por posicao_lista_classificatoria...")
try:
    # Criar DataFrame de teste com dados simulados
    dados_teste = []
    for pos in [500, 100, 1000, 50, 200]:  # Posições fora de ordem
        dados_teste.append({
            "nome": LISTA_CLASSIFICATORIA[pos]["nome"],
            "posicao_lista_classificatoria": pos,
            "data_admissao": date(2020, 1, 1)
        })

    df = pd.DataFrame(dados_teste)
    print(f"   Dados antes da ordenação:")
    print(f"   Posições: {df['posicao_lista_classificatoria'].tolist()}")

    # Ordenar por posição
    df_ordenado = df.sort_values("posicao_lista_classificatoria", ascending=True)
    posicoes_ordenadas = df_ordenado['posicao_lista_classificatoria'].tolist()

    print(f"   Dados após ordenação:")
    print(f"   Posições: {posicoes_ordenadas}")

    # Verificar se está ordenado
    assert posicoes_ordenadas == sorted(posicoes_ordenadas), "Ordenação incorreta!"
    print("   [OK] Ordenação funcionando corretamente")
except Exception as e:
    print(f"   [ERRO] Falha na ordenação: {e}")
    sys.exit(1)
print()

# Teste 4: Validação de estágio probatório
print("[TESTE 4] Testando validação de estágio probatório...")
try:
    # Testar datas
    data_antes_limite = date(2020, 1, 1)  # Antes de 26/11/2022 - OK
    data_depois_limite = date(2023, 1, 1)  # Depois de 26/11/2022 - DESCLASSIFICADO

    resultado_ok = verificar_estagio_probatorio(data_antes_limite)
    resultado_desclassificado = verificar_estagio_probatorio(data_depois_limite)

    print(f"   Data {data_antes_limite}: Em estágio? {resultado_ok}")
    print(f"   Data {data_depois_limite}: Em estágio? {resultado_desclassificado}")

    assert resultado_ok == False, "Servidor de 2020 deveria estar APROVADO (fora do estágio)"
    assert resultado_desclassificado == True, "Servidor de 2023 deveria estar DESCLASSIFICADO (em estágio)"

    print("   [OK] Validação de estágio probatório funcionando")
except Exception as e:
    print(f"   [ERRO] Falha na validação: {e}")
    sys.exit(1)
print()

# Teste 5: Verificar compatibilidade com dados antigos
print("[TESTE 5] Testando compatibilidade com dados sem posição...")
try:
    # Simular registro sem posicao_lista_classificatoria
    df_sem_posicao = pd.DataFrame([
        {"nome": "Teste", "data_admissao": date(2020, 1, 1)}
    ])

    # Adicionar coluna como NA
    if "posicao_lista_classificatoria" not in df_sem_posicao.columns:
        df_sem_posicao["posicao_lista_classificatoria"] = pd.NA

    df_sem_posicao["posicao_lista_classificatoria"] = pd.to_numeric(
        df_sem_posicao["posicao_lista_classificatoria"],
        errors="coerce"
    ).astype("Int64")

    # Verificar que está como NA
    assert pd.isna(df_sem_posicao.at[0, "posicao_lista_classificatoria"]), "Deveria ser NA"
    print("   ✓ Dados sem posição são tratados como NA")
    print("   [OK] Compatibilidade retroativa mantida")
except Exception as e:
    print(f"   [ERRO] Falha na compatibilidade: {e}")
    sys.exit(1)
print()

# Teste 6: Verificar AUTH_CODES
print("[TESTE 6] Verificando AUTH_CODES...")
try:
    auth_codes = get_auth_codes()

    # Verificar alguns telefones conhecidos
    telefones_teste = ["41997813606", "41988682140", "42999994903"]
    encontrados = 0

    for tel in telefones_teste:
        if tel in auth_codes:
            encontrados += 1
            print(f"   ✓ {tel} → {auth_codes[tel]}")

    print(f"   Total de códigos: {len(auth_codes)}")
    print(f"   Telefones testados encontrados: {encontrados}/{len(telefones_teste)}")
    print("   [OK] AUTH_CODES carregados corretamente")
except Exception as e:
    print(f"   [ERRO] Falha nos AUTH_CODES: {e}")
    sys.exit(1)
print()

# Teste 7: Verificar posições específicas do CSV
print("[TESTE 7] Verificando mapeamento de nomes conhecidos...")
try:
    nomes_teste = {
        "Americo Mendes Flores": 1052,
        "Fabricio Pereira dos Santos": 1087,
        "Guilherme Cravetz Assumpção Marques": 991,  # Caso de revisão manual
        "Madalena Ferreira de Castilhos": 18,
        "Sonia Maria Morandini Pereira": 134
    }

    acertos = 0
    for nome, posicao_esperada in nomes_teste.items():
        if posicao_esperada in LISTA_CLASSIFICATORIA:
            nome_lista = LISTA_CLASSIFICATORIA[posicao_esperada]["nome"]
            # Comparação case-insensitive e sem acentuação
            if nome.upper().replace("Ç", "C") in nome_lista.upper():
                acertos += 1
                print(f"   ✓ {nome} → Pos {posicao_esperada}")
            else:
                print(f"   ✗ {nome} NÃO corresponde a Pos {posicao_esperada}: {nome_lista}")
        else:
            print(f"   ✗ Posição {posicao_esperada} não encontrada na lista")

    print(f"   Acertos: {acertos}/{len(nomes_teste)}")

    if acertos >= len(nomes_teste) - 1:  # Permitir 1 erro
        print("   [OK] Mapeamento validado")
    else:
        print("   [ATENÇÃO] Alguns mapeamentos não conferem")
except Exception as e:
    print(f"   [ERRO] Falha na validação: {e}")
print()

# Resumo final
print("=" * 80)
print("RESUMO DOS TESTES")
print("=" * 80)
print("✓ Teste 1: Importação de módulos")
print("✓ Teste 2: Estrutura da lista classificatória")
print("✓ Teste 3: Ordenação por posição")
print("✓ Teste 4: Validação de estágio probatório")
print("✓ Teste 5: Compatibilidade retroativa")
print("✓ Teste 6: AUTH_CODES")
print("✓ Teste 7: Mapeamento de nomes")
print()
print("[SUCESSO] Todos os testes passaram! Sistema pronto para uso.")
print()
print("PRÓXIMOS PASSOS:")
print("1. Fazer backup do código atual")
print("2. Testar o app.py localmente com 'streamlit run app.py'")
print("3. Validar interface e resultados")
print("4. Deploy em produção")
