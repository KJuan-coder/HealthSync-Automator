# src/core/telegram_bot.py
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.utils.logger import logger
from src.config.settings import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Use o ID correto do grupo conforme o log
GROUP_CHAT_ID = "-1002296151588"  # Atualizado com base no log

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.reply("Bot iniciado! Pronto para receber notificações.")
    logger.info("Comando /start recebido")

@dp.message()
async def handle_message(message: types.Message):
    logger.info(f"Mensagem recebida no chat {message.chat.id}: {message.text}")
    if not message.text.startswith('/'):
        unidade = message.text
        horario = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        logger.info(f"Automação concluída com sucesso: {unidade}")
        notificacao = f"Notificação recebida: Automação concluída com sucesso em {unidade} às {horario}"
        try:
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=notificacao)
            logger.info(f"Notificação enviada ao grupo {GROUP_CHAT_ID}: {notificacao}")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação ao grupo {GROUP_CHAT_ID}: {str(e)}")

async def start_bot():
    logger.info("Iniciando o bot do Telegram")
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Erro no polling do bot: {str(e)}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(start_bot())