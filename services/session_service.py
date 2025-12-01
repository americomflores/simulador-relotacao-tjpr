"""
Serviço de gerenciamento de sessão e cookies para persistência de autenticação.
"""
import streamlit as st
import hashlib
import json
from datetime import datetime, timedelta
from streamlit_cookies_controller import CookieController
from utils.logger import log_operation, log_error
from config.settings import COOKIE_EXPIRATION_DAYS, COOKIE_SECRET_KEY


class SessionService:
    """Gerencia sessões persistentes usando cookies."""
    
    def __init__(self):
        """Inicializa o controlador de cookies."""
        try:
            self.cookies = CookieController()
        except Exception as e:
            log_error(e, "SessionService.__init__")
            self.cookies = None
    
    def verificar_sessao_persistente(self) -> bool:
        """
        Verifica se existe uma sessão persistente válida nos cookies.
        
        Returns:
            True se existe sessão válida, False caso contrário
        """
        if not self.cookies:
            return False
        
        try:
            auth_token = self.cookies.get("auth_token")
            if not auth_token:
                return False
            
            # Validar token
            telefone = self._validar_token(auth_token)
            if telefone:
                return True
            
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
        if not self.cookies:
            return None
        
        try:
            auth_token = self.cookies.get("auth_token")
            if not auth_token:
                return None
            
            telefone = self._validar_token(auth_token)
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
        if not self.cookies:
            return False
        
        try:
            # Gerar token
            token = self._gerar_token(telefone)
            
            # Definir expiração
            if manter_logado:
                # 30 dias
                expires_days = COOKIE_EXPIRATION_DAYS
            else:
                # Apenas sessão atual (expira quando navegador fecha)
                expires_days = None
            
            # Salvar cookie
            self.cookies.set("auth_token", token, expires_days=expires_days)
            self.cookies.set("remember_me", "true" if manter_logado else "false", expires_days=expires_days)
            
            log_operation("criar_sessao_persistente", telefone, f"manter_logado={manter_logado}")
            return True
        except Exception as e:
            log_error(e, "criar_sessao_persistente")
            return False
    
    def limpar_sessao(self) -> bool:
        """
        Limpa todos os cookies de autenticação.
        
        Returns:
            True se sucesso, False caso contrário
        """
        if not self.cookies:
            return False
        
        try:
            self.cookies.remove("auth_token")
            self.cookies.remove("remember_me")
            log_operation("limpar_sessao", "system")
            return True
        except Exception as e:
            log_error(e, "limpar_sessao")
            return False
    
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

