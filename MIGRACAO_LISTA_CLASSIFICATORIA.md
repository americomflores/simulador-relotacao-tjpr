# Relatório de Migração - Lista Classificatória Edital 04/2025

## ✅ Mudanças Implementadas

### 1. Extração de Dados dos PDFs

**Status:** ✅ Concluído

- Script criado: `scripts/extrair_lista_classificatoria.py`
- PDFs processados: 7 arquivos
- Servidores extraídos: **1.268 posições**
- Posições: 1 a 1.268 (sequenciais)
- Homônimos detectados: **0** (nenhum nome duplicado)
- Arquivo gerado: `lista_classificatoria.py`

**Estrutura de dados:**
```python
LISTA_CLASSIFICATORIA = {
    1: {
        "nome": "BEATRIZ ANETTE GLITZ LAUER",
        "nome_original": "BEATRIZ ANETTE GLITZ LAUER",
        "nome_display": "BEATRIZ ANETTE GLITZ LAUER",
        "inicio_cargo": "16/01/1989",
        "tempo_cargo": "36 anos, 10 meses e 24 dias",
        "tempo_poder_judiciario": "36 anos, 10 meses e 24 dias",
        "tempo_servico_publico": "39 anos, 9 meses e 17 dias",
        "data_nascimento": "28/01/1964",
        "lotacao": "...",
        "localizacao_principal": "..."
    },
    # ... até posição 1268
}
```

### 2. Migração de Inscrições Existentes

**Status:** ⚠️ Parcialmente Concluído

- Script criado: `scripts/migrar_inscricoes_existentes.py`
- Registros processados: **146 servidores**
- Migrados automaticamente (≥95%): **145** (99.3%)
- Requer revisão manual (85-94%): **1** (0.7%)
  - Guilherme Cravetz Assumpção Marques → 94% match (apenas diferença de acentuação)
- Não encontrados (<85%): **0**

**Fuzzy Matching:**
- Threshold de 95% para migração automática
- Threshold de 85% para revisão manual
- Nomes comparados sem case-sensitivity
- Tratamento correto de acentuação (UTF-8)

### 3. Mapeamento Telefone → Posição

**Status:** ⚠️ **CRÍTICO - REQUER AÇÃO**

- Arquivo gerado: `config/telefone_posicao_map.py`
- Mapeamentos criados: **19 telefones únicos**
- Registros sem telefone: **35 servidores** (23.9%)

**PROBLEMA IDENTIFICADO:**

A maioria das inscrições no CSV foi registrada usando o telefone do admin (41997813606), não o telefone do próprio servidor. Isso resulta em apenas 19 telefones únicos mapeados, significando que **apenas 19 servidores poderão fazer login no novo sistema**.

**Telefones mapeados:**
1. 41998526855 → Posição 18
2. 41997813606 → Posição 134
3. 41996632845 → Posição 580
4. 42999746557 → Posição 691
5. ... (total de 19)

### 4. Atualização da Estrutura de Dados

**Status:** ✅ Concluído

#### Google Sheets (`services/sheets_service.py`)

**Mudanças:**
- Nova coluna adicionada: `posicao_lista_classificatoria` (coluna K)
- Tipo de dados: Int64 (pandas nullable integer)
- Compatibilidade retroativa: Registros antigos sem posição recebem `NA`

**Estrutura atualizada:**
```
A: nome
B: matricula
C: data_admissao (MANTIDO para validação probatório)
D: lotacao_atual
E: escolha_anexo1
F: escolha_anexo2
G: data_inscricao
H: registrado_por
I: alterado_por
J: data_alteracao
K: posicao_lista_classificatoria (NOVO)
```

#### Lógica de Simulação (`services/simulacao_service.py`)

**Mudanças:**
- Linha 143: Ordenação alterada de `data_admissao` para `posicao_lista_classificatoria`
- Linha 146: `posicao_antiguidade` agora reflete `posicao_lista_classificatoria` (compatibilidade)
- **MANTIDO:** Validação de estágio probatório (`DATA_LIMITE_ESTAGIO = 26/11/2022`)

**Antes:**
```python
df = df.sort_values("data_admissao", ascending=True)
df["posicao_antiguidade"] = range(1, len(df) + 1)
```

**Depois:**
```python
df = df.sort_values("posicao_lista_classificatoria", ascending=True)
df["posicao_antiguidade"] = df["posicao_lista_classificatoria"]
```

#### Sistema de Autenticação (`config/auth_config.py`)

**Mudanças:**
- Códigos agora gerados dinamicamente: `TJPR-{posicao:03d}`
- Importa `LISTA_CLASSIFICATORIA` e `TELEFONE_POSICAO_MAP`
- Função `gerar_auth_codes()` cria códigos automaticamente
- Códigos legados movidos para `DEFAULT_AUTH_CODES_LEGACY` (deprecado)

**Exemplos de novos códigos:**
- Posição 1 → `TJPR-001`
- Posição 18 → `TJPR-018`
- Posição 134 → `TJPR-134`
- Posição 1268 → `TJPR-1268`

### 5. Dependências Adicionadas

**Status:** ✅ Concluído

Adicionado ao `requirements.txt`:
```
pdfplumber>=0.10.0      # Extração de PDFs
fuzzywuzzy>=0.18.0      # Matching de nomes
python-Levenshtein>=0.21.0  # Aceleração fuzzy match
```

---

## ⚠️ PROBLEMAS CRÍTICOS A RESOLVER

### 1. Autenticação Limitada (CRÍTICO)

**Problema:**
Apenas **19 servidores** dos 146 inscritos têm telefone mapeado, pois a maioria das inscrições foi feita pelo admin usando seu próprio telefone.

**Impacto:**
- 127 servidores (87%) **NÃO poderão fazer login** no sistema atual
- Apenas 19 telefones mapeados para 1268 posições possíveis

**Soluções Possíveis:**

#### Opção A: Coletar Telefones Manualmente
- Criar planilha de coleta de telefones
- Enviar para todos os 146 servidores inscritos
- Atualizar `telefone_posicao_map.py` manualmente
- Prazo: 1-2 semanas

#### Opção B: Adicionar Coluna no Google Sheets
- Adicionar coluna "telefone_servidor" no Sheets
- Admin preenche telefone de cada servidor
- Gerar novo `telefone_posicao_map.py` a partir do Sheets
- Prazo: Imediato (requer trabalho manual)

#### Opção C: Sistema Temporário de Cadastro
- Criar interface temporária para servidores cadastrarem telefone
- Validar com dados da lista (nome + matrícula)
- Gerar mapeamento automaticamente
- Prazo: 2-3 dias de desenvolvimento

**Recomendação:** Opção B (mais rápido) seguida por Opção C (mais escalável)

### 2. Revisão Manual Necessária

**Problema:**
1 servidor com match de 94% precisa de confirmação manual:

```
Nome no CSV: "Guilherme Cravetz Assumpção Marques"
Sugestão: Pos 991 - "GUILHERME CRAVETZ ASSUMPCAO MARQUES"
```

**Ação:** Confirmar se é a mesma pessoa (provavelmente sim, diferença apenas em "ç" vs "c")

### 3. Atualização do Google Sheets em Produção

**Problema:**
A estrutura do Google Sheets mudou (nova coluna K), mas os dados existentes não têm `posicao_lista_classificatoria`.

**Ação Necessária:**

1. **Fazer backup completo do Google Sheets atual**
2. **Adicionar coluna K** com cabeçalho `posicao_lista_classificatoria`
3. **Executar script de preenchimento** (ainda não criado):
   - Ler cada registro
   - Fazer fuzzy match do nome com `LISTA_CLASSIFICATORIA`
   - Atualizar coluna K com a posição
   - Gerar relatório de registros não encontrados

4. **Validar resultados** antes de colocar em produção

**Script necessário:** `scripts/atualizar_sheets_com_posicoes.py` (NÃO CRIADO)

---

## 📋 Próximos Passos Recomendados

### Fase 1: Preparação (ANTES de modificar produção)

1. ✅ Criar e testar scripts de extração (CONCLUÍDO)
2. ✅ Criar e testar scripts de migração (CONCLUÍDO)
3. ⏳ **Resolver problema de telefones** (PENDENTE - CRÍTICO)
   - Definir estratégia (Opção A, B ou C)
   - Executar coleta de telefones
   - Atualizar `telefone_posicao_map.py`
4. ⏳ Criar script para atualizar Google Sheets com posições
5. ⏳ Testar localmente com dados de produção (cópia)

### Fase 2: Migração de Dados

6. ⏳ Fazer backup completo do Google Sheets
7. ⏳ Adicionar coluna K ao Google Sheets
8. ⏳ Executar script de atualização de posições
9. ⏳ Validar resultados (conferir amostra de 20-30 registros)
10. ⏳ Resolver casos de revisão manual (1 registro)

### Fase 3: Deploy do Código

11. ⏳ Atualizar `app.py` (interface) - **NÃO INICIADO**
    - Adicionar busca automática de posição no formulário
    - Exibir "Posição Lista" ao invés de "Antiguidade"
    - Validar servidor está na lista antes de permitir inscrição
    - Atualizar mensagens e labels
12. ⏳ Testar sistema completo localmente
13. ⏳ Deploy em produção
14. ⏳ Monitorar logs e erros

---

## 🔧 Arquivos Modificados

### Criados:
- `scripts/extrair_lista_classificatoria.py`
- `scripts/migrar_inscricoes_existentes.py`
- `scripts/debug_pdf.py` (auxiliar)
- `lista_classificatoria.py`
- `config/telefone_posicao_map.py`
- `MIGRACAO_LISTA_CLASSIFICATORIA.md` (este arquivo)

### Modificados:
- `requirements.txt` (adicionadas 3 dependências)
- `services/sheets_service.py` (nova coluna K)
- `services/simulacao_service.py` (ordenação por posição)
- `config/auth_config.py` (AUTH_CODES dinâmicos)

### Pendentes:
- `app.py` (interface - NÃO INICIADO)
- `scripts/atualizar_sheets_com_posicoes.py` (NÃO CRIADO)

---

## 📊 Estatísticas

### Extração de PDFs
- Total de PDFs: 7
- Total de servidores: 1.268
- Homônimos: 0
- Posições: 1-1268 (completo e sequencial)

### Migração de Inscrições
- Total de registros CSV: 146
- Match automático (≥95%): 145 (99.3%)
- Requer revisão (85-94%): 1 (0.7%)
- Não encontrados (<85%): 0 (0.0%)
- Sem telefone: 35 (23.9%)
- Telefones únicos mapeados: 19 (13.0%)

### Sistema de Autenticação
- AUTH_CODES gerados: 19
- Servidores com acesso: 19 de 146 (13.0%) ⚠️
- Formato de código: `TJPR-{posicao:03d}`

---

## ⚙️ Comandos Úteis

### Executar Extração de PDFs
```bash
python scripts/extrair_lista_classificatoria.py
```

### Executar Migração de Inscrições
```bash
python scripts/migrar_inscricoes_existentes.py
```

### Instalar Dependências
```bash
pip install -r requirements.txt
```

### Testar Importação de Módulos
```python
from lista_classificatoria import LISTA_CLASSIFICATORIA
from config.telefone_posicao_map import TELEFONE_POSICAO_MAP
from config.auth_config import gerar_auth_codes

print(f"Lista: {len(LISTA_CLASSIFICATORIA)} servidores")
print(f"Telefones: {len(TELEFONE_POSICAO_MAP)} mapeamentos")
print(f"AUTH_CODES: {len(gerar_auth_codes())} códigos")
```

---

## 📝 Notas Técnicas

### Fuzzy Matching
- Biblioteca: `fuzzywuzzy` com `python-Levenshtein`
- Algoritmo: Levenshtein ratio
- Thresholds:
  - ≥95%: Migração automática
  - 85-94%: Revisão manual
  - <85%: Não encontrado
- Case-insensitive
- Suporta acentuação correta (UTF-8)

### Estrutura de Dados
- `LISTA_CLASSIFICATORIA`: Dicionário {posição: dados}
- `TELEFONE_POSICAO_MAP`: Dicionário {telefone: posição}
- `AUTH_CODES`: Dicionário {telefone: código} (gerado dinamicamente)

### Ordenação
- **Antes:** Por `data_admissao` (mais antigo = prioridade)
- **Depois:** Por `posicao_lista_classificatoria` (menor número = prioridade)
- **Validação adicional:** Estágio probatório (mantida)

---

## ❗ Avisos Importantes

1. **NÃO MODIFICAR manualmente `lista_classificatoria.py`** - é auto-gerado
2. **NÃO MODIFICAR manualmente `telefone_posicao_map.py`** sem revisar o script de geração
3. **FAZER BACKUP** do Google Sheets antes de qualquer alteração de estrutura
4. **TESTAR LOCALMENTE** todas as mudanças antes de deploy em produção
5. **COLETAR TELEFONES** de todos os servidores é **CRÍTICO** para o funcionamento do sistema

---

## 🔍 Validações Realizadas

✅ PDFs extraídos corretamente (1268 registros)
✅ Posições sequenciais (1-1268, sem gaps)
✅ Fuzzy matching funcional (99.3% de precisão)
✅ Encoding UTF-8 correto (acentuação preservada)
✅ Módulos importáveis sem erros
✅ Ordenação por posição implementada
✅ Coluna adicionada ao Sheets service
✅ AUTH_CODES gerados dinamicamente

⚠️ Apenas 19 telefones mapeados (13% dos inscritos)
⚠️ 1 registro precisa de revisão manual
⏳ Google Sheets em produção NÃO atualizado ainda
⏳ Interface `app.py` NÃO atualizada ainda

---

**Data da Migração:** 06/12/2025
**Versão do Código:** Baseado no commit `ee46ad7`
**Total de Horas:** ~4h de trabalho automatizado
