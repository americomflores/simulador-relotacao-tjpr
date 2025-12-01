"""
Script de teste para validar o sistema de cookies.
Execute: python test_cookies.py
"""
import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 no Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from services.session_service import get_session_service
from utils.logger import log_operation


def test_session_service():
    """Testa o SessionService."""
    print("=" * 60)
    print("TESTE DO SISTEMA DE COOKIES")
    print("=" * 60)

    session_service = get_session_service()

    # Teste 1: Verificar inicialização
    print("\n1. Verificando inicialização do serviço...")
    if session_service.cookie_manager or session_service.cookies:
        print(f"   ✅ Serviço inicializado com sucesso")
        print(f"   📦 Método: {session_service.method}")
    else:
        print(f"   ❌ Falha na inicialização - nenhuma biblioteca de cookies disponível")
        return False

    # Teste 2: Status dos cookies
    print("\n2. Verificando status dos cookies...")
    status = session_service.obter_status_cookies()
    print(f"   Disponível: {status['disponivel']}")
    print(f"   Método: {status['metodo']}")
    print(f"   Auth Token: {'Presente' if status['tem_auth_token'] else 'Ausente'}")
    print(f"   Remember Me: {'Ativo' if status['tem_remember_me'] else 'Inativo'}")
    print(f"   Sessão Válida: {'Sim' if status['sessao_valida'] else 'Não'}")
    if status['telefone']:
        print(f"   Telefone: {status['telefone']}")
    if status['erro']:
        print(f"   ⚠️ Erro: {status['erro']}")

    # Teste 3: Criar sessão de teste
    print("\n3. Testando criação de sessão persistente...")
    telefone_teste = "41997813606"
    resultado = session_service.criar_sessao_persistente(telefone_teste, manter_logado=True)
    if resultado:
        print(f"   ✅ Sessão criada com sucesso para {telefone_teste}")
    else:
        print(f"   ❌ Falha ao criar sessão")
        return False

    # Teste 4: Verificar sessão criada
    print("\n4. Verificando sessão persistente...")
    if session_service.verificar_sessao_persistente():
        print(f"   ✅ Sessão persistente detectada")
        telefone_recuperado = session_service.obter_telefone_do_cookie()
        if telefone_recuperado == telefone_teste:
            print(f"   ✅ Telefone recuperado corretamente: {telefone_recuperado}")
        else:
            print(f"   ❌ Telefone incorreto. Esperado: {telefone_teste}, Obtido: {telefone_recuperado}")
            return False
    else:
        print(f"   ❌ Sessão persistente não detectada")
        return False

    # Teste 5: Limpar sessão
    print("\n5. Testando limpeza de sessão...")
    if session_service.limpar_sessao():
        print(f"   ✅ Sessão limpa com sucesso")
    else:
        print(f"   ⚠️ Aviso: Problemas ao limpar sessão")

    # Teste 6: Verificar após limpeza
    print("\n6. Verificando após limpeza...")
    status_final = session_service.obter_status_cookies()
    if not status_final['sessao_valida']:
        print(f"   ✅ Cookies limpos corretamente")
    else:
        print(f"   ⚠️ Cookies ainda presentes após limpeza")

    print("\n" + "=" * 60)
    print("TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 60)

    return True


def main():
    """Função principal."""
    print("\n🔧 Script de Teste do Sistema de Cookies\n")

    try:
        sucesso = test_session_service()

        if sucesso:
            print("\n✅ Sistema de cookies está funcionando corretamente!")
            print("\n📋 Próximos passos:")
            print("   1. Execute: streamlit run app.py")
            print("   2. Faça login marcando 'Manter-me logado'")
            print("   3. Feche o navegador e abra novamente")
            print("   4. Verifique se o login persiste")
            print("\n💡 Dica: Abra 'Diagnóstico de Cookies' na tela de login para debug\n")
            return 0
        else:
            print("\n❌ Alguns testes falharam. Verifique os logs acima.\n")
            return 1

    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
