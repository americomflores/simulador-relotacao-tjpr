"""
Página: Como Usar o Simulador
"""
import streamlit as st
from pages._shared import footer

st.header("Como Usar o Simulador")
st.caption("Tire suas dúvidas sobre o simulador e as regras do Edital 01/2026")

# --- Guia Rápido ---
st.subheader("Guia Rápido")

CARD_CSS = """
<div style="
    border: 2px solid #E0E0E0;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    height: 100%;
    min-height: 180px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
">
    <div style="
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
        line-height: 1;
    ">{numero}</div>
    <div style="
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    ">{titulo}</div>
    <div style="
        font-size: 0.85rem;
        color: #555;
        line-height: 1.4;
    ">{descricao}</div>
</div>
"""

passos = [
    ("1", "Busque seu nome", "Na página Inscrição, busque por nome para encontrar sua posição na Lista Classificatória"),
    ("2", "Escolha as unidades", "Escolha 1 unidade do Anexo I e 1 do Anexo II"),
    ("3", "Salve a inscrição", "Confira os dados e clique em Salvar"),
    ("4", "Veja o resultado", "Vá para a página Resultado e veja se conseguiu vaga"),
]

cols = st.columns(4)
for col, (numero, titulo, descricao) in zip(cols, passos):
    with col:
        st.markdown(
            CARD_CSS.format(numero=numero, titulo=titulo, descricao=descricao),
            unsafe_allow_html=True,
        )

st.markdown("")  # espaçamento

# --- Busca ---
busca = st.text_input(
    "🔍 Buscar nas perguntas...",
    placeholder="Ex: designação, anexo, vaga...",
)
busca_lower = busca.strip().lower()

# --- FAQ ---
FAQ_ITEMS = [
    # (categoria, titulo, conteudo)
    (
        "Sobre o Simulador",
        "O que é este simulador?",
        """Este é um simulador **não oficial** criado para ajudar servidores do TJPR a se planejarem para o processo de relotação do Edital nº 01/2026 (Técnico Judiciário).

**O que ele faz:**
- Permite que você simule sua inscrição e veja o resultado provável
- Mostra quantas pessoas escolheram cada unidade (demanda)
- Calcula se você ficaria designado na origem ou não

**O que ele NÃO faz:**
- Não substitui o resultado oficial do TJPR
- Não garante que o resultado será igual ao oficial
- O resultado real depende da análise da Secretaria de Gestão de Pessoas""",
    ),
    (
        "Sobre o Simulador",
        "O que o simulador NÃO verifica automaticamente?",
        """Este simulador **NÃO verifica automaticamente**:
- Se o servidor está lotado em 1º grau (Item 3.2)
- Se houve relotação nos últimos 2 anos (Item 3.3)
- Regras especiais para unidades em estatização (Item 3.4)
- Servidores de unidades superavitárias ou já designados de ofício (Item 3.18)

Essas verificações são feitas manualmente pela **Secretaria de Gestão de Pessoas** no resultado oficial.""",
    ),
    (
        "Inscrição",
        "Como preencher minha inscrição?",
        """1. Vá para a página **Inscrição**
2. **Busque seu nome** no campo de busca — o sistema vai localizar seus dados na Lista Classificatória
3. Confira sua **posição na lista** (ela define sua prioridade)
4. Preencha sua **matrícula** e **data de admissão**
5. Escolha a **unidade do Anexo I** (1ª opção — vagas deficitárias)
6. Escolha a **unidade do Anexo II** (2ª opção — todas as unidades)
7. Clique em **Salvar Inscrição**

**Dica:** Você pode usar a página **Vagas do Edital** para ver todas as unidades disponíveis e quantas pessoas já escolheram cada uma.""",
    ),
    (
        "Inscrição",
        "O que é o Anexo I e o Anexo II?",
        """- **Anexo I** = São **213 unidades com 435 vagas** (unidades deficitárias). É sua **1ª opção** de escolha e é analisada primeiro.
- **Anexo II** = São **todas as 606 unidades** judiciárias do TJPR. É sua **2ª opção**, analisada somente se você não conseguir vaga no Anexo I.

Você deve escolher **uma unidade de cada anexo** ao se inscrever.""",
    ),
    (
        "Inscrição",
        "Posso alterar minha inscrição depois?",
        """**Sim!** Para alterar ou excluir sua inscrição:
1. Vá para a página **Inscrição**
2. Busque por **matrícula** ou **nome**
3. Os dados da inscrição existente serão carregados automaticamente
4. Faça as alterações desejadas e clique em **Salvar Inscrição**

Para excluir, use o formulário **Excluir Inscrição** no final da página.""",
    ),
    (
        "Inscrição",
        "Quem pode participar?",
        """- Servidores **Técnicos Judiciários** lotados em unidades do **1º Grau de Jurisdição**
- Servidores em **estágio probatório podem participar** (novidade do Edital 01/2026)
- Servidores relotados a pedido há **menos de 2 anos** da publicação do edital (10/02/2026) são **desclassificados** (Item 3.3)
- Exceção: se todos os servidores de uma unidade estiverem nessa situação, há preferência ao relotado há mais tempo (Item 3.3.1)""",
    ),
    (
        "Regras e Resultado",
        "Como funciona o processo de relotação?",
        """O processo segue **duas fases**, nesta ordem:

**Fase 1 — Anexo I (vagas deficitárias):**
- São analisadas primeiro as escolhas do Anexo I (213 unidades com 435 vagas)
- Os servidores são atendidos **na ordem da Lista Classificatória** (posição 1 = maior prioridade)
- Quem consegue vaga no Anexo I libera sua lotação atual

**Fase 2 — Anexo II (todas as unidades):**
- Quem **não** conseguiu vaga no Anexo I é analisado aqui
- As vagas liberadas na Fase 1 ficam disponíveis
- Se a escolha original do Anexo I estiver disponível no Anexo II, ela tem preferência (Item 3.13)

**Critério de prioridade:** Somente a posição na Lista Classificatória do Edital 01/2026.""",
    ),
    (
        "Regras e Resultado",
        "O que significa 'Designação na Origem'?",
        """É quando você consegue a vaga, mas precisa continuar trabalhando na sua unidade atual até chegar um substituto.

| Designação | O que acontece? |
|------------|-------------|
| **NÃO** | Sua saída **não deixa a unidade abaixo do mínimo** de servidores. Você pode ir para a nova unidade imediatamente! |
| **SIM** | Sua saída **deixaria a unidade abaixo do mínimo**. Você foi aprovado e será transferido oficialmente, MAS continua trabalhando na unidade atual até chegarem novos servidores. |

**Atenção:** Se não chegarem substitutos até o final da validade do concurso, sua transferência pode ser cancelada.

**Como saber se terei que ficar designado?**
- Se a unidade ficar **acima do mínimo** depois que você sair = Designação NÃO
- Se a unidade ficar **no mínimo exato** depois que você sair = Designação NÃO
- Se a unidade ficar **abaixo do mínimo** depois que você sair = Designação SIM""",
    ),
    (
        "Regras e Resultado",
        "O que significam as cores no resultado?",
        """- 🟢 **Verde** — Aprovado (designação = NÃO) - pode sair imediatamente para a nova unidade
- 🟡 **Amarelo** — Aprovado (designação = SIM) - fica na origem até chegar um substituto
- ⚪ **Branco** — Não obteve vaga nesta simulação""",
    ),
    (
        "Regras e Resultado",
        "Por que meu resultado aparece como 'NÃO OBTEVE VAGA'?",
        """Isso pode acontecer por alguns motivos:

1. **Muita concorrência:** Servidores com posição menor (mais prioritários) na Lista Classificatória preencheram as vagas antes de você
2. **Unidade sem vaga:** A unidade que você escolheu no Anexo II não ficou deficitária (não abriu vaga)
3. **Ambas as escolhas indisponíveis:** Nem a vaga do Anexo I nem a do Anexo II estavam disponíveis quando chegou sua vez

**Dica:** Experimente trocar suas escolhas para unidades com menor demanda na página **Vagas do Edital**.""",
    ),
    (
        "Termos e Referências",
        "O que é Lotação Paradigma?",
        """**Colunas da tabela de lotação (página Lotação):**
- **Lotação Real**: Quantidade de servidores que trabalham na unidade hoje
- **Lotação Paradigma**: Quantidade mínima de servidores necessária (definida pelo CNJ — Resolução 219/2016)
- **Diferença**: Quantos servidores a mais ou a menos a unidade tem

**Status:**
- 🟢 **SUPERAVITÁRIA** — Tem mais servidores que o necessário
- 🟡 **EQUILIBRADA** — Tem exatamente o necessário
- 🔴 **DEFICITÁRIA** — Faltam servidores""",
    ),
    (
        "Termos e Referências",
        "Glossário de termos",
        """| Termo | Significado |
|-------|-------------|
| **Anexo I** | 213 unidades com 435 vagas (déficit de servidores) — 1ª opção de escolha |
| **Anexo II** | Todas as 606 unidades judiciárias — 2ª opção de escolha |
| **Lista Classificatória** | Ranking dos 1.291 servidores que define a ordem de prioridade |
| **Lotação Paradigma** | Número mínimo de servidores que cada unidade deve ter (CNJ 219/2016) |
| **Designação na Origem** | Obrigação de permanecer na unidade atual até chegar substituto |
| **RAJ** | Região Administrativa Judiciária — agrupamento geográfico de comarcas |
| **Superavitária** | Unidade com **mais** servidores que o mínimo necessário |
| **Equilibrada** | Unidade com **exatamente** o mínimo necessário |
| **Deficitária** | Unidade com **menos** servidores que o mínimo necessário |""",
    ),
]

CATEGORIA_ICONES = {
    "Sobre o Simulador": "ℹ️",
    "Inscrição": "✍️",
    "Regras e Resultado": "⚖️",
    "Termos e Referências": "📖",
}

CATEGORIAS_ORDENADAS = ["Sobre o Simulador", "Inscrição", "Regras e Resultado", "Termos e Referências"]

algum_resultado = False
for categoria in CATEGORIAS_ORDENADAS:
    itens_categoria = [(t, c) for cat, t, c in FAQ_ITEMS if cat == categoria]

    # Filtra pela busca
    itens_visiveis = []
    for titulo, conteudo in itens_categoria:
        if not busca_lower or busca_lower in titulo.lower() or busca_lower in conteudo.lower():
            itens_visiveis.append((titulo, conteudo))

    if not itens_visiveis:
        continue

    icone = CATEGORIA_ICONES.get(categoria, "")
    st.subheader(f"{icone} {categoria}")

    for titulo, conteudo in itens_visiveis:
        with st.expander(titulo):
            st.markdown(conteudo)
        algum_resultado = True

if busca_lower and not algum_resultado:
    st.info(f"Nenhuma pergunta encontrada para \"{busca}\".")

footer()
