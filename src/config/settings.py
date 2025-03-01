# src/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    WEBSITE_URL = os.getenv("WEBSITE_URL")
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    UNIDADE = os.getenv("UNIDADE")
    ENFERMEIRO = os.getenv("ENFERMEIRO")
    PACIENTE = os.getenv("PACIENTE")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Token do bot
    TELEGRAM_BOT_CHAT_ID = os.getenv("TELEGRAM_BOT_CHAT_ID")  # ID do chat privado com o bot
    TELEGRAM_GROUP_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID")  # ID do grupo

    def validate(self):
        required = [
            "WEBSITE_URL", "USERNAME", "PASSWORD", "UNIDADE", "ENFERMEIRO", "PACIENTE",
            "TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_CHAT_ID", "TELEGRAM_GROUP_CHAT_ID"
        ]
        for field in required:
            if not getattr(self, field):
                raise ValueError(f"Variável de ambiente {field} não está definida")

settings = Settings()
settings.validate()