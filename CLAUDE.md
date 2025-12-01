# CLAUDE.md - Simulador de Relotação TJPR

## 📋 Visão Geral do Projeto

Aplicação Streamlit para simular o processo de relotação de servidores do Tribunal de Justiça do Paraná (Edital nº 4/2025 - Técnico Judiciário).

**Stack Tecnológico:**
- Python 3.11 + Streamlit
- Pandas para processamento de dados
- Google Sheets como banco de dados (via gspread)
- Autenticação customizada (telefone + código)

## 🏗️ Estrutura de Arquivos

```
simulador-relotacao-tjpr/
├── app.py                           # Aplicação principal (3.600+ linhas)
├── data.py                          # ANEXO_I e ANEXO_II (vagas do edital)
├── lotacao_data.py                  # Dados de lotação paradigma das unidades
├── requirements.txt                 # Dependências Python
├── .streamlit/
│   └── config.toml                 # Configuração do Streamlit
├── secrets.toml.example            # Template para credenciais Google Sheets
├── services/                        # Módulos de serviços
│   ├── auth_service.py             # Autenticação e autorização
│   ├── sheets_service.py           # Operações com Google Sheets
│   └── simulacao_service.py        # Lógica de cálculo de resultados
├── config/                          # Configurações do sistema
│   ├── auth_config.py              # AUTH_CODES, ADMIN_TELEFONES, ADMIN_SENHA
│   └── settings.py                 # DATA_LIMITE_ESTAGIO
├── utils/                           # Utilitários
│   ├── logger.py                   # Sistema de logging
│   ├── formatters.py               # Formatação de dados
│   ├── normalizers.py              # Normalização de strings
│   └── validators.py               # Validações
└── logs/                            # Logs da aplicação (auto-gerado)
    └── simulador_YYYYMMDD.log      # Logs diários
```

## 🔑 Arquivos Principais

### app.py (Arquivo Principal)

**Seções principais:**
1. **Configuração** (linhas 18-83): CSS, page config, responsividade mobile
2. **Administradores** (linhas 89-98): Telefones admin e senha
3. **Códigos de Autenticação** (linhas 101-216): Mapeamento telefone → código (108 usuários)
4. **RAJs** (linhas 316-482): 10 Regiões Administrativas Judiciárias
5. **Google Sheets** (linhas 529-705): Conexão e operações de CRUD
6. **Lógica de Simulação** (linhas 709-916): Cálculo de resultados
7. **Interface Principal** (linhas 2299-3583): 7 abas para usuários comuns
8. **Painel Admin** (linhas 1298-2296): 8 abas para administradores

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

**Dois níveis de acesso:**

1. **Usuários Comuns**: 108 telefones cadastrados em `AUTH_CODES` (app.py linhas 104-216)
   - Formato: telefone (11 dígitos) → código (TJPR-XXXXXX)
   - Acesso: inscrições, resultados, simulações

2. **Administradores**: Lista `ADMIN_TELEFONES` + senha `ADMIN_SENHA = "swift"`
   - Apenas 1 admin: "41997813606"
   - Acesso: painel administrativo completo

## 📊 Fluxo de Dados

```
Login → Google Sheets ↔ carregar_inscricoes()
                           ↓
                    calcular_resultado()
                           ↓
              Interface (7 abas) / Admin (8 abas)
```

### Google Sheets (Base de Dados)

**Estrutura das colunas:**
- A-F: Dados da inscrição (nome, matrícula, datas, escolhas)
- G: data_inscricao
- H: registrado_por (auditoria)
- I: alterado_por (auditoria)
- J: data_alteracao (auditoria)

## 🎯 Regras de Negócio Críticas

### 1. Período Probatório
- **DATA_LIMITE_ESTAGIO**: 26/11/2022
- Servidores admitidos APÓS essa data são DESCLASSIFICADOS

### 2. Critério de Prioridade
- **ÚNICO critério**: Antiguidade (data_admissao)
- Servidor mais antigo tem prioridade absoluta

### 3. Processamento em Duas Fases

**Fase 1 - Anexo I (Vagas com Déficit):**
```python
# Para cada inscrito (ordem de antiguidade):
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
    # Item 3.11: Preferência pela escolha original do Anexo I
    conceder_anexo1_via_anexo2()
elif escolha_anexo2_disponivel:
    conceder_anexo2()
else:
    status = "NÃO OBTEVE VAGA"
```

### 4. Designação na Origem (Item 3.14)

Após conceder vaga, calcula se a saída do servidor CAUSA DÉFICIT na origem:

```python
if calcular_lotacao_dinamica(origem)["status"] == "DEFICITÁRIA":
    designacao_origem = "SIM"  # Fica até ser substituído
else:
    designacao_origem = "NÃO"  # Pode sair imediatamente
```

## 🧮 Funções Principais

### Autenticação
- `verificar_login(telefone, codigo)` → Valida credenciais
- `tela_login()` → Renderiza tela de login
- `get_usuario_logado()` → Retorna telefone formatado do usuário logado

### Google Sheets
- `conectar_sheets()` → Conexão com Google Sheets (@st.cache_resource)
- `carregar_inscricoes(sheet)` → Carrega dados em DataFrame
- `salvar_inscricao(sheet, dados, telefone)` → Salva/atualiza inscrição com auditoria
- `excluir_inscricao(sheet, matricula, telefone)` → Remove inscrição

### Lógica de Negócio
- `calcular_resultado(df_inscricoes)` → Executa simulação completa (2 fases)
- `verificar_estagio_probatorio(data_admissao)` → Verifica se está em estágio
- `calcular_lotacao_dinamica(codigo, ajuste)` → Calcula lotação após ajustes

### Utilitários
- `normalizar_comarca(nome)` → Normaliza nomes de comarcas (40+ variações)
- `obter_raj_da_comarca(comarca)` → Retorna RAJ da comarca
- `obter_status_lotacao(codigo)` → Status: SUPERAVITÁRIA/EQUILIBRADA/DEFICITÁRIA

## 🖥️ Interface do Usuário

### Usuários Comuns (7 Abas)

1. **✍️ Inscrição**: Formulário de cadastro/edição
2. **👥 Inscritos**: Lista todos os inscritos (pesquisável/filtrável)
3. **🏆 Resultado**: Resultado completo da simulação com métricas
4. **🎯 Simulador**: Simulação pessoal + comparador de cenários
5. **📋 Vagas**: Visualização Anexo I e II com demanda
6. **📈 Lotação**: Tabela completa de lotação paradigma
7. **🗺️ RAJs**: Análise geográfica por região

### Administradores (8 Abas Adicionais)

1. **📊 Visão Geral**: Métricas do sistema e atividades recentes
2. **👥 Gestão de Usuários**: Lista todos os 108 usuários cadastrados
3. **📝 Gestão de Inscrições**: Administração avançada de inscrições
4. **📋 Logs de Atividades**: Auditoria completa (quem fez o quê)
5. **📥 Exportar Dados**: Download Excel (inscrições/resultados/logs)
6. **📤 Comparar com Edital Oficial**: Upload CSV do TJPR e comparação fuzzy
7. **🏠 Vagas RMC**: Foco em Região Metropolitana de Curitiba (20 comarcas ordenadas por distância)
8. **⚙️ Configurações**: Informações do sistema

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

O app.py inclui CSS responsivo (linhas 29-83) para:
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
1. **AUTH_CODES** (linhas 104-216): Lista de usuários autorizados
2. **ADMIN_TELEFONES/ADMIN_SENHA** (linhas 93-98): Credenciais administrativas
3. **DATA_LIMITE_ESTAGIO** (linha 86): Data crítica do edital
4. **Lógica de calcular_resultado()**: Implementa regras do edital oficial

### ✅ Seguro para modificar:
- CSS e estilos visuais
- Mensagens de interface
- Funções de formatação/exibição
- Exportação de dados
- Normalização de nomes/comarcas

### 🔍 Ao fazer alterações:
1. **Backup de dados**: Google Sheets mantém histórico, mas cuidado com alterações estruturais
2. **Testes de regressão**: Verificar se o cálculo de resultados continua correto
3. **Auditoria**: Todas as modificações em inscrições DEVEM registrar `alterado_por` e `data_alteracao`
4. **Session state**: Usar `st.rerun()` após mudanças de estado importantes

## 📚 Referências do Edital

O código implementa especificamente os itens:
- **Item 3.2**: Estágio probatório
- **Item 3.11**: Preferência Anexo I quando ambos disponíveis
- **Item 3.14**: Designação na origem por déficit
- **Item 3.15**: Vaga condicionada à substituição

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

---

**Última atualização**: Baseado no commit `b235a1f` - Remoção de funções obsoletas
