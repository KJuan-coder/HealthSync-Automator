# Configuração do sistema de logs
#src/utils/logger.py
import logging
import os

def setup_logger():
    logger = logging.getLogger("AutomationLogger")
    logger.setLevel(logging.INFO)

    # Evita duplicação de handlers
    if not logger.handlers:
        # Handler para arquivo
        log_dir = "src/logs"
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(f"{log_dir}/app.log")
        file_handler.setLevel(logging.INFO)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formato do log
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Adiciona os handlers ao logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()