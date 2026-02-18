# CLAUDE.md - Simulador de Relotação TJPR

## 📋 Visão Geral do Projeto

Aplicação Streamlit para simular o processo de relotação de servidores do Tribunal de Justiça do Paraná (Edital nº 01/2026 - Técnico Judiciário).

**Stack Tecnológico:**
- Python 3.11 + Streamlit
- Pandas para processamento de dados
- Google Sheets como banco de dados (via gspread)
- Autenticação customizada (telefone + código)

## 🏗️ Estrutura de Arquivos

```
simulador-relotacao-tjpr/
├── app.py                           # Aplicação principal (~2.300 linhas; parte da lógica em services/config/utils)
├── data.py                          # ANEXO_I e ANEXO_II (vagas do edital)
├── lotacao_data.py                  # Dados de lotação paradigma das unidades
├── lista_classificatoria.py         # Lista Classificatória Edital 01/2026 (1291 servidores)
├── exceptions.py                    # Exceções do sistema (ConfigurationError, SheetsError, etc.)
├── requirements.txt                 # Dependências Python
├── .streamlit/
│   └── config.toml                 # Configuração do Streamlit
├── secrets.toml.example            # Template para credenciais Google Sheets
├── scripts/                         # Scripts de migração e utilitários
│   ├── extrair_lista_classificatoria.py    # Extrai dados dos 7 PDFs
│   ├── migrar_inscricoes_existentes.py     # Migra inscrições com fuzzy matching
│   └── atualizar_csv_com_posicoes.py       # Atualiza CSV com posições
├── services/                        # Módulos de serviços
│   ├── auth_service.py             # Autenticação e autorização (verificar_login, verificar_admin)
│   ├── sheets_service.py           # Operações com Google Sheets (implementação alternativa)
│   ├── simulacao_service.py        # Lógica de cálculo (obter_status_lotacao, calcular_lotacao_dinamica)
│   ├── search_service.py          # Busca na lista classificatória (por nome, matrícula)
│   └── rajs_service.py            # Funções de RAJs (obter_raj_da_comarca)
├── config/                          # Configurações do sistema
│   ├── auth_config.py              # AUTH_CODES, ADMIN_TELEFONES, ADMIN_SENHA (get_auth_codes, etc.)
│   ├── settings.py                 # Configurações do sistema (estágio probatório removido em 01/2026)
│   ├── constants.py                # Constantes (fuzzy match, lista, status)
│   ├── rajs_config.py             # Dados das 10 RAJs
│   └── matricula_posicao_map.py    # Mapeamento matrícula → posição na lista
├── utils/                           # Utilitários
│   ├── logger.py                   # Sistema de logging
│   ├── normalizers.py              # Normalização de strings
│   ├── validators.py               # Validações
│   ├── error_handlers.py           # Tratamento de erros (handle_error, handle_success)
│   ├── ui_components.py            # Componentes de UI (alert_box, metric_card, loading_spinner, empty_state)
│   └── ui_helpers.py              # Helpers de UI (construir_opcoes_selectbox, extrair_codigo_da_opcao, etc.)
├── tests/                           # Testes
│   ├── conftest.py                 # Fixtures pytest
│   ├── test_simulacao.py           # Testes da lógica de simulação
│   ├── test_sheets.py              # Testes do Google Sheets
│   ├── test_validators.py          # Testes de validação
│   └── test_auth.py                # Testes de autenticação
└── logs/                            # Logs da aplicação (auto-gerado)
    └── simulador_YYYYMMDD.log      # Logs diários
```

## 🔑 Arquivos Principais

### app.py (Arquivo Principal)

Aplicação principal (~2.300 linhas). Parte da lógica está em `services/`, `config/` e `utils/`; o app importa deles (auth, RAJs, simulação, busca, exportação, UI).

**Seções principais (faixas aproximadas):**
1. **Configuração** (~18-156): CSS, page config, responsividade mobile
2. **Google Sheets** (~262-423): Conexão e CRUD usados pela UI — `conectar_sheets`, `carregar_inscricoes`, `salvar_inscricao`, `excluir_inscricao`, `buscar_inscricao`
3. **Lógica de Simulação** (~443+): `calcular_resultado` (2 fases), `calcular_demanda`; funções auxiliares como `obter_status_lotacao` e `calcular_lotacao_dinamica` vêm de `services/simulacao_service.py`
4. **Busca e comparação com edital** (~677+): `normalizar_nome`, `processar_csv_edital`, `comparar_edital_simulador`
5. **Interface** (~991+): `main()` com 7 abas (Resultado, Inscrição, Inscritos, Vagas, Análise de Vagas, Lotação, RAJs)

Autenticação e RAJs não ficam no app: credenciais em `config/auth_config.py`, validação em `services/auth_service.py`; dados das RAJs em `config/rajs_config.py`, funções em `services/rajs_service.py`. Existe também `services/sheets_service.py` com implementação alternativa de conexão/CRUD (11 colunas incluindo K); a UI atual usa as funções do app.py.

### config/auth_config.py e services/auth_service.py (Autenticação)

- **auth_config.py**: Credenciais e lista de usuários — `AUTH_CODES`, `ADMIN_TELEFONES`, `ADMIN_SENHA` (via `get_auth_codes()`, `get_admin_telefones()`, `get_admin_senha()`; podem vir de `secrets.toml` ou valores padrão).
- **auth_service.py**: Validação — `verificar_login(telefone, codigo)`, `verificar_admin(telefone, senha)`, `formatar_telefone_display`, `limpar_telefone`.

No estado atual, o app **não exibe tela de login** na UI (acesso direto ao conteúdo). Os módulos de autenticação existem e podem ser reativados.

### Google Sheets (Base de Dados)

A conexão e o CRUD de inscrições usados pela interface estão no **app.py** (`conectar_sheets`, `carregar_inscricoes`, `salvar_inscricao`, `excluir_inscricao`). Opcionalmente existe `services/sheets_service.py` com funções equivalentes e cabeçalhos em 11 colunas. A planilha usa 11 colunas (A–K), incluindo **K: posicao_lista_classificatoria**.

### config/rajs_config.py e services/rajs_service.py (RAJs)

- **rajs_config.py**: Dicionário **RAJS** com as 10 Regiões Administrativas Judiciárias.
- **rajs_service.py**: `obter_raj_da_comarca(comarca, normalizar_func=None)` — identifica a RAJ de uma comarca com lookup pré-indexado.

### data.py

Contém dois dicionários principais:
- **ANEXO_I**: Vagas com déficit (50 unidades)
- **ANEXO_II**: Todas as unidades judiciárias (300+ unidades)

Formato: `"CODIGO": {"comarca": "...", "unidade": "...", "quantidade": N}`

### lotacao_data.py

Dados de lotação real vs paradigma (CNJ 219/2016):
- **LOTACAO_POR_CODIGO**: Mapeamento por código do Anexo II
- **LOTACAO_COMPLETA**: Lista completa com status (SUPERAVITÁRIA/EQUILIBRADA/DEFICITÁRIA)

## 🔐 Sistema de Autenticação

**Dois níveis de acesso** (implementados em `config/auth_config.py` e `services/auth_service.py`):

1. **Usuários Comuns**: Telefones cadastrados em `AUTH_CODES` (em `auth_config.py`; pode vir de `secrets.toml` ou padrão)
   - Formato: telefone (11 dígitos) → código (TJPR-XXXXXX)
   - Validação: `verificar_login(telefone, codigo)` em `auth_service.py`

2. **Administradores**: Lista `ADMIN_TELEFONES` + senha `ADMIN_SENHA` (em `auth_config.py`; padrão: "41997813606", "swift")
   - Validação: `verificar_admin(telefone, senha)` em `auth_service.py`

**Nota:** Na versão atual da UI, o app **não exibe tela de login** — o acesso ao conteúdo é direto. Os módulos de autenticação estão disponíveis para uso ou reativação.

## 📊 Fluxo de Dados

```
Google Sheets ↔ carregar_inscricoes() (app.py)
                    ↓
             calcular_resultado() (app.py)
                    ↓
             Interface (7 abas)
```

(Login existe nos módulos `auth_config`/`auth_service` mas não é usado na UI atual.)

### Google Sheets (Base de Dados)

**Estrutura das colunas (11 colunas):**
- A: nome
- B: matricula
- C: data_admissao (MANTIDO para informação, mas não há mais restrição de estágio probatório em 01/2026)
- D: lotacao_atual
- E: escolha_anexo1
- F: escolha_anexo2
- G: data_inscricao
- H: registrado_por (auditoria)
- I: alterado_por (auditoria)
- J: data_alteracao (auditoria)
- **K: posicao_lista_classificatoria** (posição na lista classificatória)

## 🎯 Regras de Negócio Críticas

### 1. Estágio Probatório
- **Edital 01/2026**: Servidores em estágio probatório **PODEM participar** da relotação
- (Restrição removida - era DATA_LIMITE_ESTAGIO no edital anterior)

### 2. Critério de Prioridade
- **ÚNICO critério**: Posição na Lista Classificatória (Edital 01/2026)
- Posição 1 = maior prioridade, posição 1291 = menor prioridade
- A `data_admissao` é mantida apenas para informação, não afeta a ordem

### 3. Processamento em Duas Fases

**Fase 1 - Anexo I (Vagas com Déficit):**
```python
# Para cada inscrito (ordem de posicao_lista_classificatoria):
if tem_vaga_disponivel(escolha_anexo1):
    conceder_vaga()
    atualizar_lotacao_origem(-1)  # Servidor sai
    adicionar_vaga_anexo2(lotacao_origem)  # Origem fica disponível
    calcular_designacao_origem()
```

**Fase 2 - Anexo II (Todas as Unidades):**
```python
# Para quem NÃO conseguiu Anexo I:
if escolha_anexo1_disponivel_via_anexo2 AND escolha_anexo2_disponivel:
    # Item 3.13: Preferência pela escolha original do Anexo I
    conceder_anexo1_via_anexo2()
elif escolha_anexo2_disponivel:
    conceder_anexo2()
else:
    status = "NÃO OBTEVE VAGA"
```

### 4. Designação na Origem (Item 3.16)

Após conceder vaga, calcula se a saída do servidor CAUSA DÉFICIT na origem:

```python
if calcular_lotacao_dinamica(origem)["status"] == "DEFICITÁRIA":
    designacao_origem = "SIM"  # Fica até ser substituído
else:
    designacao_origem = "NÃO"  # Pode sair imediatamente
```

## 🧮 Funções Principais

### Autenticação (services/auth_service.py)
- `verificar_login(telefone, codigo)` → Valida credenciais (usa AUTH_CODES de auth_config)
- `verificar_admin(telefone, senha)` → Valida admin
- `formatar_telefone_display(telefone)`, `limpar_telefone(telefone)`

### Google Sheets (app.py — usadas pela UI)
- `conectar_sheets()` → Conexão com Google Sheets (@st.cache_resource)
- `carregar_inscricoes(sheet)` → Carrega dados em DataFrame
- `salvar_inscricao(sheet, dados)` → Salva/atualiza inscrição com auditoria
- `excluir_inscricao(sheet, matricula)` → Remove inscrição
- `buscar_inscricao(sheet, matricula)` → Busca inscrição por matrícula

### Lógica de Negócio
- **app.py**: `calcular_resultado(df_inscricoes)` → Executa simulação completa (2 fases)
- **services/simulacao_service.py**: `obter_status_lotacao(codigo)`, `obter_dados_lotacao(codigo)`, `calcular_lotacao_dinamica(codigo, ajuste)`  
  (Edital 01/2026: `verificar_estagio_probatorio` foi removido — estágio probatório pode participar.)

### RAJs (services/rajs_service.py)
- `obter_raj_da_comarca(comarca, normalizar_func=None)`

### Busca na lista classificatória (services/search_service.py)
- `buscar_servidor_por_nome(nome_inscricao, threshold)`, `buscar_servidor_por_matricula(matricula)`

### Utilitários
- **app.py**: `normalizar_comarca(nome)` → Normaliza nomes de comarcas (40+ variações)
- **utils**: normalizers, validators; **utils/error_handlers**: `handle_error`, `handle_success`; **utils/ui_components**: `alert_box`, `metric_card`, `loading_spinner`, `empty_state`

## 🖥️ Interface do Usuário

### 7 Abas (conforme app.py)

1. **🏆 Resultado**: Resultado completo da simulação (quem foi aprovado, designação na origem, vagas restantes)
2. **✍️ Minha Inscrição**: Formulário de cadastro/edição de inscrição
3. **👥 Inscritos**: Lista de todos os inscritos (pesquisável/filtrável)
4. **📋 Vagas do Edital (Anexos I e II)**: Catálogo de vagas com quantidade e demanda (quantos escolheram cada unidade)
5. **📊 Vagas após a simulação**: O que restou do Anexo I (não preenchidas) e vagas abertas no Anexo II (por RAJ), após rodar a simulação
6. **📈 Lotação**: Tabela de lotação paradigma (real vs paradigma, status por unidade)
7. **🗺️ Regiões (RAJs)**: Análise geográfica por região administrativa

Não há painel de administrador na UI atual. Os módulos de autenticação (`auth_config`, `auth_service`) permitem implementar ou reativar um painel admin no futuro.

## 🔧 Configuração e Deploy

### Variáveis de Ambiente (.streamlit/secrets.toml)

```toml
spreadsheet_name = "Nome da Planilha no Google Sheets"

[gcp_service_account]
type = "service_account"
project_id = "seu-projeto"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
# ... demais campos da service account
```

### Executar Localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

### DevContainer

O projeto inclui `.devcontainer/devcontainer.json` configurado para:
- Python 3.11
- Auto-instalação de dependências
- Streamlit iniciando automaticamente na porta 8501

## 🎨 Personalização Visual

### CSS Customizado

O app.py inclui CSS responsivo (bloco no início do arquivo) para:
- Telas móveis (max-width: 768px)
- Redução de padding e fontes em dispositivos pequenos
- Scroll horizontal em tabelas
- Tabs com wrap flexível

### Tema Streamlit (.streamlit/config.toml)

```toml
primaryColor = "#1E88E5"  # Azul TJPR
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
```

## 📝 Convenções de Código

### Formatação de Telefones
```python
# Armazenamento: "41997813606" (11 dígitos limpos)
# Display: "(41) 99781-3606"
```

### Formatação de Datas
```python
# Google Sheets: "DD/MM/YYYY" ou "DD/MM/YYYY HH:MM"
# DataFrame: datetime objects
# Display: "DD/MM/YYYY"
```

### Códigos de Unidades
```python
# Anexo I: "A1-001" a "A1-256"
# Anexo II: "A2-001" a "A2-XXX"
```

## 🚨 Pontos de Atenção para AI Assistants

### ⚠️ NUNCA modificar sem consultar:
1. **AUTH_CODES** e **ADMIN_TELEFONES/ADMIN_SENHA** em `config/auth_config.py`: Lista de usuários autorizados e credenciais administrativas
2. **Lógica de calcular_resultado()** (app.py): Implementa regras do edital oficial

(DATA_LIMITE_ESTAGIO foi removido no Edital 01/2026; não existe mais no código.)

### ✅ Seguro para modificar:
- CSS e estilos visuais
- Mensagens de interface
- Funções de formatação/exibição (utils/normalizers)
- Normalização de nomes/comarcas
- Componentes e helpers de UI (utils/ui_components, utils/ui_helpers, utils/error_handlers)

### 🔍 Ao fazer alterações:
1. **Backup de dados**: Google Sheets mantém histórico, mas cuidado com alterações estruturais
2. **Testes de regressão**: Verificar se o cálculo de resultados continua correto
3. **Auditoria**: Todas as modificações em inscrições DEVEM registrar `alterado_por` e `data_alteracao`
4. **Session state**: Usar `st.rerun()` após mudanças de estado importantes

## 📚 Referências do Edital 01/2026

### Itens implementados automaticamente:
- **Item 1.1**: Servidores em estágio probatório PODEM participar
- **Item 2.1**: Anexo I - vagas com déficit e unidades em estatização
- **Item 3.9**: Análise segue ordem da lista classificatória
- **Item 3.10**: Anexo I avaliado primeiro
- **Item 3.11**: Anexo II apenas para unidades deficitárias após Anexo I
- **Item 3.12**: Aprovados no Anexo I excluídos da análise do Anexo II
- **Item 3.13**: Preferência pela escolha original do Anexo I quando ambos disponíveis
- **Item 3.14**: Lotação dinâmica atualizada durante análise
- **Item 3.16**: Designação na origem se a saída causar déficit
- **Item 3.17**: Vaga condicionada à substituição (ato tornado sem efeito se não houver)

### Itens que requerem verificação MANUAL (não implementados no código):
- **Item 3.2**: Servidor não lotado em 1º grau (DESCLASSIFICADO)
- **Item 3.3**: Relotado há menos de 2 anos (DESCLASSIFICADO, exceto se todos assim)
- **Item 3.3.1**: Exceção: preferência ao relotado há mais tempo
- **Item 3.3.2**: Servidores do Edital 04/2025 designados na origem
- **Item 3.4**: Unidades em estatização: designação na origem até data específica
- **Item 3.18**: Servidores de unidades superavitárias ou já designados de ofício não precisam de designação

## 🐛 Troubleshooting Comum

### Erro de conexão com Google Sheets
- Verificar `secrets.toml` configurado corretamente
- Service account tem permissão na planilha?
- Nome da planilha em `spreadsheet_name` está exato?

### Dados não salvando
- Verificar se `st.cache_resource.clear()` é chamado após alterações
- Conferir formato das datas (DD/MM/YYYY)

### Cálculo de resultados incorreto
- Verificar se ANEXO_I e ANEXO_II em `data.py` estão atualizados
- Confirmar que `lotacao_data.py` tem todos os códigos necessários
- Checar se alguma inscrição tem código de unidade inexistente

Se usar `services/sheets_service.py` em vez das funções do app.py, verificar que os cabeçalhos da planilha incluem as 11 colunas (até K: posicao_lista_classificatoria).

---

**Última atualização**: Revisado em fev/2026 — alinhado à estrutura refatorada (services, config, utils) e à versão atual do app
