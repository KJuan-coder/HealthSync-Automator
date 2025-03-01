# src/core/agendamento.py
import re
from src.utils.logger import logger
from datetime import datetime, timedelta
from src.config.settings import settings

class ScheduleAppointment:
    def __init__(self):
        self.unidade = settings.UNIDADE
        self.enfermeiro = settings.ENFERMEIRO
        self.paciente = settings.PACIENTE

    async def schedule_appointment(self, page):
        logger.info("Iniciando processo de agendamento")
        # await page.get_by_text(self.unidade).click()
        await page.get_by_role("navigation").filter(has_text="AcompanhamentosAgendaBusca").click()
        await page.get_by_role("link", name="Agenda").click()
        await page.get_by_role("textbox", name="Busque um profissional pelo").click()
        await page.get_by_role("textbox", name="Busque um profissional pelo").fill(self.enfermeiro.lower())
        # Aguarda as opções carregarem
        await page.wait_for_timeout(2000)  # Dá tempo para a lista de opções aparecer

        # Busca a opção pelo nome do enfermeiro e CBO
        logger.info(f"Procurando profissional: {self.enfermeiro} com CBO 'ENFERMEIRO DA ESTRATÉGIA DE SAÚDE DA FAMÍLIA'")
        options = page.get_by_role("option").filter(has_text=re.compile(self.enfermeiro, re.IGNORECASE))
        count = await options.count()
        logger.info(f"Opções encontradas para '{self.enfermeiro}': {count}")
        
        profissional_encontrado = False
        for i in range(count):
            option = options.nth(i)
            option_text = await option.inner_text()
            logger.info(f"Verificando opção {i}: {option_text}")
            
            # Tenta primeiro "ENFERMEIRO DA ESTRATÉGIA DE SAÚDE DA FAMÍLIA"
            cbo_element = option.locator("span").filter(has_text=re.compile("ENFERMEIRO DA ESTRATÉGIA DE SAÚDE DA FAMÍLIA", re.IGNORECASE))
            if await cbo_element.count() > 0:
                cbo_text = await cbo_element.first.inner_text()
                logger.info(f"Profissional {option_text} encontrado com CBO compatível: {cbo_text}")
                await option.click()
                profissional_encontrado = True
                break
            else:
                # Fallback para "ENFERMEIRO" se o primeiro não for encontrado
                logger.info(f"CBO 'ENFERMEIRO DA ESTRATÉGIA DE SAÚDE DA FAMÍLIA' não encontrado. Tentando 'ENFERMEIRO'")
                cbo_element = option.locator("span").filter(has_text=re.compile("ENFERMEIRO", re.IGNORECASE))
                if await cbo_element.count() > 0:
                    cbo_text = await cbo_element.first.inner_text()
                    logger.info(f"Profissional {option_text} encontrado com CBO compatível: {cbo_text}")
                    await option.click()
                    profissional_encontrado = True
                    break
                else:
                    logger.info(f"Opção {option_text} (índice {i}) não possui CBO 'ENFERMEIRO'")

        if not profissional_encontrado:
            todas_opcoes = page.get_by_role("option")
            todas_count = await todas_opcoes.count()
            logger.info(f"Total de opções na lista: {todas_count}")
            for i in range(todas_count):
                texto = await todas_opcoes.nth(i).inner_text()
                logger.info(f"Opção {i}: {texto}")
            logger.error(f"Nenhum profissional {self.enfermeiro} encontrado com CBO 'ENFERMEIRO DA ESTRATÉGIA DE SAÚDE DA FAMÍLIA' ou 'ENFERMEIRO'")
            raise Exception(f"Profissional {self.enfermeiro} não encontrado com CBO compatível")

        logger.info("Aguardando a grade de horários carregar")
        await page.wait_for_selector(".rbc-time-content", timeout=15000)
        await page.wait_for_timeout(2000)

        await page.locator(".rbc-time-content").first.click()

        logger.info("Verificando horários disponíveis")
        time_slots = page.locator(".rbc-timeslot-group")
        count = await time_slots.count()  # Usa await para obter o número de slots
        available_slot = None
        selected_time = None

        for i in range(count):
            slot_group = time_slots.nth(i)
            slot_time = await slot_group.locator(".rbc-label").inner_text() if await slot_group.locator(".rbc-label").count() > 0 else "sem horário"
            slot = slot_group.locator(".rbc-time-slot")
            slot_classes = await slot.get_attribute("class") or ""
            add_button = slot.locator(".rbc-time-slot-hover button", has_text="Adicionar agendamento")

            logger.info(f"Verificando slot {i}: classes={slot_classes}, horário={slot_time}, botão visível={await add_button.is_visible()}")

            if "rbc-time-slot-available" in slot_classes:
                await slot.hover()
                await page.wait_for_timeout(500)
                if await add_button.is_visible():
                    available_slot = add_button
                    selected_time = slot_time
                    logger.info(f"Horário disponível encontrado: {selected_time}")
                    await available_slot.click()
                    logger.info(f"Horário selecionado: {selected_time}")
                    break

        if not available_slot:
            logger.warning("Nenhum horário disponível encontrado")
            raise Exception("Nenhum horário disponível para agendamento")

        logger.info("Aguardando formulário de agendamento")
        await page.wait_for_selector("text=Cidadão*", timeout=15000, state="visible")
        await page.wait_for_timeout(1000)

        logger.info("Prosseguindo com o agendamento")
        logger.info(f"Selecionando cidadão: {self.paciente}")
        citizen_field = page.get_by_role("textbox", name="Cidadão*")
        await citizen_field.wait_for(timeout=5000, state="visible")
        await citizen_field.click()
        await citizen_field.fill(self.paciente.lower())
        await page.wait_for_timeout(2000)
        await citizen_field.press("ArrowDown")
        await citizen_field.press("Enter")
        logger.info(f"Paciente selecionado: {self.paciente}")

        logger.info("Marcando opção de imprimir comprovante")
        await page.locator("label").filter(has_text="Imprimir comprovante ao salvar").locator("span").first.click()

        logger.info("Finalizando agendamento")
        await page.get_by_role("button", name="Salvar").click()

        logger.info("Aguardando confirmação do agendamento")
        logger.info("Agendamento concluído com sucesso")

        await self.remover_agenda(page)

    async def remover_agenda(self, page):
        logger.info("Iniciando processo de remoção de agendamento")
        await page.get_by_role("navigation").filter(has_text="AcompanhamentosAgendaBusca").click()
        await page.get_by_role("link", name="Agenda").click()
        await page.get_by_role("textbox", name="Busque um profissional pelo").click()
        await page.get_by_role("textbox", name="Busque um profissional pelo").fill(self.enfermeiro.lower())
        await page.get_by_role("option", name=self.enfermeiro).click()
        await page.wait_for_selector(".rbc-time-content", timeout=15000)
        await page.wait_for_timeout(2000)

        logger.info(f"Procurando agendamento de {self.paciente}")
        appointment = page.locator("div").filter(has_text=re.compile(f"^{self.paciente}", re.IGNORECASE))
        if await appointment.count() > 0:  # Usa await para contar os elementos
            logger.info(f"Agendamento encontrado, total encontrado: {await appointment.count()}")
            logger.info(f"Texto do agendamento encontrado: {await appointment.nth(2).inner_text()}")
            await appointment.nth(2).click()

            options_button = appointment.locator("xpath=..").locator("button[aria-haspopup='true']").first
            await options_button.click()
            await page.get_by_role("menuitem", name="Cancelar").locator("div").click()
            await page.get_by_role("button", name="Excluir").click()
            logger.info("Agendamento removido com sucesso")
        else:
            logger.warning(f"Nenhum agendamento encontrado para {self.paciente}")
            raise Exception("Nenhum agendamento encontrado para remoção")

        logger.info("Aguardando confirmação da remoção")
        await page.wait_for_timeout(2000)
        logger.info("Remoção concluída")