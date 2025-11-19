# Commander Nodos Bot

Bot para servidores Hell Let Loose baseado no CRCON (hll_rcon_tool), que permite ao comandante solicitar construção de nodos e aos engenheiros confirmarem quando completarem a tarefa. Sistema com rastreamento de confirmações por tipo de nodo.

**Desenvolvido por:** Felipe Bandeira  
**GitHub:** https://github.com/felipebandeira23/commander_nodos

## 📋 Funcionalidade
- O comandante pode usar o comando `!nodos` no chat do jogo para solicitar construção de nodes aos engenheiros.
- Os engenheiros do mesmo time recebem uma mensagem privada solicitando a construção de todos os tipos de nodes.
- Engenheiros usam `!feito [tipo]` para confirmar que construíram um nodo específico (muni/fuel/manpower).
- O comandante recebe notificações em tempo real sobre o progresso das confirmações.
- Sistema rastreia 3 nodes de cada tipo (munição, combustível e mão-de-obra) por time.
- Quando todos os nodes são confirmados, o comandante e engenheiros são notificados da missão completa.

## 🔧 Requisitos
- Python 3.10+
- [hll_rcon_tool (CRCON)](https://github.com/MarechJ/hll_rcon_tool) versão 11.6.1 ou superior

## 🚀 Instalação

### 1. Baixar o arquivo do bot

```bash
cd /root/hll_rcon_tool/custom_tools
wget https://raw.githubusercontent.com/felipebandeira23/commander_nodos/main/custom_tools/commander_nodos.py
```

Se a pasta `custom_tools` não existir:
```bash
cd /root/hll_rcon_tool
mkdir -p custom_tools
cd custom_tools
wget https://raw.githubusercontent.com/felipebandeira23/commander_nodos/main/custom_tools/commander_nodos.py
```

### 2. Registrar os hooks no arquivo `hooks.py`

Edite o arquivo `/root/hll_rcon_tool/rcon/hooks.py`:

**No início do arquivo, adicione o import:**
```python
import custom_tools.commander_nodos as commander_nodos
```

**No final do arquivo, adicione o hook:**
```python
@on_chat
def commander_nodos_chat(rcon: Rcon, struct_log: StructuredLogLineWithMetaData):
    commander_nodos.commander_nodos_on_chat(rcon, struct_log)
```

### 3. Reiniciar o CRCON

```bash
cd /root/hll_rcon_tool
sudo bash restart.sh
```

Ou se o script tiver permissões de execução:
```bash
./restart.sh
```

> **Nota:** Certifique-se de que o script `restart.sh` tem permissões de execução (`chmod +x restart.sh`).

### 4. Configurar servidores ativos

Edite o arquivo `commander_nodos.py` e configure os servidores onde o bot estará ativo:

```python
ENABLE_ON_SERVERS: Final = ["1"]  # ["1", "2", "3"] para múltiplos servidores
```

## 📝 Como Usar

### Para Comandantes

#### Solicitar Nodes
```
!nodos
```

**O que acontece:**
- Todos os engenheiros do seu time recebem uma notificação
- Você recebe confirmação de quantos engenheiros foram notificados
- Sistema começa a rastrear confirmações

**Exemplo de mensagem que os engenheiros recebem:**
```
COMANDANTE SOLICITOU NODES!
Precisamos: Munição, Combustível, Mão-de-obra
Quando terminar, confirme: !feito [muni/fuel/manpower]
```

**Exemplo de confirmação para o comandante:**
```
Solicitação enviada para 3 engenheiro(s)!
Aguardando confirmações: [...] Munição: 0/3 | [...] Combustível: 0/3 | [...] Mão-de-obra: 0/3
```

#### Receber Atualizações

Sempre que um engenheiro confirmar um node, você receberá:
```
Node confirmado: Munição
Status: [...] Munição: 1/3 | [...] Combustível: 0/3 | [...] Mão-de-obra: 0/3
```

#### Confirmação Final

Quando todos os nodes forem confirmados:
```
TODOS OS NODES CONFIRMADOS!
Recursos completos disponíveis!
```

---

### Para Engenheiros

#### Quando Receber Solicitação

Você verá:
```
COMANDANTE SOLICITOU NODES!
Precisamos: Munição, Combustível, Mão-de-obra
Quando terminar, confirme: !feito [muni/fuel/manpower]
```

#### Confirmar Node Construído

Após construir um node, confirme com:

**Munição:**
```
!feito muni
```

**Combustível:**
```
!feito fuel
```

**Mão-de-obra:**
```
!feito manpower
```

**Exemplo de resposta:**
```
Confirmado: Munição
Status: [...] Munição: 1/3 | [...] Combustível: 0/3 | [...] Mão-de-obra: 0/3
```

#### Missão Completa

Quando todos os nodes forem confirmados, você receberá:
```
Missão completa! Todos os nodes construídos!
```

---

## ⚙️ Características Técnicas

### Sistema de Confirmação
- Rastreia confirmações individuais por engenheiro e tipo de nodo
- Requer 3 confirmações por tipo (pode ser de engenheiros diferentes)
- Previne duplicação de confirmações pelo mesmo engenheiro
- Status em tempo real com formato `[OK]` quando completo e `[...]` quando pendente

### Cooldown
- 60 segundos entre usos do comando `!nodos` pelo comandante
- Sem cooldown para confirmações `!feito` dos engenheiros

### Sistema de Times
- Solicitações são isoladas por time (Allies/Axis)
- Apenas engenheiros do mesmo time do comandante recebem notificações
- Cada time pode ter sua própria solicitação ativa simultaneamente

---

## 🎨 Personalização

### Arquivo: `commander_nodos.py`

```python
# -------- CONFIG --------
ENABLE_ON_SERVERS: Final = ["1"]  # IDs dos servidores onde ativar
CHAT_COMMAND_REQUEST: Final = "!nodos"  # Comando do comandante
CHAT_COMMAND_CONFIRM: Final = "!feito"  # Comando dos engenheiros
COOLDOWN_SECONDS: Final = 60  # Tempo entre usos do !nodos
LANGUAGE: Final = "pt"  # "pt" para Português, "en" para English
NODES_REQUIRED_PER_TYPE = 3  # Confirmações necessárias por tipo
# ------------------------
```

### Parâmetros Configuráveis

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `ENABLE_ON_SERVERS` | Lista de IDs de servidores onde o bot está ativo | `["1"]` |
| `CHAT_COMMAND_REQUEST` | Comando que o comandante usa | `"!nodos"` |
| `CHAT_COMMAND_CONFIRM` | Comando que engenheiros usam | `"!feito"` |
| `COOLDOWN_SECONDS` | Segundos entre usos de !nodos pelo mesmo comandante | `60` |
| `LANGUAGE` | Idioma das mensagens ("pt" ou "en") | `"pt"` |
| `NODES_REQUIRED_PER_TYPE` | Quantas confirmações necessárias por tipo de node | `3` |

---

## 🔍 Detalhes Técnicos

### Rastreamento de Estado

O bot mantém um dicionário em memória:
```python
_active_requests = {
    "Allies": {
        "commander_id": "76561198000000000",
        "timestamp": datetime.utcnow(),
        "engineers_notified": 3,
        "confirmations": {
            "muni": ["engineer_id_1"],
            "fuel": ["engineer_id_2", "engineer_id_3"],
            "manpower": []
        }
    }
}
```

### Fluxo de Execução

1. **Comandante digita `!nodos`**
   - Bot verifica cooldown
   - Valida que é comandante
   - Lista engenheiros no time
   - Cria solicitação ativa
   - Notifica todos os engenheiros

2. **Engenheiro digita `!feito muni`**
   - Bot verifica que é engenheiro
   - Valida tipo de node
   - Adiciona confirmação
   - Notifica engenheiro e comandante
   - Verifica se está completo

3. **Quando completo**
   - Notifica comandante
   - Notifica todos os engenheiros
   - Limpa solicitação ativa

### Validações

- ✅ Apenas comandante pode usar `!nodos`
- ✅ Apenas engenheiros podem usar `!feito`
- ✅ Cooldown de 60s entre solicitações
- ✅ Validação de tipos de node
- ✅ Proteção contra confirmações duplicadas
- ✅ Verificação de time (Allies/Axis)

---

## 🐛 Resolução de Problemas

### "Aguarde 60s entre usos"
- Espere o cooldown terminar antes de usar `!nodos` novamente
- Apenas o comandante que fez a primeira solicitação precisa esperar

### "Apenas o comandante pode usar !nodos"
- Certifique-se de estar no papel de Commander
- O bot verifica via `get_detailed_players()` e `get_player_info()`

### "Nenhum engenheiro encontrado"
- Confirme que há jogadores com role "Engineer" no seu time
- Peça para alguém trocar de classe para engenheiro

### "Nenhuma solicitação ativa"
- O comandante precisa usar `!nodos` primeiro
- Solicitações são limpas após completar todos os nodes

### "Tipo inválido"
- Use apenas: `muni`, `fuel` ou `manpower`
- Exemplo correto: `!feito muni`

### Bot não responde
- Verifique se o servidor está na lista `ENABLE_ON_SERVERS`
- Confirme que o import está correto no `hooks.py`
- Verifique os logs do CRCON: `docker compose logs -f backend`

---

## 🌍 Suporte a Múltiplos Idiomas

O bot suporta Português e Inglês. Para mudar o idioma:

```python
LANGUAGE: Final = "en"  # "pt" para Português, "en" para English
```

### Mensagens em Inglês:
- Comando do comandante: `!nodos`
- Confirmação: `!feito muni` / `!feito fuel` / `!feito manpower`
- Todas as mensagens são automaticamente traduzidas

---

## 📊 Exemplo de Sessão Completa

```
[Commander] !nodos
[Bot → Commander] Solicitação enviada para 3 engenheiro(s)!
                  Aguardando confirmações: [...] Munição: 0/3 | [...] Combustível: 0/3 | [...] Mão-de-obra: 0/3

[Bot → Eng1] COMANDANTE SOLICITOU NODES!
             Precisamos: Munição, Combustível, Mão-de-obra
             Quando terminar, confirme: !feito [muni/fuel/manpower]

[Engineer1] !feito muni
[Bot → Eng1] Confirmado: Munição
             Status: [...] Munição: 1/3 | [...] Combustível: 0/3 | [...] Mão-de-obra: 0/3
[Bot → Commander] Node confirmado: Munição
                  Status: [...] Munição: 1/3 | [...] Combustível: 0/3 | [...] Mão-de-obra: 0/3

[Engineer2] !feito muni
[Bot → Eng2] Confirmado: Munição
             Status: [...] Munição: 2/3 | [...] Combustível: 0/3 | [...] Mão-de-obra: 0/3

[Engineer3] !feito muni
[Bot → Eng3] Confirmado: Munição
             Status: [OK] Munição: 3/3 | [...] Combustível: 0/3 | [...] Mão-de-obra: 0/3

... (engenheiros continuam confirmando fuel e manpower) ...

[Engineer3] !feito manpower
[Bot → Commander] TODOS OS NODES CONFIRMADOS!
                  Recursos completos disponíveis!
[Bot → All Engineers] Missão completa! Todos os nodes construídos!
```

---

## 📝 Notas Importantes

### Por que sistema de confirmação manual?
O Hell Let Loose **não gera logs de construção de estruturas**. Os logs disponíveis são apenas:
- KILL / TEAM KILL
- CHAT (Team/Unit)
- CONNECTED / DISCONNECTED
- MATCH START / MATCH END

**Não existe** log tipo "STRUCTURE BUILT" ou similar no HLL, por isso a solução de confirmação manual é a mais confiável.

---

## 📞 Autor e Suporte

**Desenvolvido por:** Felipe Bandeira  
**GitHub:** https://github.com/felipebandeira23/commander_nodos

**Problemas ou sugestões?**
- Abra uma issue no GitHub
- Contribuições são bem-vindas!

---

## 📄 Licença

Este projeto é open source e está disponível sob os termos da licença MIT.

---

# 🇬🇧 English Version

# Commander Nodos Bot

Bot for Hell Let Loose servers based on CRCON (hll_rcon_tool), which allows the commander to request node construction and engineers to confirm when they complete the task. System with confirmation tracking by node type.

**Developed by:** Felipe Bandeira  
**GitHub:** https://github.com/felipebandeira23/commander_nodos

## 📋 Features
- Commander can use the `!nodos` command in game chat to request node construction from engineers.
- Engineers on the same team receive a private message requesting construction of all node types.
- Engineers use `!feito [type]` to confirm they built a specific node (muni/fuel/manpower).
- Commander receives real-time notifications about confirmation progress.
- System tracks 3 nodes of each type (munitions, fuel, and manpower) per team.
- When all nodes are confirmed, commander and engineers are notified of mission completion.

## 🔧 Requirements
- Python 3.10+
- [hll_rcon_tool (CRCON)](https://github.com/MarechJ/hll_rcon_tool) version 11.6.1 or higher

## 🚀 Installation

### 1. Download the bot file

```bash
cd /root/hll_rcon_tool/custom_tools
wget https://raw.githubusercontent.com/felipebandeira23/commander_nodos/main/custom_tools/commander_nodos.py
```

If the `custom_tools` folder doesn't exist:
```bash
cd /root/hll_rcon_tool
mkdir -p custom_tools
cd custom_tools
wget https://raw.githubusercontent.com/felipebandeira23/commander_nodos/main/custom_tools/commander_nodos.py
```

### 2. Register hooks in the `hooks.py` file

Edit the file `/root/hll_rcon_tool/rcon/hooks.py`:

**At the beginning of the file, add the import:**
```python
import custom_tools.commander_nodos as commander_nodos
```

**At the end of the file, add the hook:**
```python
@on_chat
def commander_nodos_chat(rcon: Rcon, struct_log: StructuredLogLineWithMetaData):
    commander_nodos.commander_nodos_on_chat(rcon, struct_log)
```

### 3. Restart CRCON

```bash
cd /root/hll_rcon_tool
sudo bash restart.sh
```

Or if the script has execution permissions:
```bash
./restart.sh
```

> **Note:** Make sure the `restart.sh` script has execution permissions (`chmod +x restart.sh`).

### 4. Configure active servers

Edit the `commander_nodos.py` file and configure which servers the bot will be active on:

```python
ENABLE_ON_SERVERS: Final = ["1"]  # ["1", "2", "3"] for multiple servers
```

## 📝 How to Use

### For Commanders

#### Request Nodes
```
!nodos
```

**What happens:**
- All engineers on your team receive a notification
- You receive confirmation of how many engineers were notified
- System starts tracking confirmations

**Example message engineers receive:**
```
COMMANDER REQUESTED NODES!
We need: Munition, Fuel, Manpower
When finished, confirm: !feito [muni/fuel/manpower]
```

**Example confirmation for commander:**
```
Request sent to 3 engineer(s)!
Awaiting confirmations: [...] Munition: 0/3 | [...] Fuel: 0/3 | [...] Manpower: 0/3
```

#### Receive Updates

Whenever an engineer confirms a node, you will receive:
```
Node confirmed: Munition
Status: [...] Munition: 1/3 | [...] Fuel: 0/3 | [...] Manpower: 0/3
```

#### Final Confirmation

When all nodes are confirmed:
```
ALL NODES CONFIRMED!
Full resources available!
```

---

### For Engineers

#### When Receiving Request

You will see:
```
COMMANDER REQUESTED NODES!
We need: Munition, Fuel, Manpower
When finished, confirm: !feito [muni/fuel/manpower]
```

#### Confirm Node Built

After building a node, confirm with:

**Munition:**
```
!feito muni
```

**Fuel:**
```
!feito fuel
```

**Manpower:**
```
!feito manpower
```

**Example response:**
```
Confirmed: Munition
Status: [...] Munition: 1/3 | [...] Fuel: 0/3 | [...] Manpower: 0/3
```

#### Mission Complete

When all nodes are confirmed, you will receive:
```
Mission complete! All nodes built!
```

---

## ⚙️ Technical Features

### Confirmation System
- Tracks individual confirmations by engineer and node type
- Requires 3 confirmations per type (can be from different engineers)
- Prevents duplicate confirmations by the same engineer
- Real-time status with `[OK]` format when complete and `[...]` when pending

### Cooldown
- 60 seconds between uses of `!nodos` command by commander
- No cooldown for `!feito` confirmations by engineers

### Team System
- Requests are isolated by team (Allies/Axis)
- Only engineers on the same team as commander receive notifications
- Each team can have its own active request simultaneously

---

## 🎨 Customization

### File: `commander_nodos.py`

```python
# -------- CONFIG --------
ENABLE_ON_SERVERS: Final = ["1"]  # Server IDs where bot is active
CHAT_COMMAND_REQUEST: Final = "!nodos"  # Commander command
CHAT_COMMAND_CONFIRM: Final = "!feito"  # Engineer command
COOLDOWN_SECONDS: Final = 60  # Time between !nodos uses
LANGUAGE: Final = "en"  # "pt" for Portuguese, "en" for English
NODES_REQUIRED_PER_TYPE = 3  # Confirmations required per type
# ------------------------
```

### Configurable Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ENABLE_ON_SERVERS` | List of server IDs where bot is active | `["1"]` |
| `CHAT_COMMAND_REQUEST` | Command that commander uses | `"!nodos"` |
| `CHAT_COMMAND_CONFIRM` | Command that engineers use | `"!feito"` |
| `COOLDOWN_SECONDS` | Seconds between !nodos uses by same commander | `60` |
| `LANGUAGE` | Message language ("pt" or "en") | `"en"` |
| `NODES_REQUIRED_PER_TYPE` | How many confirmations needed per node type | `3` |

---

## 🔍 Technical Details

### State Tracking

The bot maintains a dictionary in memory:
```python
_active_requests = {
    "Allies": {
        "commander_id": "76561198000000000",
        "timestamp": datetime.utcnow(),
        "engineers_notified": 3,
        "confirmations": {
            "muni": ["engineer_id_1"],
            "fuel": ["engineer_id_2", "engineer_id_3"],
            "manpower": []
        }
    }
}
```

### Execution Flow

1. **Commander types `!nodos`**
   - Bot checks cooldown
   - Validates is commander
   - Lists engineers on team
   - Creates active request
   - Notifies all engineers

2. **Engineer types `!feito muni`**
   - Bot verifies is engineer
   - Validates node type
   - Adds confirmation
   - Notifies engineer and commander
   - Checks if complete

3. **When complete**
   - Notifies commander
   - Notifies all engineers
   - Clears active request

### Validations

- ✅ Only commander can use `!nodos`
- ✅ Only engineers can use `!feito`
- ✅ 60s cooldown between requests
- ✅ Node type validation
- ✅ Protection against duplicate confirmations
- ✅ Team verification (Allies/Axis)

---

## 🐛 Troubleshooting

### "Wait 60s between uses"
- Wait for cooldown to finish before using `!nodos` again
- Only the commander who made the first request needs to wait

### "Only commander can use !nodos"
- Make sure you are in the Commander role
- Bot checks via `get_detailed_players()` and `get_player_info()`

### "No engineers found"
- Confirm there are players with "Engineer" role on your team
- Ask someone to switch class to engineer

### "No active request"
- Commander needs to use `!nodos` first
- Requests are cleared after completing all nodes

### "Invalid type"
- Use only: `muni`, `fuel` or `manpower`
- Correct example: `!feito muni`

### Bot doesn't respond
- Check if server is in `ENABLE_ON_SERVERS` list
- Confirm import is correct in `hooks.py`
- Check CRCON logs: `docker compose logs -f backend`

---

## 🌍 Multi-language Support

The bot supports Portuguese and English. To change language:

```python
LANGUAGE: Final = "en"  # "pt" for Portuguese, "en" for English
```

### Messages in English:
- Commander command: `!nodos`
- Confirmation: `!feito muni` / `!feito fuel` / `!feito manpower`
- All messages are automatically translated

---

## 📊 Complete Session Example

```
[Commander] !nodos
[Bot → Commander] Request sent to 3 engineer(s)!
                  Awaiting confirmations: [...] Munition: 0/3 | [...] Fuel: 0/3 | [...] Manpower: 0/3

[Bot → Eng1] COMMANDER REQUESTED NODES!
             We need: Munition, Fuel, Manpower
             When finished, confirm: !feito [muni/fuel/manpower]

[Engineer1] !feito muni
[Bot → Eng1] Confirmed: Munition
             Status: [...] Munition: 1/3 | [...] Fuel: 0/3 | [...] Manpower: 0/3
[Bot → Commander] Node confirmed: Munition
                  Status: [...] Munition: 1/3 | [...] Fuel: 0/3 | [...] Manpower: 0/3

[Engineer2] !feito muni
[Bot → Eng2] Confirmed: Munition
             Status: [...] Munition: 2/3 | [...] Fuel: 0/3 | [...] Manpower: 0/3

[Engineer3] !feito muni
[Bot → Eng3] Confirmed: Munition
             Status: [OK] Munition: 3/3 | [...] Fuel: 0/3 | [...] Manpower: 0/3

... (engineers continue confirming fuel and manpower) ...

[Engineer3] !feito manpower
[Bot → Commander] ALL NODES CONFIRMED!
                  Full resources available!
[Bot → All Engineers] Mission complete! All nodes built!
```

---

## 📝 Important Notes

### Why manual confirmation system?
Hell Let Loose **does not generate structure construction logs**. The available logs are only:
- KILL / TEAM KILL
- CHAT (Team/Unit)
- CONNECTED / DISCONNECTED
- MATCH START / MATCH END

There is **no "STRUCTURE BUILT"** log or similar in HLL, so the manual confirmation solution is the most reliable.

---

## 📞 Author and Support

**Developed by:** Felipe Bandeira  
**GitHub:** https://github.com/felipebandeira23/commander_nodos

**Problems or suggestions?**
- Open an issue on GitHub
- Contributions are welcome!

---

## 📄 License

This project is open source and available under the terms of the MIT License.
