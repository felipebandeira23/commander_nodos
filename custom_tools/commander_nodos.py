"""
commander_nodos.py


This bot was developed by:
Felipe Bandeira 
[https://github.com/felipebandeira23/commander_nodos](https://github.com/felipebandeira23/commander_nodos)


Plugin para CRCON/HLL:
- Comandante pode usar !nodos para solicitar nodos aos engenheiros.
- Engenheiros podem usar !feito [tipo] para confirmar conclusão.
- Comandante recebe notificação quando engenheiros confirmarem.
- Sistema de rastreamento de solicitações por time.

Plugin for CRCON/HLL (Hell Let Loose):

- The Commander can use !nodos in chat to request node construction from Engineers in their team.
- Engineers can use !feito [type] (e.g., !feito muni) to confirm completion of node building. Supported types: muni (Munition), fuel (Fuel), manpower (Manpower).
- The Commander receives notifications whenever engineers confirm completion.
- Request tracking is team-based: confirmations are tracked per node type for each team.
- Progress and status updates (number of nodes built vs. required) are sent to Commander and Engineers.

Automatic language support: all bot messages can be displayed in Portuguese or English, depending on configuration.
"""


from __future__ import annotations
from datetime import datetime, timedelta
from typing import Final, Optional

from rcon.rcon import Rcon, StructuredLogLineWithMetaData
from rcon.types import Roles

# -------- CONFIG --------
ENABLE_ON_SERVERS: Final = ["1"]
CHAT_COMMAND_REQUEST: Final = "!nodos"
CHAT_COMMAND_CONFIRM: Final = "!feito"
COOLDOWN_SECONDS: Final = 60
LANGUAGE: Final = "pt"  # "pt" para Português, "en" para English

# Traduções
TRANSLATIONS = {
    "pt": {
        "node_types": {
            "muni": "Munição",
            "fuel": "Combustível", 
            "manpower": "Mão-de-obra"
        },
        "commander_only": "Apenas o comandante pode usar !nodos.",
        "engineer_only": "Apenas engenheiros podem usar !feito.",
        "cooldown": "Aguarde {cooldown}s entre usos de {command}.",
        "team_not_found": "Não consegui identificar seu time.",
        "no_engineers": "Nenhum engenheiro encontrado no seu time.",
        "request_sent": "Solicitação enviada para {count} engenheiro(s)!\nAguardando confirmações: {status}",
        "commander_request": "COMANDANTE SOLICITOU NODES!\nPrecisamos: {types}\nQuando terminar, confirme: !feito [muni/fuel/manpower]",
        "no_active_request": "Nenhuma solicitação de nodes ativa no momento.",
        "usage": "Use: !feito [muni/fuel/manpower]\nExemplo: !feito muni",
        "invalid_type": "Tipo inválido! Use: muni, fuel ou manpower\nExemplo: !feito muni",
        "already_confirmed": "Você já confirmou {type}.",
        "confirmed": "Confirmado: {type}\nStatus: {status}",
        "node_confirmed": "Node confirmado: {type}\nStatus: {status}",
        "all_confirmed": "TODOS OS NODES CONFIRMADOS!\nRecursos completos disponíveis!",
        "mission_complete": "Missão completa! Todos os nodes construídos!",
        "no_active": "Nenhuma solicitação ativa."
    },
    "en": {
        "node_types": {
            "muni": "Munition",
            "fuel": "Fuel",
            "manpower": "Manpower"
        },
        "commander_only": "Only the commander can use !nodos.",
        "engineer_only": "Only engineers can use !feito.",
        "cooldown": "Wait {cooldown}s between uses of {command}.",
        "team_not_found": "Could not identify your team.",
        "no_engineers": "No engineers found on your team.",
        "request_sent": "Request sent to {count} engineer(s)!\nAwaiting confirmations: {status}",
        "commander_request": "COMMANDER REQUESTED NODES!\nWe need: {types}\nWhen finished, confirm: !feito [muni/fuel/manpower]",
        "no_active_request": "No active node request at the moment.",
        "usage": "Use: !feito [muni/fuel/manpower]\nExample: !feito muni",
        "invalid_type": "Invalid type! Use: muni, fuel or manpower\nExample: !feito muni",
        "already_confirmed": "You already confirmed {type}.",
        "confirmed": "Confirmed: {type}\nStatus: {status}",
        "node_confirmed": "Node confirmed: {type}\nStatus: {status}",
        "all_confirmed": "ALL NODES CONFIRMED!\nFull resources available!",
        "mission_complete": "Mission complete! All nodes built!",
        "no_active": "No active request."
    }
}

NODES_REQUIRED_PER_TYPE = 3
# ------------------------

# Estrutura para rastrear solicitações ativas
_active_requests: dict[str, dict] = {}  # team -> {commander_id, timestamp, engineers_notified, confirmations}
_last_used: dict[str, datetime] = {}


def _now() -> datetime:
    return datetime.utcnow()

def _can_use(pid: str) -> bool:
    last = _last_used.get(pid)
    return not last or (_now() - last).total_seconds() >= COOLDOWN_SECONDS

def _set_used(pid: str):
    _last_used[pid] = _now()

def _norm(s: str | None) -> str:
    return (s or "").strip().lower()

def _enabled() -> bool:
    from rcon.utils import get_server_number
    return str(get_server_number()) in ENABLE_ON_SERVERS

def _t(key: str, **kwargs) -> str:
    """Retorna a tradução para a chave especificada no idioma configurado."""
    text = TRANSLATIONS.get(LANGUAGE, TRANSLATIONS["pt"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

def _get_node_types() -> dict[str, str]:
    """Retorna os tipos de nodes no idioma configurado."""
    return TRANSLATIONS.get(LANGUAGE, TRANSLATIONS["pt"])["node_types"]

def _get_sender_info(rcon: Rcon, pid: str) -> tuple[str | None, str | None]:
    """Obtém role e team do jogador."""
    role = team = None
    try:
        players = (rcon.get_detailed_players() or {}).get("players", {})
        me = players.get(pid)
        if me:
            role = me.get("role")
            team = me.get("team")
    except Exception:
        pass
    if not role or not team:
        try:
            info = rcon.get_player_info(player=pid) or {}
            role = role or info.get("role")
            team = team or info.get("team")
        except Exception:
            pass
    return role, team

def _list_engineers(rcon: Rcon, team: str) -> list[str]:
    """Lista todos os IDs dos engenheiros no time especificado."""
    ids = []
    try:
        for p in (rcon.get_detailed_players() or {}).get("players", {}).values():
            if _norm(p.get("team")) == _norm(team) and _norm(p.get("role")) == "engineer":
                pid = p.get("player_id")
                if pid:
                    ids.append(pid)
    except Exception:
        pass
    return ids

def _get_commander_id(team: str) -> Optional[str]:
    """Obtém o ID do comandante que fez a solicitação ativa."""
    req = _active_requests.get(team)
    return req["commander_id"] if req else None

def _create_request(team: str, commander_id: str, num_engineers: int):
    """Cria uma nova solicitação de nodes para o time."""
    _active_requests[team] = {
        "commander_id": commander_id,
        "timestamp": _now(),
        "engineers_notified": num_engineers,
        "confirmations": {}  # tipo_node -> [engineer_ids que confirmaram]
    }

def _add_confirmation(team: str, node_type: str, engineer_id: str):
    """Adiciona confirmação de um engenheiro para um tipo de node."""
    if team not in _active_requests:
        return False
    
    req = _active_requests[team]
    if node_type not in req["confirmations"]:
        req["confirmations"][node_type] = []
    
    if engineer_id not in req["confirmations"][node_type]:
        req["confirmations"][node_type].append(engineer_id)
        return True
    return False

def _get_confirmation_status(team: str) -> str:
    """Retorna o status atual das confirmações."""
    if team not in _active_requests:
        return _t("no_active")
    
    req = _active_requests[team]
    confirmations = req["confirmations"]
    node_types = _get_node_types()
    
    status_parts = []
    for node_key, node_label in node_types.items():
        count = len(confirmations.get(node_key, []))
        if count >= NODES_REQUIRED_PER_TYPE:
            status_parts.append(f"[OK] {node_label}: {count}/{NODES_REQUIRED_PER_TYPE}")
        else:
            status_parts.append(f"[...] {node_label}: {count}/{NODES_REQUIRED_PER_TYPE}")
    
    return " | ".join(status_parts)

def _is_request_complete(team: str) -> bool:
    """Verifica se todos os nodes foram confirmados."""
    if team not in _active_requests:
        return False
    
    req = _active_requests[team]
    node_types = _get_node_types()
    for node_type in node_types.keys():
        if len(req["confirmations"].get(node_type, [])) < NODES_REQUIRED_PER_TYPE:
            return False
    return True

def _clear_request(team: str):
    """Remove a solicitação ativa do time."""
    if team in _active_requests:
        del _active_requests[team]

def commander_nodos_on_chat(rcon: Rcon, log: StructuredLogLineWithMetaData):
    """Handler principal para comandos de chat."""
    if not _enabled(): 
        return

    msg = _norm(log.get("sub_content"))
    pid = log.get("player_id_1")
    
    if not pid:
        return

    # Comando do comandante: !nodos
    if msg.startswith(CHAT_COMMAND_REQUEST):
        _handle_commander_request(rcon, pid)
        return
    
    # Comando dos engenheiros: !nodook [tipo]
    if msg.startswith(CHAT_COMMAND_CONFIRM):
        _handle_engineer_confirmation(rcon, pid, msg)
        return


def _handle_commander_request(rcon: Rcon, pid: str):
    """Processa solicitação de nodes do comandante."""
    if not _can_use(pid):
        rcon.message_player(pid, _t("cooldown", cooldown=COOLDOWN_SECONDS, command=CHAT_COMMAND_REQUEST), False)
        return

    role, team = _get_sender_info(rcon, pid)
    
    if _norm(role) != _norm(Roles.commander.value):
        rcon.message_player(pid, _t("commander_only"), False)
        return

    if not team:
        rcon.message_player(pid, _t("team_not_found"), False)
        return

    # Lista engenheiros disponíveis
    engineer_ids = _list_engineers(rcon, team)
    if not engineer_ids:
        rcon.message_player(pid, _t("no_engineers"), False)
        return

    # Cria nova solicitação
    _create_request(team, pid, len(engineer_ids))
    
    # Monta mensagem para engenheiros
    node_types = _get_node_types()
    types_list = ', '.join(node_types.values())
    msg_to_eng = _t("commander_request", types=types_list)
    
    for eid in engineer_ids:
        rcon.message_player(eid, msg_to_eng, False)

    rcon.message_player(
        pid, 
        _t("request_sent", count=len(engineer_ids), status=_get_confirmation_status(team)),
        False
    )
    _set_used(pid)


def _handle_engineer_confirmation(rcon: Rcon, pid: str, msg: str):
    """Processa confirmação de node construído por engenheiro."""
    role, team = _get_sender_info(rcon, pid)
    
    if _norm(role) != "engineer":
        rcon.message_player(pid, _t("engineer_only"), False)
        return
    
    if not team:
        return
    
    # Verifica se há solicitação ativa
    if team not in _active_requests:
        rcon.message_player(pid, _t("no_active_request"), False)
        return
    
    # Extrai tipo de node do comando: !feito muni/fuel/manpower
    parts = msg.split()
    if len(parts) < 2:
        rcon.message_player(pid, _t("usage"), False)
        return
    
    node_type = _norm(parts[1])
    node_types = _get_node_types()
    
    # Valida tipo de node
    if node_type not in node_types:
        rcon.message_player(pid, _t("invalid_type"), False)
        return
    
    # Adiciona confirmação
    if not _add_confirmation(team, node_type, pid):
        rcon.message_player(pid, _t("already_confirmed", type=node_types[node_type]), False)
        return
    
    # Feedback para engenheiro
    rcon.message_player(
        pid,
        _t("confirmed", type=node_types[node_type], status=_get_confirmation_status(team)),
        False
    )
    
    # Notifica comandante do progresso
    commander_id = _get_commander_id(team)
    if commander_id:
        rcon.message_player(
            commander_id,
            _t("node_confirmed", type=node_types[node_type], status=_get_confirmation_status(team)),
            False
        )
    
    # Verifica se todos os nodes foram confirmados
    if _is_request_complete(team):
        # Notifica comandante
        if commander_id:
            rcon.message_player(commander_id, _t("all_confirmed"), False)
        
        # Notifica todos os engenheiros
        for eid in _list_engineers(rcon, team):
            rcon.message_player(eid, _t("mission_complete"), False)
        
        # Limpa a solicitação
        _clear_request(team)
        _clear_request(team)
