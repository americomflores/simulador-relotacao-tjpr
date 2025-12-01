# Como Testar Antes do Commit

## 🚀 Passo a Passo Rápido

### 1. Instalar Dependências (se necessário)

**⚠️ Se tiver erro com pyarrow**, veja `SOLUCAO_PYARROW.md` primeiro!

**Instalação normal**:
```bash
pip install -r requirements.txt
```

**Se der erro de pyarrow** (dependência opcional):
```bash
# Instalar apenas o essencial para testar login
pip install streamlit streamlit-cookies-controller

# O resto pode ser instalado depois se necessário
```

**Verificar instalação**:
```bash
pip show streamlit-cookies-controller
```

Se não estiver instalado, instale:
```bash
pip install streamlit-cookies-controller
```

---

### 2. Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`

---

### 3. Testes Manuais Essenciais

#### ✅ Teste 1: Login Básico
1. Na tela de login, digite:
   - Telefone: `41997813606`
   - Código: `TJPR-F4F1X5`
   - **NÃO** marque "Manter-me logado"
2. Clique em "🚀 Entrar"
3. **Resultado esperado**: Login bem-sucedido, entra na aplicação

#### ✅ Teste 2: Login com Persistência
1. Se estiver logado, clique em "🚪 Sair"
2. Faça login novamente:
   - Telefone: `41997813606`
   - Código: `TJPR-F4F1X5`
   - **MARQUE** "🔒 Manter-me logado"
3. Clique em "🚀 Entrar"
4. Após entrar, **recarregue a página** (F5 ou Ctrl+R)
5. **Resultado esperado**: 
   - Mensagem "✅ Sessão restaurada automaticamente"
   - Você permanece logado (não volta para tela de login)

#### ✅ Teste 3: Logout Completo
1. Estando logado, clique em "🚪 Sair"
2. **Resultado esperado**: Volta para tela de login
3. Recarregue a página (F5)
4. **Resultado esperado**: Continua na tela de login (não restaura sessão)

#### ✅ Teste 4: Validações
1. Tente entrar sem preencher nada
   - **Esperado**: Mensagem "❌ Preencha o telefone e o código!"
2. Digite telefone inválido (menos de 10 dígitos)
   - **Esperado**: Mensagem "❌ Telefone inválido!"
3. Digite telefone válido mas código errado
   - **Esperado**: Mensagem "❌ Telefone ou código inválido!"

#### ✅ Teste 5: Campo de Código Oculto
1. Na tela de login, digite no campo "Código de Acesso"
2. **Resultado esperado**: O texto aparece como asteriscos (•••••)

---

### 4. Verificar Logs

**Windows PowerShell**:
```powershell
Get-Content logs\*.log -Tail 30
```

**Linux/Mac**:
```bash
tail -30 logs/*.log
```

**O que procurar**:
- ✅ `OPERATION: login_success` - Login funcionou
- ✅ `OPERATION: criar_sessao_persistente` - Cookie foi criado
- ✅ `OPERATION: limpar_sessao` - Logout funcionou
- ❌ `ERROR:` - Se aparecer, há problema

---

### 5. Testes Automatizados (Opcional)

Se quiser executar os testes automatizados:

```bash
# Instalar pytest (se não tiver)
pip install pytest pytest-cov pytest-mock

# Executar todos os testes
pytest -v

# Apenas testes de autenticação
pytest tests/test_auth.py -v

# Com cobertura de código
pytest --cov=services --cov=utils --cov-report=html
```

---

## 🐛 Troubleshooting

### Problema: "Sessão não persiste"

**Soluções**:
1. Verifique se `streamlit-cookies-controller` está instalado:
   ```bash
   pip install streamlit-cookies-controller
   ```

2. Verifique configurações de cookies do navegador:
   - Permita cookies para `localhost:8501`
   - Não use modo anônimo/privado

3. Verifique logs em `logs/` para erros

### Problema: "Erro ao importar session_service"

**Soluções**:
1. Verifique se o arquivo existe:
   ```bash
   ls services/session_service.py  # Linux/Mac
   dir services\session_service.py  # Windows
   ```

2. Verifique se `services/__init__.py` existe

3. Reinstale dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Problema: "Token inválido"

**Soluções**:
1. Limpe cookies do navegador:
   - Chrome: F12 → Application → Cookies → Delete
   - Firefox: F12 → Storage → Cookies → Delete All

2. Faça login novamente

---

## ✅ Checklist Antes do Commit

Marque cada item após testar:

- [ ] Login funciona com credenciais válidas
- [ ] Login falha corretamente com credenciais inválidas
- [ ] "Manter-me logado" persiste sessão (teste recarregar página)
- [ ] Sem "Manter-me logado", sessão é temporária
- [ ] Logout limpa tudo (teste recarregar após logout)
- [ ] Campo de código está oculto (password)
- [ ] Preview de telefone funciona
- [ ] Mensagens de erro aparecem corretamente
- [ ] Logs não mostram erros críticos
- [ ] Interface está responsiva

---

## 📝 Comandos Úteis

```bash
# Limpar cache do Streamlit (se necessário)
rm -rf .streamlit/cache  # Linux/Mac
rmdir /s .streamlit\cache  # Windows

# Verificar sintaxe Python
python -m py_compile services/session_service.py
python -m py_compile app.py

# Verificar imports
python -c "from services.session_service import get_session_service; print('OK')"
```

---

## 🎯 Teste Rápido (2 minutos)

Se estiver com pressa, faça apenas estes 3 testes:

1. **Login + Recarregar**: 
   - Login com "Manter-me logado" → Recarregar → Deve manter logado ✅

2. **Logout + Recarregar**: 
   - Logout → Recarregar → Deve pedir login ✅

3. **Verificar logs**: 
   - `Get-Content logs\*.log -Tail 10` → Sem erros ✅

Se esses 3 passarem, está pronto para commit! 🚀

