# 🧪 Guia de Teste - Sistema de Login com Cookies

## ✅ Sistema Instalado e Configurado

O sistema de cookies foi atualizado com sucesso:
- ✅ `extra-streamlit-components` instalado
- ✅ Fallback para `streamlit-cookies-controller`
- ✅ Logs detalhados implementados
- ✅ Interface de diagnóstico criada
- ✅ Tratamento robusto de erros

## 🚀 Como Testar

### 1. Iniciar a Aplicação

```bash
streamlit run app.py
```

### 2. Teste Básico - Login Normal (SEM manter logado)

**Objetivo:** Verificar que o login funciona corretamente

1. Acesse a aplicação no navegador
2. Faça login com:
   - **Telefone:** `41997813606`
   - **Código:** `TJPR-F4F1X5`
   - **NÃO** marque "Manter-me logado"
3. ✅ **Esperado:** Login bem-sucedido, acesso ao sistema

**Teste de persistência:**
4. Atualize a página (F5)
5. ✅ **Esperado:** Continua logado (sessão do navegador)
6. Feche o navegador completamente
7. Abra novamente e acesse a aplicação
8. ✅ **Esperado:** Precisa fazer login novamente

---

### 3. Teste Principal - Login Persistente (COM manter logado)

**Objetivo:** Verificar que os cookies persistem após fechar o navegador

1. Acesse a aplicação no navegador
2. Faça login com:
   - **Telefone:** `41997813606`
   - **Código:** `TJPR-F4F1X5`
   - ✅ **Marque** "Manter-me logado"
3. ✅ **Esperado:** Login bem-sucedido
4. ✅ **Esperado:** Mensagem de confirmação sobre cookies

**Teste de persistência:**
5. Feche o navegador **completamente**
6. Espere 5 segundos
7. Abra o navegador novamente
8. Acesse a aplicação
9. ✅ **Esperado:** Login automático com mensagem "Sessão restaurada automaticamente via cookies"

---

### 4. Teste de Diagnóstico de Cookies

**Objetivo:** Verificar status dos cookies em tempo real

**Na tela de login:**
1. Expanda "🔧 Diagnóstico de Cookies (Debug)"
2. ✅ **Deve mostrar:**
   - "Sistema de cookies disponível: **stx**"
   - Token de autenticação: Ausente (antes do login)
   - Lembrar login: Inativo (antes do login)

**Após fazer login COM "Manter-me logado":**
3. Volte para tela de login (clique em Sair)
4. Expanda novamente o diagnóstico
5. ✅ **Deve mostrar:**
   - Token de autenticação: **Presente**
   - Lembrar login: **Ativo**
   - Sessão válida: **Sim**
   - Telefone: **(41) 99781-3606**

---

### 5. Teste de Logout

**Objetivo:** Verificar que o logout limpa os cookies

1. Faça login com "Manter-me logado"
2. No menu do app, clique em "🚪 Sair"
3. ✅ **Esperado:** Volta para tela de login
4. Abra o diagnóstico de cookies
5. ✅ **Esperado:**
   - Token: Ausente
   - Sessão válida: Não
6. Feche e abra o navegador
7. ✅ **Esperado:** Precisa fazer login novamente

---

### 6. Teste de Múltiplos Usuários

**Objetivo:** Verificar isolamento de sessões

1. Faça login com usuário A com "Manter-me logado"
2. Faça logout
3. Faça login com usuário B (diferente) sem "Manter-me logado"
4. Feche o navegador
5. Abra novamente
6. ✅ **Esperado:** Sessão do usuário A **NÃO** deve ser restaurada (pois fez logout)

---

### 7. Teste de Logs

**Objetivo:** Verificar que todas as operações estão sendo registradas

1. Navegue até a pasta `logs/`
2. Abra o arquivo mais recente: `simulador_YYYYMMDD.log`
3. ✅ **Deve conter:**
   - `OPERATION: session_init | USER: system | DETAILS: Usando extra_streamlit_components`
   - `OPERATION: criar_sessao_persistente | USER: 41997813606`
   - `OPERATION: verificar_sessao | USER: 41997813606 | DETAILS: Sessão válida encontrada`
   - `OPERATION: obter_telefone | USER: 41997813606`
   - `OPERATION: limpar_sessao | USER: system`

**Ver logs em tempo real (Windows):**
```powershell
Get-Content logs\simulador_*.log -Wait -Tail 20
```

**Linux/Mac:**
```bash
tail -f logs/simulador_*.log
```

---

## 🐛 Troubleshooting

### Problema: Cookies não persistem

**Verificações:**

1. **Navegador em modo privado?**
   - ❌ Modo anônimo não salva cookies
   - ✅ Use navegador normal

2. **Configurações de privacidade:**
   - Abra: `chrome://settings/cookies`
   - ✅ Deve estar "Permitir todos os cookies"

3. **Extensões de bloqueio:**
   - Desative temporariamente:
     - Privacy Badger
     - uBlock Origin
     - Ghostery

4. **Verificar cookies no navegador:**
   - F12 → Application → Cookies → localhost
   - ✅ Deve ter: `auth_token` e `remember_me`

### Problema: Erro "Sistema de cookies indisponível"

**Solução:**
```bash
pip install extra-streamlit-components
```

Depois reinicie o Streamlit.

### Problema: Login funciona mas não persiste

**Debug:**

1. Abra o diagnóstico de cookies
2. Verifique se "Token de autenticação" está **Presente**
3. Se ausente, verifique os logs:
   ```bash
   grep -i "criar_sessao" logs/simulador_*.log
   ```
4. Se houver erros, copie e reporte

### Problema: Mensagem "Sessão restaurada" mas deslogado

**Causa:** Token expirou ou foi invalidado

**Solução:**
1. F12 → Application → Cookies
2. Delete `auth_token` e `remember_me`
3. Faça login novamente

---

## 📊 Checklist de Validação

Use este checklist para validar completamente o sistema:

- [ ] Aplicação inicia sem erros
- [ ] Login sem "Manter-me logado" funciona
- [ ] Login sem "Manter-me logado" **não** persiste após fechar navegador
- [ ] Login COM "Manter-me logado" funciona
- [ ] Login COM "Manter-me logado" **persiste** após fechar navegador
- [ ] Mensagem "Sessão restaurada automaticamente" aparece
- [ ] Diagnóstico de cookies mostra "Sistema disponível: stx"
- [ ] Diagnóstico mostra token presente após login
- [ ] Logout limpa os cookies corretamente
- [ ] Logout impede restauração automática
- [ ] Logs registram todas as operações
- [ ] Não há erros no console do navegador (F12)
- [ ] Não há erros nos logs Python

---

## 🔐 Segurança

### Dados Armazenados nos Cookies

Os cookies armazenam:
- `auth_token`: Token hash gerado a partir do telefone
- `remember_me`: Flag booleana

**NÃO armazena:**
- ❌ Senhas ou códigos de acesso
- ❌ Dados pessoais sensíveis
- ❌ Informações de inscrição

### Formato do Token

```
auth_token = base64(telefone) + ":" + sha256(telefone + timestamp + secret)
```

### Expiração

- **Com "Manter-me logado":** 30 dias
- **Sem "Manter-me logado":** Até fechar navegador

### Alterar Chave Secreta (Produção)

Edite `config/settings.py`:
```python
COOKIE_SECRET_KEY = "sua-chave-secreta-aqui"
```

Gere uma chave forte:
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## 📈 Monitoramento em Produção

### Verificar Taxa de Sucesso de Cookies

```bash
grep "criar_sessao_persistente" logs/*.log | wc -l
```

### Identificar Problemas Frequentes

```bash
grep "ERROR" logs/*.log | grep "session"
```

### Ver Usuários com Sessão Ativa

```bash
grep "Sessão válida encontrada" logs/*.log | tail -20
```

---

## 🎯 Cenários de Uso Real

### Cenário 1: Usuário Mobile

1. Acessa pelo celular
2. Faz login COM "Manter-me logado"
3. Fecha o app (Chrome/Safari)
4. Abre dias depois
5. ✅ Login automático

### Cenário 2: Usuário Desktop

1. Acessa pelo computador do trabalho
2. Faz login SEM "Manter-me logado"
3. Fecha o navegador no fim do expediente
4. ✅ Precisa fazer login novamente (segurança)

### Cenário 3: Múltiplos Dispositivos

1. Login no celular COM "Manter-me logado"
2. Login no computador SEM "Manter-me logado"
3. Ambas as sessões são independentes
4. ✅ Celular persiste, computador não

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `logs/simulador_YYYYMMDD.log`
2. Capture screenshot do diagnóstico de cookies
3. Abra F12 → Console e copie erros JavaScript
4. Reporte com todas as informações acima

---

**Última atualização:** 2025-11-30
**Versão do sistema:** 2.0 - Login com Cookies Persistentes
