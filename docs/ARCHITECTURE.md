# Arquitetura do Sistema

## Visão Geral

O Simulador de Relotação TJPR é uma aplicação Streamlit modular que implementa as regras do Edital nº 4/2025 para simulação de relotação de servidores.

## Arquitetura em Camadas

```
┌─────────────────────────────────────┐
│         UI Layer (Streamlit)        │
│  app.py - Interface do usuário      │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│      Services Layer                  │
│  - auth_service.py                   │
│  - sheets_service.py                 │
│  - simulacao_service.py              │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│      Utils Layer                     │
│  - logger.py                        │
│  - validators.py                     │
│  - formatters.py                    │
│  - normalizers.py                   │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│      Config Layer                    │
│  - settings.py                       │
│  - auth_config.py                    │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│      Data Layer                      │
│  - data.py (ANEXO_I, ANEXO_II)      │
│  - lotacao_data.py                   │
│  - Google Sheets (via gspread)      │
└──────────────────────────────────────┘
```

## Componentes Principais

### 1. Camada de Apresentação (UI)

**app.py**
- Interface Streamlit principal
- Gerencia rotas e navegação
- Renderiza componentes visuais
- Gerencia estado da sessão

### 2. Camada de Serviços

#### auth_service.py
- Autenticação de usuários
- Verificação de administradores
- Formatação de telefones
- Gerenciamento de sessão

#### sheets_service.py
- Conexão com Google Sheets
- CRUD de inscrições
- Validação de cabeçalhos
- Tratamento de erros de conexão

#### simulacao_service.py
- Cálculo de resultados da simulação
- Verificação de estágio probatório
- Cálculo de lotação dinâmica
- Processamento em duas fases (Anexo I e II)

### 3. Camada de Utilitários

#### logger.py
- Sistema de logging estruturado
- Logs em arquivo e console
- Rastreamento de operações

#### validators.py
- Validação de dados de entrada
- Validação de telefones, matrículas, datas
- Validação de códigos de unidades

#### formatters.py
- Formatação de dados para exibição
- Formatação de datas e telefones

#### normalizers.py
- Normalização de nomes e comarcas
- Comparação fuzzy de strings
- Matching de unidades

### 4. Camada de Configuração

#### settings.py
- Constantes do sistema
- Data limite de estágio probatório

#### auth_config.py
- Configuração de autenticação
- Códigos de acesso
- Lista de administradores
- Carregamento de secrets

### 5. Camada de Dados

#### data.py
- ANEXO_I: Vagas com déficit
- ANEXO_II: Todas as unidades judiciárias

#### lotacao_data.py
- Dados de lotação paradigma
- Status de lotação (SUPERAVITÁRIA/EQUILIBRADA/DEFICITÁRIA)

#### Google Sheets
- Armazenamento persistente de inscrições
- Auditoria de alterações
- Histórico de operações

## Fluxo de Dados

### Fluxo de Autenticação

```
1. Usuário insere telefone + código
   ↓
2. auth_service.verificar_login()
   ↓
3. Consulta config/auth_config.AUTH_CODES
   ↓
4. Se válido: st.session_state.autenticado = True
   ↓
5. Redireciona para interface principal
```

### Fluxo de Simulação

```
1. Usuário solicita cálculo de resultado
   ↓
2. sheets_service.carregar_inscricoes()
   ↓
3. simulacao_service.calcular_resultado()
   ├─ Ordena por antiguidade
   ├─ Marca desclassificados (estágio probatório)
   ├─ FASE 1: Processa Anexo I
   │  ├─ Verifica vagas disponíveis
   │  ├─ Atualiza lotação dinâmica
   │  └─ Calcula designação na origem
   └─ FASE 2: Processa Anexo II
      ├─ Verifica vagas liberadas
      ├─ Aplica item 3.11 (prioridade Anexo I)
      └─ Calcula designação na origem
   ↓
4. Retorna DataFrame com resultados
   ↓
5. UI exibe resultados formatados
```

### Fluxo de Salvamento

```
1. Usuário preenche formulário
   ↓
2. validators.validar_inscricao()
   ↓
3. Se válido: sheets_service.salvar_inscricao()
   ├─ Busca inscrição existente
   ├─ Se existe: atualiza (mantém registrado_por)
   ├─ Se novo: cria (define registrado_por)
   └─ Registra alterado_por e data_alteracao
   ↓
4. logger.log_operation()
   ↓
5. Limpa cache do Streamlit
   ↓
6. Recarrega dados
```

## Tratamento de Erros

### Hierarquia de Exceções

```
SimuladorError (base)
├── AuthenticationError
├── ValidationError
├── SheetsError
├── SimulationError
└── ConfigurationError
```

### Estratégia de Tratamento

1. **Camada de Serviços**: Captura exceções específicas e relança como exceções customizadas
2. **Camada de UI**: Captura exceções e exibe mensagens amigáveis ao usuário
3. **Logger**: Registra todos os erros com stack trace completo

## Cache e Performance

### Cache do Streamlit

- `@st.cache_resource`: Conexão com Google Sheets (mantém conexão ativa)
- Cache invalidado manualmente após operações de escrita

### Otimizações

- Ordenação única por antiguidade
- Cálculo de lotação dinâmica apenas quando necessário
- Lazy loading de dados pesados

## Segurança

### Autenticação

- Códigos de acesso únicos por telefone
- Senha de administrador (pode ser movida para secrets.toml)
- Validação de entrada em todas as funções críticas

### Auditoria

- Todas as operações de escrita são logadas
- Rastreamento de quem fez o quê e quando
- Logs persistentes em arquivo

### Dados Sensíveis

- Credenciais podem ser movidas para `secrets.toml`
- Service Account do Google Cloud isolada
- Sem exposição de dados sensíveis no código

## Testes

### Estrutura de Testes

```
tests/
├── conftest.py          # Fixtures compartilhadas
├── test_auth.py         # Testes de autenticação
├── test_simulacao.py    # Testes de lógica de simulação
├── test_sheets.py       # Testes de Google Sheets (com mocks)
└── test_validators.py   # Testes de validação
```

### Cobertura

- Testes unitários para todas as funções críticas
- Testes de integração com mocks para Google Sheets
- Fixtures para dados de teste reutilizáveis

## Extensibilidade

### Adicionar Nova Funcionalidade

1. Criar função no serviço apropriado
2. Adicionar validações em `validators.py` se necessário
3. Adicionar testes em `tests/`
4. Integrar na UI em `app.py`

### Adicionar Nova Fonte de Dados

1. Criar novo serviço em `services/`
2. Implementar interface consistente com `sheets_service.py`
3. Atualizar `app.py` para usar novo serviço
4. Adicionar testes

## Considerações de Design

### Princípios Aplicados

- **Separação de Responsabilidades**: Cada módulo tem uma responsabilidade clara
- **DRY (Don't Repeat Yourself)**: Funções utilitárias reutilizáveis
- **Single Responsibility**: Cada função faz uma coisa bem
- **Fail Fast**: Validações no início das funções
- **Explicit is Better than Implicit**: Código claro e documentado

### Padrões Utilizados

- **Service Layer Pattern**: Lógica de negócio isolada em serviços
- **Repository Pattern**: Abstração de acesso a dados (Google Sheets)
- **Factory Pattern**: Criação de objetos de configuração
- **Strategy Pattern**: Diferentes estratégias de normalização/comparação

