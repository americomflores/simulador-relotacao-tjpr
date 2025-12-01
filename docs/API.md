# Documentação da API

## Serviços

### auth_service

#### `formatar_telefone_display(telefone: str) -> str`
Formata telefone para exibição: (XX) XXXXX-XXXX

**Parâmetros:**
- `telefone`: Telefone em qualquer formato

**Retorna:**
- Telefone formatado para exibição

**Exemplo:**
```python
formatar_telefone_display("41997813606")  # "(41) 99781-3606"
```

#### `limpar_telefone(telefone: str) -> str`
Remove tudo que não for número do telefone.

**Parâmetros:**
- `telefone`: Telefone em qualquer formato

**Retorna:**
- Telefone apenas com números

**Exemplo:**
```python
limpar_telefone("(41) 99781-3606")  # "41997813606"
```

#### `verificar_login(telefone: str, codigo: str) -> bool`
Verifica se telefone e código são válidos.

**Parâmetros:**
- `telefone`: Telefone do usuário
- `codigo`: Código de acesso

**Retorna:**
- True se credenciais são válidas, False caso contrário

#### `verificar_admin(telefone: str, senha: str) -> bool`
Verifica se o usuário é administrador.

**Parâmetros:**
- `telefone`: Telefone do usuário
- `senha`: Senha de administrador

**Retorna:**
- True se é admin, False caso contrário

#### `is_admin() -> bool`
Verifica se o usuário logado é administrador.

**Retorna:**
- True se é admin, False caso contrário

#### `get_usuario_logado() -> str`
Retorna o telefone formatado do usuário logado.

**Retorna:**
- Telefone formatado ou "Desconhecido"

---

### sheets_service

#### `conectar_sheets() -> gspread.Worksheet`
Conecta ao Google Sheets usando credenciais do secrets.

**Retorna:**
- Sheet object ou None em caso de erro

**Exceções:**
- `ConfigurationError`: Se credenciais não encontradas
- `SheetsError`: Se erro ao conectar

#### `carregar_inscricoes(sheet: gspread.Worksheet) -> pd.DataFrame`
Carrega todas as inscrições do Google Sheets.

**Parâmetros:**
- `sheet`: Sheet object do gspread ou None

**Retorna:**
- DataFrame com as inscrições

**Exceções:**
- `SheetsError`: Se erro ao carregar

#### `salvar_inscricao(sheet: gspread.Worksheet, dados: dict, telefone_usuario: str) -> bool`
Salva ou atualiza uma inscrição, registrando quem fez a operação.

**Parâmetros:**
- `sheet`: Sheet object do gspread
- `dados`: Dicionário com dados da inscrição
- `telefone_usuario`: Telefone do usuário que está salvando

**Retorna:**
- True se sucesso, False caso contrário

**Exceções:**
- `SheetsError`: Se erro ao salvar

**Formato de `dados`:**
```python
{
    "nome": str,
    "matricula": str,
    "data_admissao": str,  # "DD/MM/YYYY"
    "lotacao_atual": str,  # Código Anexo II
    "escolha_anexo1": str,  # Código Anexo I (opcional)
    "escolha_anexo2": str,  # Código Anexo II (opcional)
    "data_inscricao": str   # "DD/MM/YYYY HH:MM"
}
```

#### `excluir_inscricao(sheet: gspread.Worksheet, matricula: str, telefone_usuario: str) -> tuple[bool, str | None]`
Exclui uma inscrição pela matrícula.

**Parâmetros:**
- `sheet`: Sheet object do gspread
- `matricula`: Matrícula da inscrição a excluir
- `telefone_usuario`: Telefone do usuário que está excluindo

**Retorna:**
- Tupla (sucesso, nome_excluido)

**Exceções:**
- `SheetsError`: Se erro ao excluir

#### `buscar_inscricao(sheet: gspread.Worksheet, matricula: str) -> dict | None`
Busca inscrição por matrícula.

**Parâmetros:**
- `sheet`: Sheet object do gspread
- `matricula`: Matrícula a buscar

**Retorna:**
- Dicionário com dados da inscrição ou None

---

### simulacao_service

#### `verificar_estagio_probatorio(data_admissao: date) -> bool`
Verifica se servidor está em estágio probatório.

**Parâmetros:**
- `data_admissao`: Data de admissão do servidor

**Retorna:**
- True se está em estágio probatório, False caso contrário

#### `calcular_lotacao_dinamica(codigo_unidade: str, ajuste: int = 0) -> dict | None`
Calcula a lotação considerando ajustes dinâmicos.

**Parâmetros:**
- `codigo_unidade`: Código da unidade
- `ajuste`: Número de servidores a adicionar (+) ou remover (-)

**Retorna:**
- Dicionário com lotação calculada ou None

**Formato do retorno:**
```python
{
    "lotacao_real": int,
    "lotacao_paradigma": int,
    "diferenca": int,
    "status": str  # "SUPERAVITÁRIA", "EQUILIBRADA", "DEFICITÁRIA"
}
```

#### `calcular_resultado(df_inscricoes: pd.DataFrame) -> tuple`
Calcula o resultado da simulação com lotação dinâmica.

**Parâmetros:**
- `df_inscricoes`: DataFrame com inscrições

**Retorna:**
- Tupla (df_resultado, vagas_anexo1, vagas_anexo2, ajustes_lotacao)

**Exceções:**
- `SimulationError`: Se erro ao calcular

**Colunas do DataFrame de resultado:**
- `posicao_antiguidade`: Posição na ordem de antiguidade
- `status`: "APROVADO", "DESCLASSIFICADO", "NÃO OBTEVE VAGA"
- `resultado`: "ANEXO I", "ANEXO I (via A2)", "ANEXO II", "Estágio Probatório", "Sem vaga"
- `vaga_obtida`: Descrição da vaga obtida
- `designacao_origem`: "SIM", "NÃO", "-"
- `observacao`: Observações adicionais
- `status_origem_inicial`: Status inicial da lotação de origem
- `status_origem_final`: Status final da lotação de origem

#### `calcular_demanda(df_inscricoes: pd.DataFrame) -> tuple[dict, dict]`
Calcula a demanda por vaga (quantos servidores escolheram cada vaga).

**Parâmetros:**
- `df_inscricoes`: DataFrame com inscrições

**Retorna:**
- Tupla (demanda_a1, demanda_a2) - dicionários com contagem por código

---

### validators

#### `validar_telefone(telefone: str) -> bool`
Valida formato de telefone.

**Parâmetros:**
- `telefone`: Telefone a validar

**Retorna:**
- True se válido, False caso contrário

#### `validar_matricula(matricula: str) -> bool`
Valida formato de matrícula.

**Parâmetros:**
- `matricula`: Matrícula a validar

**Retorna:**
- True se válido, False caso contrário

#### `validar_data_admissao(data_admissao: date | str) -> tuple[bool, str]`
Valida data de admissão.

**Parâmetros:**
- `data_admissao`: datetime.date ou string

**Retorna:**
- Tupla (is_valid, error_message)

#### `validar_codigo_unidade(codigo: str, anexo: str | None = None) -> tuple[bool, str]`
Valida se código de unidade existe no Anexo I ou II.

**Parâmetros:**
- `codigo`: Código da unidade
- `anexo`: "I" para Anexo I, "II" para Anexo II, None para ambos

**Retorna:**
- Tupla (is_valid, error_message)

#### `validar_inscricao(nome: str, matricula: str, data_admissao: date, lotacao_atual: str, escolha_anexo1: str = "", escolha_anexo2: str = "") -> tuple[bool, list[str]]`
Valida todos os campos de uma inscrição.

**Parâmetros:**
- `nome`: Nome do servidor
- `matricula`: Matrícula
- `data_admissao`: Data de admissão
- `lotacao_atual`: Código da lotação atual
- `escolha_anexo1`: Código da escolha Anexo I (opcional)
- `escolha_anexo2`: Código da escolha Anexo II (opcional)

**Retorna:**
- Tupla (is_valid, error_messages)

---

### normalizers

#### `normalizar_nome(nome: str) -> str`
Normaliza um nome para comparação (remove acentos, converte para minúsculas, etc).

**Parâmetros:**
- `nome`: Nome a ser normalizado

**Retorna:**
- Nome normalizado

#### `nomes_sao_iguais(nome1: str, nome2: str) -> bool`
Compara dois nomes de forma flexível.

**Parâmetros:**
- `nome1`: Primeiro nome
- `nome2`: Segundo nome

**Retorna:**
- True se os nomes são considerados iguais

#### `normalizar_comarca(nome: str) -> str`
Normaliza nome de comarca para comparação.

**Parâmetros:**
- `nome`: Nome da comarca

**Retorna:**
- Nome normalizado

---

### logger

#### `log_operation(operation: str, user: str, details: str = "")`
Registra uma operação importante no sistema.

**Parâmetros:**
- `operation`: Nome da operação (ex: "salvar_inscricao")
- `user`: Telefone do usuário que executou a operação
- `details`: Detalhes adicionais da operação

#### `log_error(error: Exception, context: str = "")`
Registra um erro com contexto.

**Parâmetros:**
- `error`: Exceção ocorrida
- `context`: Contexto adicional do erro

---

## Exceções

### SimuladorError
Exceção base para erros do simulador.

### AuthenticationError
Erro de autenticação.

### ValidationError
Erro de validação de dados.

### SheetsError
Erro ao acessar Google Sheets.

### SimulationError
Erro durante cálculo de simulação.

### ConfigurationError
Erro de configuração do sistema.

