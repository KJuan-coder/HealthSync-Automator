# Configurações para pytest
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture
def mock_playwright():
    with sync_playwright() as p:
        yield p