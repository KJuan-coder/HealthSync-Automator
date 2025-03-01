# src/core/atendimento.py
from datetime import datetime
import re
import asyncio
from aiogram import Bot
from src.utils.logger import logger
from src.config.settings import settings

class AttendanceList:
    def __init__(self):
        """Inicializa com variáveis do .env."""
        self.url = settings.WEBSITE_URL
        self.unidade = settings.UNIDADE
        self.enfermeiro = settings.ENFERMEIRO
        self.paciente = settings.PACIENTE
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.chat_id = settings.TELEGRAM_BOT_CHAT_ID
        self.group_chat_id = settings.TELEGRAM_GROUP_CHAT_ID

    async def SOAP_A03(self, page):
        """Preenche o formulário SOAP com o código A03 (Febre)."""
        logger.info("Iniciando preenchimento do formulário SOAP com código A03")
        await page.get_by_role("tab", name="SOAP").click()
        await page.get_by_role("textbox", name="Motivo da consulta (CIAP 2)").click()
        await page.get_by_role("textbox", name="Motivo da consulta (CIAP 2)").fill("a03")
        await page.get_by_role("option", name="FEBRE Código A03 Inclui:").click()
        await page.get_by_test_id("ProblemasCondicoesForm.ciap").click()
        await page.wait_for_timeout(2000)
        await page.get_by_test_id("ProblemasCondicoesForm.ciap").fill("a03")
        await page.get_by_role("option", name="FEBRE Código A03 Inclui:").click()
        await page.wait_for_timeout(2000)
        try:
            element = page.get_by_test_id("ProblemasCondicoesFormFooterButtons.adicionar")
            await element.wait_for(state="visible")
            logger.info("Elemento encontrado e visível")
            await element.click()
            logger.info("Botão 'Adicionar' clicado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao clicar no botão 'Adicionar': {str(e)}")
            await page.pause()
        await page.wait_for_timeout(2000)
        await page.locator("label").filter(has_text="Alta do episódio").locator("span").first.click()
        try:
            element = page.get_by_test_id("AtendimentoIndividualFooter.finalizar")
            await element.wait_for(state="visible")
            logger.info("Elemento encontrado e visível Finalizar")
            await element.click()
            logger.info("Botão 'Finalizar' clicado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao clicar no botão 'Finalizar': {str(e)}")
            await page.pause()
        logger.info("Formulário SOAP A03 preenchido e finalizado com sucesso")

    async def notify_telegram_bot(self):
        """Envia uma mensagem diretamente ao grupo do Telegram."""
        try:
            # Monta a mensagem com unidade, URL e horário
            horario = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            notificacao = f"Notificação recebida: Automação concluída com sucesso em {self.unidade} e {self.url} às {horario}"
            logger.info(f"Tentando enviar mensagem ao grupo {self.group_chat_id}")
            await self.bot.send_message(chat_id=self.group_chat_id, text=notificacao)
            logger.info(f"Mensagem enviada ao grupo do Telegram: {notificacao}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem ao grupo do Telegram {self.group_chat_id}: {str(e)}")
        finally:
            await self.bot.session.close()
            logger.info("Sessão do bot encerrada com sucesso")

    async def lista_atendimento(self, page):
        """Acessa a lista de atendimento."""
        logger.info("Iniciando processo de acesso à lista de atendimento")

        await page.get_by_role("navigation").filter(has_text="AcompanhamentosAgendaBusca").click()
        await page.get_by_role("link", name="Lista de atendimentos").click()
        await page.mouse.move(0, 0)
        logger.info("Lista de atendimento carregada com sucesso 1")

        await page.get_by_test_id("adicionarCidadaoAtendimento").click()
        # Começa clicando no label "Nome" antes de tentar o campo "Digite o nome completo do"
        # Verifica se o label "Nome" está disponível antes de clicar
        try:
            nome_label = page.locator("label").filter(has_text="Nome").locator("span").first
            await nome_label.wait_for(timeout=5000, state="visible")  # Aguarda 5 segundos
            await nome_label.click()
            logger.info("Clicado no label 'Nome' para exibir o campo do cidadão")
        except Exception as e:
            logger.info(f"Label 'Nome' não encontrado ou não visível: {str(e)}. Prosseguindo sem clicar")

        # Tenta o campo "Digite o nome completo do" primeiro, fallback para "Cidadão*"
        try:
            cidadao_field = page.get_by_role("textbox", name="Digite o nome completo do")
            await cidadao_field.wait_for(timeout=15000, state="visible")
            logger.info("Campo 'Digite o nome completo do' encontrado")
        except Exception as e:
            logger.info(f"Campo 'Digite o nome completo do' não encontrado após clique em 'Nome': {str(e)}. Tentando 'Cidadão*' sem clique adicional")
            cidadao_field = page.get_by_role("textbox", name="Cidadão*")
            await cidadao_field.wait_for(timeout=15000, state="visible")
            logger.info("Campo 'Cidadão*' encontrado")

        await cidadao_field.fill(self.paciente.lower())
        await page.wait_for_timeout(2000)
        await page.get_by_role("option", name=self.paciente).click()

        logger.info(f"Paciente {self.paciente} selecionado")

        profissional_field = page.get_by_role("textbox", name="Profissional")
        await profissional_field.wait_for(timeout=15000, state="visible")
        await profissional_field.fill(self.enfermeiro.lower())
        await page.wait_for_timeout(2000)

        options = page.get_by_role("option").filter(has_text=re.compile(self.enfermeiro, re.IGNORECASE))
        logger.info(f"Opções encontradas para {self.enfermeiro}: {await options.count()}")
        await page.wait_for_timeout(2000)
        if await options.count() > 0:  # Usa await para contar as opções
            count = await options.count()
            for i in range(min(count, 3)):
                logger.info(f"Opção {i}: {await options.nth(i).inner_text()}")
            selected_option = options.first
            logger.info(f"Selecionando opção: {await selected_option.inner_text()}")
            await selected_option.click()
            logger.info(f"Profissional {self.enfermeiro} selecionado")
        else:
            logger.error(f"Nenhuma opção encontrada para {self.enfermeiro}")
            raise Exception(f"Nenhuma opção encontrada para {self.enfermeiro}")

        logger.info(f"Verificando atendimentos para {self.paciente}")
        await page.locator("label").filter(has_text="DEMANDA ESPONTÂNEA").locator("span").first.click()
        await page.get_by_test_id("adicionarAtendimento").click()
        await page.wait_for_timeout(2000)

        # await page.get_by_role("navigation").filter(has_text="AcompanhamentosAgendaBusca").click()
        logger.info("Lista de atendimento carregada com sucesso")
        await page.mouse.move(0, 0)

        logger.info("Verificando a lista de atendimentos para encontrar o paciente")
        paciente_span = page.get_by_text(re.compile(self.paciente, re.IGNORECASE))
        if await paciente_span.count() > 0:  # Usa await para contar os elementos
            logger.info(f"Paciente encontrado: {await paciente_span.inner_text()}")
            atender_button = page.locator("button[title='Atender']").first
            logger.info(f"Botões 'Atender' com title encontrados: {await page.locator('button[title=\"Atender\"]').count()}")
            if not await atender_button.is_visible():
                logger.info("Botão 'Atender' com title não encontrado ou não visível, tentando abordagem alternativa")
                buttons_no_text = page.get_by_role("button").filter(has_text=re.compile(r"^$", re.IGNORECASE))
                logger.info(f"Botões sem texto encontrados: {await buttons_no_text.count()}")
                count = await buttons_no_text.count()
                for i in range(min(count, 5)):
                    logger.info(f"Botão {i} sem texto: {await buttons_no_text.nth(i).get_attribute('title') or 'Sem title'}")
                atender_button = buttons_no_text.first

            if await atender_button.is_visible():
                await atender_button.scroll_into_view_if_needed()
                await atender_button.wait_for(timeout=5000, state="visible")
                await atender_button.click()
                logger.info(f"Botão 'Atender' clicado para {self.paciente}")
            else:
                logger.warning(f"Botão 'Atender' não visível para {self.paciente}")
                context_texts = paciente_span.locator("xpath=ancestor::div").locator(":scope *").filter(has_text=re.compile(".*", re.IGNORECASE))
                logger.info(f"Textos no contexto do paciente: {await context_texts.count()}")
                count = await context_texts.count()
                for i in range(min(count, 5)):
                    logger.info(f"Texto {i} no contexto: {await context_texts.nth(i).inner_text()}")
                raise Exception(f"Botão 'Atender' não encontrado ou não visível para {self.paciente}")
        else:
            all_texts = page.locator(":scope *").filter(has_text=re.compile(".*", re.IGNORECASE))
            logger.info(f"Paciente {self.paciente} não encontrado. Textos disponíveis na página: {await all_texts.count()}")
            count = await all_texts.count()
            for i in range(min(count, 10)):
                logger.info(f"Texto {i}: {await all_texts.nth(i).inner_text()}")
            raise Exception(f"Paciente {self.paciente} não encontrado na lista de atendimentos")

        logger.info("Processo de lista de atendimento concluído")
        await self.SOAP_A03(page)
        logger.info("SOAP A03 concluído após atendimento")
        await self.notify_telegram_bot()