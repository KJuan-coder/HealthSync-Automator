# Ponto de entrada da aplicação
import asyncio
from src.core.automation import WebsiteAutomation

async def main():
    automation = WebsiteAutomation()
    await automation.run()

if __name__ == "__main__":
    asyncio.run(main())