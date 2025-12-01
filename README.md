# Simulador de Relotação TJPR

Aplicação Streamlit para simular o processo de relotação de servidores do Tribunal de Justiça do Paraná (Edital nº 4/2025 - Técnico Judiciário).

## 📋 Visão Geral

Este simulador permite que servidores do TJPR visualizem e simulem o processo de relotação conforme as regras estabelecidas no Edital nº 4/2025. O sistema implementa todas as regras críticas do edital, incluindo:

- Verificação de estágio probatório
- Processamento em duas fases (Anexo I e Anexo II)
- Cálculo dinâmico de lotação
- Designação na origem por déficit
- Priorização por antiguidade

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- Conta Google Cloud com Service Account configurada
- Google Sheets com permissões para a Service Account

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd simulador-relotacao-tjpr
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as credenciais**

   Copie o arquivo de exemplo:
   ```bash
   cp secrets.toml.example .streamlit/secrets.toml
   ```

   Edite `.streamlit/secrets.toml` e preencha:
   - `spreadsheet_name`: Nome exato da planilha no Google Sheets
   - `gcp_service_account`: Credenciais da Service Account (todos os campos do JSON)

   **Opcional** (para maior segurança):
   - `admin_senha`: Senha de administrador
   - `admin_telefones`: Lista de telefones de administradores
   - `auth_codes`: Mapeamento de telefones para códigos de acesso

5. **Execute a aplicação**
   ```bash
   streamlit run app.py
   ```

   A aplicação estará disponível em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
simulador-relotacao-tjpr/
├── app.py                    # Aplicação principal Streamlit
├── data.py                   # ANEXO_I e ANEXO_II (vagas do edital)
├── lotacao_data.py           # Dados de lotação paradigma
├── exceptions.py             # Exceções customizadas
├── config/                   # Configurações
│   ├── __init__.py
│   ├── settings.py           # Constantes e configurações
│   └── auth_config.py       # Configuração de autenticação
├── services/                 # Lógica de negócio
│   ├── __init__.py
│   ├── auth_service.py       # Autenticação e autorização
│   ├── sheets_service.py     # Operações Google Sheets
│   └── simulacao_service.py  # Lógica de cálculo de resultados
├── utils/                    # Utilitários
│   ├── __init__.py
│   ├── logger.py             # Sistema de logging
│   ├── formatters.py         # Formatação de dados
│   ├── normalizers.py        # Normalização de dados
│   └── validators.py         # Validações
├── tests/                    # Testes
│   ├── __init__.py
│   ├── conftest.py           # Configuração pytest
│   ├── test_auth.py          # Testes de autenticação
│   ├── test_simulacao.py     # Testes de simulação
│   ├── test_sheets.py        # Testes de Google Sheets
│   └── test_validators.py    # Testes de validação
├── docs/                     # Documentação técnica
│   ├── ARCHITECTURE.md       # Arquitetura do sistema
│   └── API.md                # Documentação de funções
├── logs/                     # Logs do sistema (gerado automaticamente)
├── requirements.txt          # Dependências Python
├── secrets.toml.example      # Template de configuração
└── README.md                 # Este arquivo
```

## 🔐 Autenticação

O sistema possui dois níveis de acesso:

### Usuários Comuns
- Acesso via telefone + código de acesso
- Códigos são enviados por WhatsApp
- Permitem: visualizar inscrições, fazer simulações, cadastrar/editar própria inscrição

### Administradores
- Acesso via telefone de admin + senha
- Permitem: todas as funcionalidades de usuário comum + painel administrativo completo

**Nota**: Por padrão, as credenciais estão hardcoded no código. Para maior segurança, mova-as para `secrets.toml` conforme documentado em `secrets.toml.example`.

## 📊 Funcionalidades

### Para Usuários Comuns

1. **✍️ Inscrição**: Cadastrar ou editar sua inscrição
2. **👥 Inscritos**: Lista de todos os inscritos (pesquisável/filtrável)
3. **🏆 Resultado**: Resultado completo da simulação com métricas
4. **🎯 Simulador**: Simulação pessoal + comparador de cenários
5. **📋 Vagas**: Visualização Anexo I e II com demanda
6. **📈 Lotação**: Tabela completa de lotação paradigma
7. **🗺️ RAJs**: Análise geográfica por região

### Para Administradores (Além das acima)

1. **📊 Visão Geral**: Métricas do sistema e atividades recentes
2. **👥 Gestão de Usuários**: Lista todos os usuários cadastrados
3. **📝 Gestão de Inscrições**: Administração avançada de inscrições
4. **📋 Logs de Atividades**: Auditoria completa (quem fez o quê)
5. **📥 Exportar Dados**: Download Excel (inscrições/resultados/logs)
6. **📤 Comparar com Edital Oficial**: Upload CSV do TJPR e comparação fuzzy
7. **🏠 Vagas RMC**: Foco em Região Metropolitana de Curitiba
8. **⚙️ Configurações**: Informações do sistema

## 🧪 Testes

Execute os testes com:

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html

# Teste específico
pytest tests/test_auth.py

# Verbose
pytest -v
```

## 🐛 Troubleshooting

### Erro de conexão com Google Sheets

- Verifique se `secrets.toml` está configurado corretamente
- Confirme que a Service Account tem permissão na planilha
- Verifique se o nome da planilha em `spreadsheet_name` está exato (case-sensitive)

### Dados não salvando

- Verifique se `st.cache_resource.clear()` é chamado após alterações
- Confira o formato das datas (DD/MM/YYYY)
- Verifique os logs em `logs/` para mais detalhes

### Cálculo de resultados incorreto

- Verifique se `ANEXO_I` e `ANEXO_II` em `data.py` estão atualizados
- Confirme que `lotacao_data.py` tem todos os códigos necessários
- Verifique se alguma inscrição tem código de unidade inexistente

### Erro de importação de módulos

- Certifique-se de que está no diretório raiz do projeto
- Verifique se todas as dependências estão instaladas: `pip install -r requirements.txt`

## 📚 Documentação Adicional

- [Arquitetura do Sistema](docs/ARCHITECTURE.md)
- [Documentação da API](docs/API.md)
- [CLAUDE.md](CLAUDE.md) - Documentação técnica detalhada do projeto original

## 🔧 Desenvolvimento

### Adicionar Novo Usuário

1. Edite `config/auth_config.py` e adicione o telefone e código em `DEFAULT_AUTH_CODES`
2. Ou adicione em `secrets.toml` na seção `[auth_codes]`

### Adicionar Novo Administrador

1. Edite `config/auth_config.py` e adicione o telefone em `DEFAULT_ADMIN_TELEFONES`
2. Ou adicione em `secrets.toml` na seção `admin_telefones`

### Estrutura de Dados

As inscrições são armazenadas no Google Sheets com as seguintes colunas:

- `nome`: Nome do servidor
- `matricula`: Matrícula
- `data_admissao`: Data de admissão (DD/MM/YYYY)
- `lotacao_atual`: Código da lotação atual (Anexo II)
- `escolha_anexo1`: Código da escolha Anexo I (opcional)
- `escolha_anexo2`: Código da escolha Anexo II (opcional)
- `data_inscricao`: Data/hora da inscrição
- `registrado_por`: Telefone de quem registrou
- `alterado_por`: Telefone de quem alterou por último
- `data_alteracao`: Data/hora da última alteração

## 📝 Licença

Este projeto é um simulador não oficial criado para auxiliar na tomada de decisão. O resultado oficial depende exclusivamente da análise do TJPR conforme Edital nº 4/2025.

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte, entre em contato pelo WhatsApp: **(41) 99781-3606**

---

**Última atualização**: 2025
