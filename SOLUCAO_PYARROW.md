# Solução Rápida para Erro do pyarrow

## 🎯 Solução Mais Rápida

O `pyarrow` não é necessário para o sistema funcionar. Siga estes passos:

### Passo 1: Instalar apenas o essencial

```bash
pip install streamlit streamlit-cookies-controller
```

### Passo 2: Testar se funciona

```bash
streamlit run app.py
```

**Se funcionar**: ✅ Pronto! O resto pode ser instalado depois.

**Se der erro de importação**: Continue com o Passo 3.

### Passo 3: Instalar dependências restantes (se necessário)

```bash
# Instalar uma por uma, ignorando erros de build
pip install pandas --no-build-isolation
pip install gspread
pip install google-auth
pip install openpyxl
```

### Passo 4: Se pandas ainda falhar

```bash
# Usar versão específica que tem wheel pré-compilado
pip install "pandas>=2.0.0,<3.0.0" --only-binary :all:
```

---

## 🔍 Por que isso funciona?

- `pyarrow` é uma dependência **opcional** do pandas
- O sistema funciona sem ele (apenas algumas operações podem ser mais lentas)
- `streamlit-cookies-controller` não depende de pyarrow
- O sistema de login funciona independente do pandas

---

## ✅ Verificação Final

```bash
# Teste se o essencial está instalado
python -c "import streamlit; from streamlit_cookies_controller import CookiesController; print('✅ OK')"
```

Se imprimir "✅ OK", você pode testar o sistema de login!

---

**Dica**: Se precisar do pandas depois (para funcionalidades do simulador), tente instalar em outro momento ou use uma versão pré-compilada.

