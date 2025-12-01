# Instalação Alternativa - Resolvendo Erro do pyarrow

## 🔧 Problema

O erro `Failed to build pyarrow` acontece porque o `pyarrow` precisa ser compilado e requer `cmake`. Mas **não precisamos do pyarrow diretamente** - é apenas uma dependência opcional do pandas.

## ✅ Solução 1: Instalar sem pyarrow (Recomendado)

Instale as dependências uma por uma, pulando problemas de build:

```bash
# Instalar dependências essenciais primeiro
pip install streamlit
pip install pandas
pip install gspread
pip install google-auth
pip install openpyxl
pip install streamlit-cookies-controller

# Instalar dependências de teste (opcional)
pip install pytest pytest-cov pytest-mock
```

Se o pandas tentar instalar pyarrow e falhar, use:

```bash
# Instalar pandas sem pyarrow
pip install pandas --no-deps
pip install numpy python-dateutil pytz
```

## ✅ Solução 2: Usar versões específicas com wheels pré-compilados

```bash
# Versões que têm wheels pré-compilados (não precisam compilar)
pip install streamlit>=1.28.0
pip install pandas>=2.0.0
pip install gspread>=5.0.0
pip install google-auth>=2.0.0
pip install openpyxl>=3.1.0
pip install streamlit-cookies-controller>=0.2.0
```

## ✅ Solução 3: Instalar pyarrow pré-compilado (Windows)

```bash
# Tentar instalar pyarrow diretamente (pode ter wheel pré-compilado)
pip install pyarrow

# Se funcionar, então instalar o resto
pip install -r requirements.txt
```

## ✅ Solução 4: Instalar apenas o necessário para testar

Para testar o sistema de login, você só precisa:

```bash
pip install streamlit
pip install streamlit-cookies-controller
```

As outras dependências (pandas, gspread) só são necessárias quando você usar funcionalidades que dependem delas.

## 🧪 Teste Rápido sem Todas as Dependências

Se quiser testar apenas o sistema de login sem instalar tudo:

1. **Instale apenas o essencial**:
   ```bash
   pip install streamlit streamlit-cookies-controller
   ```

2. **Crie um arquivo de teste simples** (`test_login_simples.py`):
   ```python
   import streamlit as st
   from services.session_service import get_session_service
   
   st.title("Teste de Login")
   
   session_service = get_session_service()
   st.write("SessionService criado:", session_service is not None)
   ```

3. **Execute**:
   ```bash
   streamlit run test_login_simples.py
   ```

## 📋 Verificação Rápida

Após instalar, verifique:

```bash
# Verificar se streamlit-cookies-controller está instalado
python -c "from streamlit_cookies_controller import CookiesController; print('OK')"

# Verificar se session_service funciona
python -c "from services.session_service import get_session_service; print('OK')"
```

Se ambos retornarem "OK", o sistema de login está pronto para testar!

## 🚀 Próximos Passos

Depois de resolver a instalação:

1. Execute: `streamlit run app.py`
2. Teste o login conforme `COMO_TESTAR.md`
3. Se funcionar, está pronto para commit!

---

**Nota**: O pyarrow é opcional. O sistema funciona sem ele, apenas algumas funcionalidades do pandas podem ser mais lentas.

