# Testes unitários para a automação
import pytest
from src.core.automation import WebsiteAutomation
from src.config.settings import settings

def test_login_success(mock_playwright):
    """Testa o fluxo de login com mocks."""
    automation = WebsiteAutomation()
    # Aqui você pode mockar o Playwright para simular o login
    # Por simplicidade, apenas verificamos se roda sem erro
    try:
        automation.login()
        assert True
    except Exception:
        assert False, "Login falhou inesperadamente"

def test_settings_validation():
    """Testa a validação das configurações."""
    original_url = settings.WEBSITE_URL
    settings.WEBSITE_URL = None  # Simula configuração faltando
    with pytest.raises(ValueError):
        settings.validate()
    settings.WEBSITE_URL = original_url  # Restaura para outros testes