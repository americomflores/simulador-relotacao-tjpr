# Guia de Testes - Sistema de Login com Persistência

## 🧪 Testes Manuais

### Pré-requisitos
1. Certifique-se de que todas as dependências estão instaladas:
   ```bash
   pip install -r requirements.txt
   ```

2. Verifique se o `secrets.toml` está configurado corretamente

3. Inicie o Streamlit:
   ```bash
   streamlit run app.py
   ```

---

## 📋 Checklist de Testes

### 1. Teste de Login Básico

**Objetivo**: Verificar se o login funciona normalmente

**Passos**:
1. Acesse a aplicação
2. Digite um telefone válido (ex: 41997813606)
3. Digite o código correspondente (ex: TJPR-F4F1X5)
4. **NÃO** marque "Manter-me logado"
5. Clique em "Entrar"

**Resultado Esperado**:
- ✅ Login bem-sucedido
- ✅ Redirecionamento para a interface principal
- ✅ Mensagem de sucesso aparece brevemente
- ✅ Sidebar mostra telefone formatado

---

### 2. Teste de "Manter-me logado" (Sessão Persistente)

**Objetivo**: Verificar se a sessão persiste após fechar/recarregar

**Passos**:
1. Faça logout (se estiver logado)
2. Faça login novamente
3. **MARQUE** a opção "Manter-me logado"
4. Clique em "Entrar"
5. Após login bem-sucedido, **recarregue a página** (F5 ou Ctrl+R)

**Resultado Esperado**:
- ✅ Login bem-sucedido
- ✅ Após recarregar, você permanece logado
- ✅ Mensagem "✅ Sessão restaurada automaticamente" aparece
- ✅ Não precisa fazer login novamente

---

### 3. Teste de Sessão Temporária (Sem "Manter-me logado")

**Objetivo**: Verificar que sem a opção marcada, a sessão não persiste

**Passos**:
1. Faça logout
2. Faça login **SEM** marcar "Manter-me logado"
3. Após login, **feche completamente o navegador**
4. Abra o navegador novamente e acesse a aplicação

**Resultado Esperado**:
- ✅ Login funciona normalmente
- ✅ Após fechar e reabrir navegador, você precisa fazer login novamente
- ✅ Cookie não persiste entre sessões do navegador

---

### 4. Teste de Restauração Automática

**Objetivo**: Verificar restauração de sessão ao recarregar

**Passos**:
1. Faça login com "Manter-me logado" marcado
2. Navegue pela aplicação (vá para diferentes abas)
3. Recarregue a página (F5)

**Resultado Esperado**:
- ✅ Sessão é restaurada automaticamente
- ✅ Você permanece na mesma aba/contexto
- ✅ Mensagem de sessão restaurada aparece uma vez

---

### 5. Teste de Logout

**Objetivo**: Verificar se o logout limpa tudo corretamente

**Passos**:
1. Faça login com "Manter-me logado" marcado
2. Navegue pela aplicação
3. Clique em "🚪 Sair" no sidebar

**Resultado Esperado**:
- ✅ Volta para tela de login
- ✅ Session state é limpo
- ✅ Cookies são removidos
- ✅ Ao recarregar, você precisa fazer login novamente

---

### 6. Teste de Validação de Credenciais

**Objetivo**: Verificar mensagens de erro

**Teste 6.1 - Telefone Inválido**:
- Digite telefone com menos de 10 dígitos
- Resultado esperado: ❌ Mensagem "Telefone inválido!"

**Teste 6.2 - Código Inválido**:
- Digite telefone válido mas código errado
- Resultado esperado: ❌ Mensagem "Telefone ou código inválido!"

**Teste 6.3 - Campos Vazios**:
- Tente entrar sem preencher nada
- Resultado esperado: ❌ Mensagem "Preencha o telefone e o código!"

---

### 7. Teste de Campo de Código Oculto

**Objetivo**: Verificar que o código é ocultado durante digitação

**Passos**:
1. Acesse a tela de login
2. Clique no campo "Código de Acesso"
3. Digite um código

**Resultado Esperado**:
- ✅ O texto digitado aparece como asteriscos (•••••)
- ✅ Campo funciona como password

---

### 8. Teste de Preview de Telefone

**Objetivo**: Verificar formatação em tempo real

**Passos**:
1. Na tela de login, digite um telefone
2. Observe o preview abaixo do campo

**Resultado Esperado**:
- ✅ Preview mostra telefone formatado: (41) 99781-3606
- ✅ Atualiza em tempo real conforme você digita

---

## 🔍 Testes Automatizados

Execute os testes unitários:

```bash
# Todos os testes
pytest

# Apenas testes de autenticação
pytest tests/test_auth.py -v

# Com cobertura
pytest --cov=services --cov=utils --cov-report=html

# Testes específicos de sessão (quando criados)
pytest tests/test_session.py -v
```

---

## 🐛 Problemas Comuns e Soluções

### Problema: "Sessão não persiste após recarregar"

**Possíveis causas**:
1. Cookies bloqueados pelo navegador
   - **Solução**: Verifique configurações de cookies do navegador
   - Permita cookies para o domínio do Streamlit

2. `streamlit-cookies-controller` não instalado
   - **Solução**: `pip install streamlit-cookies-controller`

3. Erro no serviço de sessão
   - **Solução**: Verifique os logs em `logs/`

### Problema: "Erro ao importar session_service"

**Possíveis causas**:
1. Módulo não encontrado
   - **Solução**: Verifique se `services/session_service.py` existe
   - Verifique se `services/__init__.py` existe

2. Dependências faltando
   - **Solução**: `pip install -r requirements.txt`

### Problema: "Token inválido"

**Possíveis causas**:
1. Cookie corrompido
   - **Solução**: Limpe cookies do navegador e faça login novamente

2. `COOKIE_SECRET_KEY` alterado
   - **Solução**: Mantenha a mesma chave ou limpe todos os cookies

---

## 📊 Verificação de Logs

Verifique os logs para debug:

```bash
# Ver último log
tail -f logs/simulador_*.log

# Ou no Windows PowerShell
Get-Content logs/simulador_*.log -Tail 50 -Wait
```

Procure por:
- `OPERATION: login_success`
- `OPERATION: criar_sessao_persistente`
- `OPERATION: limpar_sessao`
- `ERROR:` (qualquer erro)

---

## ✅ Checklist Final Antes do Commit

- [ ] Login funciona com credenciais válidas
- [ ] Login falha com credenciais inválidas (mensagens corretas)
- [ ] "Manter-me logado" persiste sessão por 30 dias
- [ ] Sem "Manter-me logado", sessão é temporária
- [ ] Sessão é restaurada automaticamente ao recarregar
- [ ] Logout limpa session state e cookies
- [ ] Campo de código está oculto (password)
- [ ] Preview de telefone funciona
- [ ] Testes automatizados passam: `pytest`
- [ ] Sem erros nos logs
- [ ] Interface está responsiva e funcional

---

## 🚀 Comandos Rápidos

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py

# Executar testes
pytest -v

# Verificar lint
pylint services/session_service.py

# Limpar cache do Streamlit (se necessário)
rm -rf .streamlit/cache
```

---

**Última atualização**: 2025

