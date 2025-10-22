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
cd ~/hll_rcon_tool
mkdir -p custom_tools
cp commander_nodos.py custom_tools/
```

2. Edite o arquivo `hooks.py` (que também está no diretório principal do CRCON) e registre os ganchos do bot:

```python
import custom_tools.commander_nodos as commander_nodos

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

> Certifique-se de que o script `restart.sh` tem permissões de execução (`chmod +x restart.sh`).

4. Verifique se o bot está habilitado para o servidor correto.
No `commander_nodos.py`, edite se necessário:
```python
ENABLE_ON_SERVERS = ["1"]
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

## Licença
MIT
