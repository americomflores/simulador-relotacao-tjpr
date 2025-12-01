# 📚 Documentação - Simulador de Relotação TJPR

## 📖 Índice de Documentos

### 🍪 Sistema de Login com Cookies

1. **[RESUMO_MELHORIAS_COOKIES.md](RESUMO_MELHORIAS_COOKIES.md)**
   - 📋 Resumo executivo das melhorias
   - ✅ Comparação antes vs depois
   - 📊 Métricas de sucesso
   - 🎯 Benefícios alcançados
   - **Leia primeiro!**

2. **[MELHORIAS_COOKIES.md](MELHORIAS_COOKIES.md)**
   - 🔧 Detalhamento técnico completo
   - 📝 Problemas identificados e soluções
   - 🧪 Instruções de troubleshooting
   - 🔐 Considerações de segurança
   - **Para desenvolvedores**

3. **[GUIA_TESTE_LOGIN.md](GUIA_TESTE_LOGIN.md)**
   - 🧪 7 cenários de teste detalhados
   - ✅ Checklist de validação
   - 🐛 Solução de problemas comuns
   - 📊 Monitoramento em produção
   - **Para testadores e QA**

4. **[DEPLOY_ATUALIZACAO_COOKIES.md](DEPLOY_ATUALIZACAO_COOKIES.md)**
   - 🚀 Instruções de deploy
   - ⚡ Quick start (5 minutos)
   - 📦 Deploy em produção
   - 🔄 Procedimentos de rollback
   - **Para DevOps e administradores**

---

## 🚀 Quick Start

### Para Usuários

1. Acesse a aplicação
2. Faça login normalmente
3. ✅ Marque "Manter-me logado" para login automático
4. ❌ Deixe desmarcado para maior segurança em computadores compartilhados

### Para Desenvolvedores

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar aplicação
streamlit run app.py

# 3. Testar cookies (opcional)
python test_cookies.py

# 4. Ver logs
tail -f logs/simulador_*.log
```

### Para Administradores

1. Ler [RESUMO_MELHORIAS_COOKIES.md](RESUMO_MELHORIAS_COOKIES.md)
2. Seguir [DEPLOY_ATUALIZACAO_COOKIES.md](DEPLOY_ATUALIZACAO_COOKIES.md)
3. Validar com [GUIA_TESTE_LOGIN.md](GUIA_TESTE_LOGIN.md)
4. Monitorar logs em produção

---

## 📋 Fluxo de Leitura Recomendado

### Se você é novo no projeto:
1. `../CLAUDE.md` - Visão geral do projeto
2. `RESUMO_MELHORIAS_COOKIES.md` - Entender as melhorias
3. `GUIA_TESTE_LOGIN.md` - Testar o sistema

### Se vai fazer deploy:
1. `RESUMO_MELHORIAS_COOKIES.md` - Entender mudanças
2. `DEPLOY_ATUALIZACAO_COOKIES.md` - Seguir instruções
3. `GUIA_TESTE_LOGIN.md` - Validar deploy

### Se está debugando problemas:
1. `GUIA_TESTE_LOGIN.md` → Seção "Troubleshooting"
2. `MELHORIAS_COOKIES.md` → Seção "Troubleshooting Comum"
3. Verificar `logs/simulador_*.log`
4. Usar diagnóstico visual na tela de login

### Se está desenvolvendo:
1. `MELHORIAS_COOKIES.md` - Arquitetura completa
2. `../services/session_service.py` - Código-fonte
3. `../test_cookies.py` - Testes

---

## 🔍 Informações Técnicas Rápidas

### Arquivos Principais

| Arquivo | Descrição | Linhas |
|---------|-----------|--------|
| `app.py` | Aplicação principal | ~3700 |
| `services/session_service.py` | Gerenciamento de cookies | ~340 |
| `services/auth_service.py` | Autenticação | ~130 |
| `config/settings.py` | Configurações | ~13 |

### Dependências Críticas

```txt
streamlit>=1.40.1
extra-streamlit-components>=0.1.71  # Nova!
streamlit-cookies-controller         # Fallback
```

### Variáveis de Ambiente

```bash
COOKIE_SECRET_KEY="sua-chave-secreta"  # Alterar em produção!
```

---

## 🐛 Debug Rápido

### Problema: Cookies não funcionam

1. **Verificar instalação:**
   ```bash
   pip show extra-streamlit-components
   ```

2. **Ver diagnóstico:**
   - Abrir tela de login
   - Expandir "🔧 Diagnóstico de Cookies"

3. **Verificar logs:**
   ```bash
   grep "session" logs/simulador_*.log | tail -20
   ```

### Problema: Login não persiste

1. Navegador em modo privado?
2. Cookies bloqueados?
3. Verificar F12 → Application → Cookies → `auth_token`

---

## 📞 Suporte

### Problemas Comuns
- Consulte seção "Troubleshooting" em cada documento
- Verifique logs em `../logs/`
- Use diagnóstico visual na aplicação

### Reportar Bugs
1. Screenshot do diagnóstico de cookies
2. Últimas 50 linhas do log
3. Descrição do problema
4. Passos para reproduzir

### Contato
- **Admin:** (41) 99781-3606
- **Logs:** `../logs/simulador_YYYYMMDD.log`

---

## 📊 Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| 2.0 | 2025-11-30 | Sistema de cookies com fallback, logs, diagnóstico |
| 1.0 | 2025-XX-XX | Versão inicial |

---

## 🎯 Próximos Passos

Após ler a documentação:

1. ✅ Testar localmente
2. ✅ Fazer deploy em staging (se aplicável)
3. ✅ Validar em produção
4. ✅ Monitorar por 24h
5. ✅ Coletar feedback dos usuários

---

**Última atualização:** 2025-11-30
**Mantenedor:** Sistema
