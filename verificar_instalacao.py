"""
Script de verificação rápida das dependências e estrutura do projeto.
Execute antes de fazer commit para garantir que tudo está OK.
"""
import sys
import os

def verificar_importacoes():
    """Verifica se todas as importações necessárias funcionam."""
    print("🔍 Verificando importações...")
    
    erros = []
    
    try:
        import streamlit
        print("  ✅ streamlit")
    except ImportError as e:
        erros.append(f"  ❌ streamlit: {e}")
    
    try:
        import pandas
        print("  ✅ pandas")
    except ImportError as e:
        erros.append(f"  ❌ pandas: {e}")
    
    try:
        import gspread
        print("  ✅ gspread")
    except ImportError as e:
        erros.append(f"  ❌ gspread: {e}")
    
    try:
        from streamlit_cookies_controller import CookiesController
        print("  ✅ streamlit-cookies-controller")
    except ImportError as e:
        erros.append(f"  ❌ streamlit-cookies-controller: {e}")
        print("     💡 Execute: pip install streamlit-cookies-controller")
    
    try:
        from services.session_service import get_session_service
        print("  ✅ services.session_service")
    except ImportError as e:
        erros.append(f"  ❌ services.session_service: {e}")
    
    try:
        from services.auth_service import verificar_login
        print("  ✅ services.auth_service")
    except ImportError as e:
        erros.append(f"  ❌ services.auth_service: {e}")
    
    try:
        from config.settings import COOKIE_EXPIRATION_DAYS, COOKIE_SECRET_KEY
        print("  ✅ config.settings")
    except ImportError as e:
        erros.append(f"  ❌ config.settings: {e}")
    
    try:
        from utils.logger import log_operation
        print("  ✅ utils.logger")
    except ImportError as e:
        erros.append(f"  ❌ utils.logger: {e}")
    
    if erros:
        print("\n❌ Erros encontrados:")
        for erro in erros:
            print(erro)
        return False
    
    print("\n✅ Todas as importações funcionaram!")
    return True


def verificar_arquivos():
    """Verifica se arquivos importantes existem."""
    print("\n📁 Verificando arquivos...")
    
    arquivos_necessarios = [
        "app.py",
        "services/session_service.py",
        "services/auth_service.py",
        "config/settings.py",
        "config/auth_config.py",
        "utils/logger.py",
        "requirements.txt",
    ]
    
    faltando = []
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"  ✅ {arquivo}")
        else:
            faltando.append(arquivo)
            print(f"  ❌ {arquivo} - NÃO ENCONTRADO")
    
    if faltando:
        print(f"\n❌ {len(faltando)} arquivo(s) faltando!")
        return False
    
    print("\n✅ Todos os arquivos necessários existem!")
    return True


def verificar_estrutura():
    """Verifica estrutura de diretórios."""
    print("\n📂 Verificando estrutura de diretórios...")
    
    diretorios = [
        "services",
        "config",
        "utils",
        "tests",
    ]
    
    faltando = []
    for diretorio in diretorios:
        if os.path.isdir(diretorio):
            print(f"  ✅ {diretorio}/")
        else:
            faltando.append(diretorio)
            print(f"  ❌ {diretorio}/ - NÃO ENCONTRADO")
    
    if faltando:
        print(f"\n❌ {len(faltando)} diretório(s) faltando!")
        return False
    
    print("\n✅ Estrutura de diretórios OK!")
    return True


def verificar_sintaxe():
    """Verifica sintaxe dos arquivos Python principais."""
    print("\n🔤 Verificando sintaxe Python...")
    
    arquivos = [
        "services/session_service.py",
        "services/auth_service.py",
        "config/settings.py",
    ]
    
    erros = []
    for arquivo in arquivos:
        if not os.path.exists(arquivo):
            continue
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                compile(f.read(), arquivo, 'exec')
            print(f"  ✅ {arquivo}")
        except SyntaxError as e:
            erros.append(f"  ❌ {arquivo}: {e}")
            print(f"  ❌ {arquivo}: Erro de sintaxe na linha {e.lineno}")
        except Exception as e:
            erros.append(f"  ❌ {arquivo}: {e}")
            print(f"  ❌ {arquivo}: {e}")
    
    if erros:
        print("\n❌ Erros de sintaxe encontrados!")
        return False
    
    print("\n✅ Sintaxe Python OK!")
    return True


def main():
    """Executa todas as verificações."""
    print("=" * 60)
    print("🔍 VERIFICAÇÃO DO PROJETO - Sistema de Login")
    print("=" * 60)
    
    resultados = []
    
    resultados.append(verificar_arquivos())
    resultados.append(verificar_estrutura())
    resultados.append(verificar_importacoes())
    resultados.append(verificar_sintaxe())
    
    print("\n" + "=" * 60)
    if all(resultados):
        print("✅ TODAS AS VERIFICAÇÕES PASSARAM!")
        print("🚀 Pronto para testar manualmente e fazer commit!")
        print("\n📋 Próximos passos:")
        print("   1. Execute: streamlit run app.py")
        print("   2. Teste login com 'Manter-me logado'")
        print("   3. Recarregue a página para verificar persistência")
        print("   4. Veja COMO_TESTAR.md para mais detalhes")
        return 0
    else:
        print("❌ ALGUMAS VERIFICAÇÕES FALHARAM!")
        print("🔧 Corrija os erros acima antes de fazer commit.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

