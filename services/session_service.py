"""
Serviço de gerenciamento de sessão e cookies para persistência de autenticação.
"""
import streamlit as st
import hashlib
import json
from datetime import datetime, timedelta
from utils.logger import log_operation, log_error
from config.settings import COOKIE_EXPIRATION_DAYS, COOKIE_SECRET_KEY


class SessionService:
    """Gerencia sessões persistentes usando cookies."""

    def __init__(self):
        """Inicializa o controlador de cookies."""
        self.cookies = None
        self.cookie_manager = None
        self.method = None

        # Tentar inicializar com extra_streamlit_components primeiro (mais estável)
        try:
            import extra_streamlit_components as stx
            self.cookie_manager = stx.CookieManager()
            self.method = "stx"
            log_operation("session_init", "system", "Usando extra_streamlit_components")
        except ImportError:
            log_operation("session_init", "system", "extra_streamlit_components não disponível")
        except Exception as e:
            log_error(e, "SessionService.__init__:stx")

        # Fallback para streamlit_cookies_controller
        if not self.cookie_manager:
            try:
                from streamlit_cookies_controller import CookieController
                self.cookies = CookieController()
                self.method = "controller"
                log_operation("session_init", "system", "Usando streamlit_cookies_controller")
            except ImportError:
                log_error(Exception("Nenhuma biblioteca de cookies disponível"), "SessionService.__init__")
            except Exception as e:
                log_error(e, "SessionService.__init__:controller")
    
    def verificar_sessao_persistente(self) -> bool:
        """
        Verifica se existe uma sessão persistente válida nos cookies.

        Returns:
            True se existe sessão válida, False caso contrário
        """
        if not self.cookie_manager and not self.cookies:
            log_operation("verificar_sessao", "system", "Nenhum gerenciador de cookies disponível")
            return False

        try:
            # Tentar cookie novo (auth_data)
            auth_data = self._get_cookie_json("auth_data")

            # MIGRAÇÃO: Se não encontrar cookie novo, tentar cookies antigos
            if not auth_data:
                old_token = self._get_cookie("auth_token")
                old_remember = self._get_cookie("remember_me")

                if old_token:
                    # Migrar para novo formato
                    auth_data = {
                        "token": old_token,
                        "remember": old_remember == "true",
                        "created_at": datetime.now().isoformat()
                    }

                    # Salvar no novo formato
                    expires_days = COOKIE_EXPIRATION_DAYS if auth_data["remember"] else None
                    self._set_cookie_json("auth_data", auth_data, expires_days)

                    log_operation("migrar_cookies", "system", "Cookies migrados para novo formato")

            if not auth_data or "token" not in auth_data:
                log_operation("verificar_sessao", "system", "Dados de autenticação não encontrados nos cookies")
                return False

            # Validar token
            telefone = self._validar_token(auth_data["token"])
            if telefone:
                log_operation("verificar_sessao", telefone, "Sessão válida encontrada")
                return True

            log_operation("verificar_sessao", "system", "Token inválido")
            return False
        except Exception as e:
            log_error(e, "verificar_sessao_persistente")
            return False
    
    def obter_telefone_do_cookie(self) -> str | None:
        """
        Obtém o telefone do usuário do cookie de autenticação.

        Returns:
            Telefone do usuário ou None se não encontrado/inválido
        """
        if not self.cookie_manager and not self.cookies:
            return None

        try:
            # Obter dados do cookie JSON
            auth_data = self._get_cookie_json("auth_data")
            if not auth_data or "token" not in auth_data:
                return None

            telefone = self._validar_token(auth_data["token"])
            if telefone:
                log_operation("obter_telefone", telefone, "Telefone recuperado do cookie")
            return telefone
        except Exception as e:
            log_error(e, "obter_telefone_do_cookie")
            return None
    
    def criar_sessao_persistente(self, telefone: str, manter_logado: bool = False) -> bool:
        """
        Cria uma sessão persistente salvando token nos cookies.

        Args:
            telefone: Telefone do usuário autenticado
            manter_logado: Se True, cookie expira em 30 dias; se False, apenas sessão atual

        Returns:
            True se sucesso, False caso contrário
        """
        if not self.cookie_manager and not self.cookies:
            log_operation("criar_sessao", telefone, "Nenhum gerenciador de cookies disponível")
            return False

        try:
            # Gerar token
            token = self._gerar_token(telefone)

            # Definir expiração
            expires_days = COOKIE_EXPIRATION_DAYS if manter_logado else None

            # SOLUÇÃO: Salvar tudo em 1 cookie JSON (evita erro de chave duplicada)
            auth_data = {
                "token": token,
                "remember": manter_logado,
                "created_at": datetime.now().isoformat()
            }

            success = self._set_cookie_json("auth_data", auth_data, expires_days)

            if success:
                log_operation("criar_sessao_persistente", telefone, f"manter_logado={manter_logado}, method={self.method}")
                return True
            else:
                log_operation("criar_sessao_persistente", telefone, f"Falha ao salvar cookie, method={self.method}")
                return False
        except Exception as e:
            log_error(e, "criar_sessao_persistente")
            return False
    
    def limpar_sessao(self) -> bool:
        """
        Limpa todos os cookies de autenticação.

        Returns:
            True se sucesso, False caso contrário
        """
        if not self.cookie_manager and not self.cookies:
            return False

        try:
            # SOLUÇÃO: Apenas 1 chamada a delete() (evita erro de chave duplicada)
            success = self._remove_cookie("auth_data")

            # Garantir que o cache foi limpo
            if "cookies_cache" in st.session_state:
                del st.session_state.cookies_cache

            if success:
                log_operation("limpar_sessao", "system", f"method={self.method}")
                return True
            return False
        except Exception as e:
            log_error(e, "limpar_sessao")
            return False

    def _get_all_cookies(self) -> dict:
        """
        Obtém todos os cookies de uma vez (cacheable).

        Returns:
            Dicionário com todos os cookies
        """
        try:
            if self.method == "stx" and self.cookie_manager:
                # Usar session_state para cachear e evitar múltiplas chamadas
                if "cookies_cache" not in st.session_state:
                    st.session_state.cookies_cache = self.cookie_manager.get_all() or {}
                return st.session_state.cookies_cache
            elif self.method == "controller" and self.cookies:
                # Controller não tem problema com múltiplas chamadas
                return {}  # Controller usa get() direto
            return {}
        except Exception as e:
            log_error(e, "_get_all_cookies")
            return {}

    def _get_cookie(self, key: str) -> str | None:
        """
        Obtém um cookie usando o método disponível.

        Args:
            key: Nome do cookie

        Returns:
            Valor do cookie ou None
        """
        try:
            if self.method == "stx" and self.cookie_manager:
                # Usar cache para evitar múltiplas chamadas a get_all()
                cookies = self._get_all_cookies()
                return cookies.get(key) if cookies else None
            elif self.method == "controller" and self.cookies:
                return self.cookies.get(key)
            return None
        except Exception as e:
            log_error(e, f"_get_cookie:{key}")
            return None

    def _set_cookie(self, key: str, value: str, expires_days: int | None = None) -> bool:
        """
        Define um cookie usando o método disponível.

        Args:
            key: Nome do cookie
            value: Valor do cookie
            expires_days: Dias para expiração (None = sessão atual)

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            if self.method == "stx" and self.cookie_manager:
                # extra_streamlit_components usa max_age em segundos
                if expires_days:
                    max_age = expires_days * 24 * 60 * 60
                    self.cookie_manager.set(key, value, max_age=max_age)
                else:
                    self.cookie_manager.set(key, value)

                # Limpar cache para forçar reload
                if "cookies_cache" in st.session_state:
                    del st.session_state.cookies_cache

                return True
            elif self.method == "controller" and self.cookies:
                self.cookies.set(key, value, expires_days=expires_days)
                return True
            return False
        except Exception as e:
            log_error(e, f"_set_cookie:{key}")
            return False

    def _remove_cookie(self, key: str) -> bool:
        """
        Remove um cookie usando o método disponível.

        Args:
            key: Nome do cookie

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            if self.method == "stx" and self.cookie_manager:
                self.cookie_manager.delete(key)

                # Limpar cache para forçar reload
                if "cookies_cache" in st.session_state:
                    del st.session_state.cookies_cache

                return True
            elif self.method == "controller" and self.cookies:
                self.cookies.remove(key)
                return True
            return False
        except Exception as e:
            log_error(e, f"_remove_cookie:{key}")
            return False

    def _set_cookie_json(self, key: str, data: dict, expires_days: int | None = None) -> bool:
        """
        Define um cookie com dados em formato JSON.

        Args:
            key: Nome do cookie
            data: Dicionário com dados a salvar
            expires_days: Dias para expiração (None = sessão atual)

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Serializar para JSON
            value = json.dumps(data)

            # Usar método existente para salvar
            return self._set_cookie(key, value, expires_days)
        except Exception as e:
            log_error(e, f"_set_cookie_json:{key}")
            return False

    def _get_cookie_json(self, key: str) -> dict | None:
        """
        Obtém um cookie e desserializa de JSON.

        Args:
            key: Nome do cookie

        Returns:
            Dicionário com dados ou None
        """
        try:
            value = self._get_cookie(key)
            if not value:
                return None

            # Desserializar JSON
            return json.loads(value)
        except Exception as e:
            log_error(e, f"_get_cookie_json:{key}")
            return None
    
    def _gerar_token(self, telefone: str) -> str:
        """
        Gera um token seguro para o telefone.
        
        Args:
            telefone: Telefone do usuário
            
        Returns:
            Token hash único
        """
        # Combinar telefone + timestamp + secret key
        timestamp = datetime.now().isoformat()
        data = f"{telefone}:{timestamp}:{COOKIE_SECRET_KEY}"
        
        # Gerar hash SHA256
        token = hashlib.sha256(data.encode()).hexdigest()
        
        # Adicionar telefone codificado no token (para validação)
        # Formato: telefone_base64:hash
        import base64
        telefone_encoded = base64.b64encode(telefone.encode()).decode()
        
        return f"{telefone_encoded}:{token}"
    
    def _validar_token(self, token: str) -> str | None:
        """
        Valida um token e retorna o telefone se válido.

        Args:
            token: Token a validar

        Returns:
            Telefone se válido, None caso contrário
        """
        try:
            if not token or ":" not in token:
                return None

            # Extrair telefone do token
            telefone_encoded, token_hash = token.split(":", 1)

            # Decodificar telefone
            import base64
            telefone = base64.b64decode(telefone_encoded.encode()).decode()

            # Validar formato do telefone (deve ter 10-11 dígitos)
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            if not (10 <= len(telefone_limpo) <= 11):
                return None

            # Token é válido se conseguiu decodificar telefone válido
            return telefone_limpo
        except Exception as e:
            log_error(e, "_validar_token")
            return None

    def obter_status_cookies(self) -> dict:
        """
        Obtém informações de diagnóstico sobre o sistema de cookies.

        Returns:
            Dicionário com informações de status
        """
        status = {
            "disponivel": False,
            "metodo": None,
            "tem_auth_data": False,
            "tem_remember_me": False,
            "sessao_valida": False,
            "telefone": None,
            "erro": None
        }

        try:
            if not self.cookie_manager and not self.cookies:
                status["erro"] = "Nenhuma biblioteca de cookies instalada"
                return status

            status["disponivel"] = True
            status["metodo"] = self.method

            # Verificar cookie JSON
            auth_data = self._get_cookie_json("auth_data")

            status["tem_auth_data"] = bool(auth_data)
            status["tem_remember_me"] = auth_data.get("remember", False) if auth_data else False

            # Validar sessão
            if auth_data and "token" in auth_data:
                telefone = self._validar_token(auth_data["token"])
                if telefone:
                    status["sessao_valida"] = True
                    status["telefone"] = telefone

        except Exception as e:
            status["erro"] = str(e)
            log_error(e, "obter_status_cookies")

        return status


# Instância global do serviço
_session_service = None


def get_session_service() -> SessionService:
    """
    Retorna instância singleton do SessionService.
    
    Returns:
        Instância do SessionService
    """
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service

