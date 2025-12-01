# Teste Rápido - Sistema de Login

## ⚡ Teste Express (5 minutos)

### 1. Verificar Instalação
```bash
# Verificar se streamlit-cookies-controller está instalado
pip show streamlit-cookies-controller
```

### 2. Executar Aplicação
```bash
streamlit run app.py
```

### 3. Teste Rápido de Login

**Cenário 1 - Login Normal**:
1. Acesse `http://localhost:8501`
2. Digite telefone: `41997813606`
3. Digite código: `TJPR-F4F1X5`
4. **NÃO** marque "Manter-me logado"
5. Clique "Entrar"
6. ✅ Deve entrar normalmente

**Cenário 2 - Login com Persistência**:
1. Clique "🚪 Sair"
2. Faça login novamente
3. **MARQUE** "Manter-me logado"
4. Clique "Entrar"
5. Recarregue a página (F5)
6. ✅ Deve restaurar sessão automaticamente

**Cenário 3 - Logout**:
1. Clique "🚪 Sair"
2. Recarregue a página
3. ✅ Deve pedir login novamente

### 4. Verificar Logs
```bash
# Windows PowerShell
Get-Content logs\*.log -Tail 20

# Linux/Mac
tail -20 logs/*.log
```

Procure por:
- `OPERATION: login_success`
- `OPERATION: criar_sessao_persistente`
- Sem erros (`ERROR:`)

---

## ✅ Tudo OK?

Se todos os cenários funcionaram:
- ✅ Sistema está pronto para commit
- ✅ Login com persistência funcionando
- ✅ Logout limpa tudo corretamente

Se algo falhou:
- Verifique `TESTE_LOGIN.md` para troubleshooting
- Verifique logs em `logs/`
- Execute testes automatizados: `pytest -v`

