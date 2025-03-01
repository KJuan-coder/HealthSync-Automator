# src/core/automation.py
import re
from playwright.async_api import async_playwright, TimeoutError
from src.config.settings import settings
from src.utils.logger import logger
from src.core.agendamento import ScheduleAppointment
from src.core.atendimento import AttendanceList

class WebsiteAutomation:
    def __init__(self):
        """Inicializa a automação com as configurações do .env."""
        settings.validate()
        self.url = settings.WEBSITE_URL
        self.username = settings.USERNAME
        self.password = settings.PASSWORD
        self.unidade = settings.UNIDADE
        logger.info(f"Usuário carregado: {self.username}")
        logger.info(f"Senha carregada: {self.password}")

    async def login(self, page):
        """Realiza o login no site e retorna a página logada."""
        logger.info(f"Acessando o site: {self.url}")
        await page.goto(self.url)

        logger.info("Aceitando cookies")
        await page.get_by_role("button", name="Aceitar todos").click()
        await page.wait_for_selector('//*[@id="root"]/div/div[3]/div[1]/div/div[2]/div/form/div/div[1]/div/div[1]/div/div/input', timeout=10000)

        logger.info("Preenchendo o campo de usuário")
        await page.locator('//*[@id="root"]/div/div[3]/div[1]/div/div[2]/div/form/div/div[1]/div/div[1]/div/div/input').fill(self.username)

        logger.info("Preenchendo o campo de senha")
        await page.locator('//*[@id="root"]/div/div[3]/div[1]/div/div[2]/div/form/div/div[2]/div/div/div/div[1]/div/div/input').fill(self.password)

        logger.info("Clicando no botão de login")
        await page.click("button[type='submit']")

        logger.info("Verificando diálogo de sessão existente")
        try:
            await page.wait_for_timeout(2000)
            iframes = page.locator("iframe")
            count = await iframes.count()  # Usa await para obter o número de iframes
            for i in range(count):
                frame = iframes.nth(i)
                logger.info(f"Verificando iframe {i}: {await frame.get_attribute('src')}")
                continue_button = frame.locator("xpath=//button[contains(., 'Continuar')]")
                if await continue_button.is_visible(timeout=3000):
                    await continue_button.click()
                    logger.info("Clicado em 'Continuar' dentro do iframe")
                    break
            else:
                continue_button = page.locator("xpath=//button[contains(., 'Continuar')]")
                if await continue_button.is_visible(timeout=3000):
                    await continue_button.click()
                    logger.info("Clicado em 'Continuar' na página principal sem iframe")
                else:
                    logger.info("Nenhum botão 'Continuar' encontrado")
        except TimeoutError:
            logger.info("Nenhum diálogo de sessão detectado, prosseguindo normalmente")

        logger.info("Aguardando página principal após login")
        # await page.pause()
        # await page.wait_for_selector("text=Centro de Referencia Municipal de Saude", timeout=10000)
        # Verifica a unidade específica do .env e o CBO
        await page.wait_for_timeout(2000)  # Aguarda extra para garantir carregamento completo

        # Verifica a unidade específica do .env e o CBO
        logger.info(f"Procurando unidade: {self.unidade} com CBO 'Enfermeiro da estratégia de saúde da família'")
        unidades = page.locator("h3").filter(has_text=re.compile(self.unidade, re.IGNORECASE))
        count = await unidades.count()
        logger.info(f"Unidades encontradas com texto '{self.unidade}': {count}")

        unidade_encontrada = False
        for i in range(count):
            unidade = unidades.nth(i)
            unidade_text = await unidade.inner_text()
            logger.info(f"Verificando unidade {i}: {unidade_text}")
            # Busca o CBO apenas no div irmão direto
            cbo_element = unidade.locator("xpath=ancestor::div/following-sibling::div[1]//span[contains(., 'Enfermeiro da estratégia de saúde da família')]")
            cbo_count = await cbo_element.count()
            logger.info(f"CBOs encontrados para unidade {unidade_text}: {cbo_count}")
            if cbo_count > 0:
                cbo_text = await cbo_element.first.inner_text()  # Usa .first para evitar modo estrito
                logger.info(f"Unidade {unidade_text} encontrada com CBO compatível: {cbo_text}")
                await unidade.click()  # Clica na unidade correta
                unidade_encontrada = True
                break
            else:
                logger.info(f"Unidade {unidade_text} (índice {i}) não possui CBO 'Enfermeiro da estratégia de saúde da família'")

        if not unidade_encontrada:
            # Loga todas as unidades <h3> e seus CBOs para depuração
            todas_unidades = page.locator("h3")
            todas_count = await todas_unidades.count()
            logger.info(f"Total de unidades <h3> na página: {todas_count}")
            for i in range(todas_count):
                unidade = todas_unidades.nth(i)
                unidade_text = await unidade.inner_text()
                cbo_element = unidade.locator("xpath=ancestor::div/following-sibling::div[1]//span[contains(., 'Enfermeiro')]")
                cbo_text = await cbo_element.first.inner_text() if await cbo_element.count() > 0 else "Nenhum CBO encontrado"
                logger.info(f"Unidade {i}: {unidade_text} | CBO: {cbo_text}")
            logger.error(f"Nenhuma unidade {self.unidade} encontrada com CBO 'Enfermeiro da estratégia de saúde da família'")
            raise Exception(f"Unidade {self.unidade} não encontrada com CBO compatível")

        logger.info(f"Login bem-sucedido para o usuário: {self.username}")

    async def run(self):
        """Ponto de entrada para executar a automação."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()

                logger.info("Iniciando a automação do site Agendamento")
                await self.login(page)  # Agora assíncrono
                scheduler = ScheduleAppointment()
                await scheduler.schedule_appointment(page)
                
                logger.info("Chamando a função de lista de atendimento")
                attendance = AttendanceList()
                await attendance.lista_atendimento(page)
                logger.info("Automação de lista de atendimento concluída")

                logger.info(f"Automação concluída com sucesso: {self.unidade} / {self.url}")
                await page.wait_for_timeout(5000)
                await browser.close()
        except TimeoutError:
            logger.error("Tempo de espera excedido. Verifique os seletores ou a conexão.")
            raise
        except Exception as e:
            logger.error(f"Erro durante a automação: {str(e)}")
            raise

    def extract_data(self):
        """Exemplo de função para extrair dados após o login."""
        try:
            with async_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(self.url)
                page.fill("input[id='username']", self.username)
                page.fill("input[id='password']", self.password)
                page.click("button[type='submit']")
                page.wait_for_selector("text=Welcome", timeout=10000)

                logger.info("Extraindo dados da página")
                data = page.inner_text("h1")
                logger.info(f"Dado extraído: {data}")

                browser.close()
                return data
        except Exception as e:
            logger.error(f"Erro ao extrair dados: {str(e)}")
            raise