# HealthSync Automator

Bem-vindo ao **HealthSync Automator**, uma solução sofisticada em Python para automatizar processos de atendimento e agendamento em sistemas de saúde (como o e-SUS), integrada ao Telegram para notificações em tempo real. Este projeto utiliza o **Playwright** para interagir com interfaces web e o **Telegram** para enviar atualizações a um grupo privado, otimizando fluxos de trabalho em ambientes de saúde.

## Como o Projeto Funciona

O **HealthSync Automator** é estruturado em módulos que colaboram para realizar login, gerenciar atendimentos, agendar consultas e notificar o sucesso das operações.

### Estrutura do Projeto
- **`src/core/automation.py`**: Orquestra o fluxo principal, incluindo autenticação no site.
- **`src/core/atendimento.py`**: Adiciona cidadãos à lista de atendimento e preenche formulários SOAP.
- **`src/core/agendamento.py`**: Agenda consultas com base em horários disponíveis.
- **`src/core/telegram_bot.py`**: (Opcional) Monitora mensagens do chat privado e redireciona ao grupo.
- **`main.py`**: Ponto de entrada para iniciar a automação.
- **`src/config/settings.py`**: Carrega configurações do arquivo `.env`.
- **`src/utils/logger.py`**: Configura logs detalhados para rastreamento.

### Fluxo de Execução
1. **Autenticação**:
   - Acessa o site definido em `WEBSITE_URL`, aceita cookies e autentica com `USERNAME` e `PASSWORD`.
   - Verifica a unidade (`UNIDADE`) e o CBO "Enfermeiro da estratégia de saúde da família".

2. **Agendamento**:
   - Navega até "Agenda", busca o profissional (`ENFERMEIRO`), seleciona um horário disponível e agenda para o paciente (`PACIENTE`).
   - Prioriza o CBO "ENFERMEIRO DA ESTRATÉGIA DE SAÚDE DA FAMÍLIA", com fallback para "ENFERMEIRO".

3. **Atendimento**:
   - Adiciona o paciente à lista, preenchendo "Digite o nome completo do" ou "Cidadão*" (com fallback).
   - Preenche o formulário SOAP com o código A03 (Febre) e finaliza.

4. **Notificação**:
   - Envia uma mensagem ao grupo Telegram (`TELEGRAM_GROUP_CHAT_ID`) com unidade, URL e horário de conclusão.

### Características
- **Resiliência**: Lida com elementos dinâmicos usando `try/except` para fallbacks inteligentes.
- **Logs**: Registra todas as ações em `src/logs/app.log` para monitoramento e depuração.
- **Escalabilidade**: Suporta execução em múltiplas VPNs com configurações distintas.

---

## Configuração do Projeto

### Pré-requisitos
- **Python 3.8+**: Certifique-se de ter instalado.
- **Dependências**: Instale via `pip`:

- **Playwright**: Após instalar, execute:
# Configuração da Automação

## Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis ajustadas ao seu caso:

```ini
# URL do site a ser automatizado
WEBSITE_URL=https://seusite.digt.app.br/

# Credenciais de login
USERNAME=seu_usuario
PASSWORD=sua_senha

# Dados da automação
UNIDADE=Nome da Unidade de Saúde
ENFERMEIRO=Nome Completo do Enfermeiro
PACIENTE=Nome Completo do Paciente

# Configurações do Telegram
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
TELEGRAM_BOT_CHAT_ID=seu_id_do_chat_privado
TELEGRAM_GROUP_CHAT_ID=-id_do_grupo
```

## Como Executar

### 1. Configurar o Ambiente

Crie um ambiente virtual:
```sh
python -m venv venv
```

Ative o ambiente:
- **Windows:**
  ```sh
  venv\Scripts\activate
  ```
- **Linux/macOS:**
  ```sh
  source venv/bin/activate
  ```

Instale as dependências:
```sh
pip install -r requirements.txt
```

### 2. Executar a Automação

#### Com o Bot (Opcional)

**Terminal 1 (Bot):**
```sh
venv\Scripts\python.exe src\core\telegram_bot.py
```

**Terminal 2 (Automação):**
```sh
venv\Scripts\python.exe main.py
```

#### Sem o Bot
Apenas a automação envia diretamente ao grupo:
```sh
venv\Scripts\python.exe main.py
```

### 3. Agendamento (Opcional)
Use o **Windows Task Scheduler** para agendar a execução do `main.py` em horários específicos.

- **Programa:**
  ```sh
  C:\caminho\para\venv\Scripts\python.exe
  ```
- **Argumentos:**
  ```sh
  C:\caminho\para\main.py
  ```
- **Gatilho:**
  Exemplo: **Diariamente às 6:10** (ajuste conforme necessário).

  ### Personalização
- Substitua `[CeearaU]` pelo seu nome ou pseudônimo.