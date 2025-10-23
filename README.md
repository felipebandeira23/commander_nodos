# Commander Nodos Bot

Bot para servidores Hell Let Loose baseado no CRCON (hll_rcon_tool), que permite ao comandante solicitar construção de nodos somente quando necessário. Ele identifica via logs se há nodos faltando e notifica os engenheiros do mesmo time com uma mensagem automatizada e clara.

## Funcionalidade
- O comandante pode usar o comando `!nodos` no chat do jogo.
- O bot verifica via logs se todos os três tipos de nodos (munição, combustível e mão-de-obra) estão construídos.
- Se algum estiver faltando, os engenheiros do mesmo time recebem uma mensagem privada solicitando a construção.
- O comandante recebe uma confirmação de que a solicitação foi enviada.

## Requisitos
- Python 3.10+
- [hll_rcon_tool (CRCON)](https://github.com/MarechJ/hll_rcon_tool) versão 11.6.1 ou superior

## Instalação
1. Coloque o arquivo `commander_nodos.py` dentro da pasta `custom_tools/` do seu diretório principal do CRCON. Se a pasta não existir, crie.

```
cd /root/hll_rcon_tool
wget https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_restart/refs/heads/main/restart.sh
mkdir custom_tools
```
Depois execute:
```
cd custom_tools
wget https://raw.githubusercontent.com/felipebandeira23/commander_nodos/7ec6ce2f00ca0332d4fe91268b80870adc3e3638/custom_tools/commander_nodos.py
```
2. Edite o arquivo `hooks.py` (localizado em /hll_rcon_tool/rcon) e registre os ganchos do bot:

Bem no início do arquivo
```
import custom_tools.commander_nodos as commander_nodos
```
Depois coloque bem no final do arquivo
```
@on_chat
def commander_nodos_chat(rcon, log):
    commander_nodos.commander_nodos_on_chat(rcon, log)

@on_log
def commander_nodos_log(rcon, log):
    commander_nodos.commander_nodos_on_log(rcon, log)
```

3. Reinicie o CRCON para que o novo plugin seja carregado. Se estiver usando `restart.sh`, basta executar:

```
./restart.sh
```
Ou execute
```
sudo bash restart.sh
```

> Certifique-se de que o script `restart.sh` tem permissões de execução (`chmod +x restart.sh`).

4. Verifique se o bot está habilitado para o servidor correto.
No `commander_nodos.py`, edite se possuir mais de um servidor:
```
ENABLE_ON_SERVERS = ["1"]

# ['1],['2'].... Param mais servidores
```

## Como funciona
- O bot escuta o chat e verifica se o jogador digitou `!nodos`.
- Ele valida se o jogador é o comandante e se está em cooldown.
- O bot rastreia via logs a construção e remoção de nodos e mantém um contador por tipo e por time.
- Se estiver faltando algum tipo de nodo, os engenheiros recebem uma mensagem como:

```
Engenheiros, precisamos de NODOS. Faltando: Munição: 2, Combustível: 1. Por favor, completem para garantirmos recursos!
```

- O comandante recebe a confirmação:
```
Solicitação enviada para X engenheiro(s).
Solicitação de nodos enviadas aos engenheiros!
```

## Personalização
Você pode ajustar:
- Quantidade mínima de nodos (`NODES_REQUIRED_PER_TYPE = 3`)
- Cooldown entre usos (`COOLDOWN_SECONDS = 10`)
- Servidores ativos (`ENABLE_ON_SERVERS`)
- CHAT_COMMAND = (`!nodos`) # Mude para o que preferir

---------------------------------------------------------------------------------
---------------------------------------------------------------------------------
# English - Commander Nodos Bot
Bot for Hell Let Loose servers based on CRCON (hll_rcon_tool), which allows the commander to request the construction of nodes only when necessary. It identifies via logs if any nodes are missing and notifies engineers on the same team with a clear and automated message.

## Functionality
- The commander can use the `!nodes` command in the game chat.
- The bot checks through logs if all three types of nodes (ammunition, fuel, and manpower) are built.
- If any are missing, engineers on the same team receive a private message requesting the construction.
- The commander receives a confirmation that the request has been sent.
  
## Install

```
cd /root/hll_rcon_tool
wget https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_restart/refs/heads/main/restart.sh
mkdir custom_tools
```
Then execute
```
cd custom_tools
wget https://raw.githubusercontent.com/felipebandeira23/commander_nodos/7ec6ce2f00ca0332d4fe91268b80870adc3e3638/custom_tools/commander_nodos.py
```

2. Edit the `hooks.py` file (also in the CRCON root directory) and register the bot hooks:

- In the import part, on top of the file
```
import custom_tools.commander_nodos as commander_nodos 
```
- At the very end of the file
```
@on_chat
def commander_nodos_chat(rcon, log):
commander_nodos.commander_nodos_on_chat(rcon, log)


@on_log
def commander_nodos_log(rcon, log):
commander_nodos.commander_nodos_on_log(rcon, log)
```

3. Restart CRCON so the new plugin is loaded. If using `restart.sh`, simply run:
```
./restart.sh
```
or
```
sudo bash restart.sh
```


> Make sure the `restart.sh` script has execution permission (`chmod +x restart.sh`).


4. Confirm the bot is enabled for the correct server.
Edit this in `commander_nodos.py` if you have more than one server:
```
ENABLE_ON_SERVERS = ["1"]

# ['1],['2'].... If you have more than one
```


## How it works
- The bot listens to chat and checks if the player typed `!nodos`.
- It validates that the player is the commander and not on cooldown.
- The bot tracks node construction/removal via logs and maintains a count per type and team.
- If any node type is missing, engineers receive a message like:


```
Engineers, we need NODOS. Missing: Munitions: 2, Fuel: 1. Please build them to secure our resources!
```


- The commander receives confirmation:
```
Request sent to X engineer(s).
Node request sent to engineers!
```


## Customization
You can adjust:
- Minimum number of required nodes (`NODES_REQUIRED_PER_TYPE = 3`)
- Cooldown between uses (`COOLDOWN_SECONDS = 10`)
- Enabled servers (`ENABLE_ON_SERVERS`)
- CHAT_COMMAND = (`!nodos`) / Switch to whatever you prefer

