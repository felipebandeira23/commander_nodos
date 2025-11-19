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
NODE_TYPES_PT = {
    "muni": "Munição",
    "fuel": "Combustível", 
    "manpower": "Mão-de-obra"
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
        return "Nenhuma solicitação ativa."
    
    req = _active_requests[team]
    confirmations = req["confirmations"]
    
    status_parts = []
    for node_key, node_label in NODE_TYPES_PT.items():
        count = len(confirmations.get(node_key, []))
        if count >= NODES_REQUIRED_PER_TYPE:
            status_parts.append(f"✓ {node_label}: {count}/{NODES_REQUIRED_PER_TYPE}")
        else:
            status_parts.append(f"⏳ {node_label}: {count}/{NODES_REQUIRED_PER_TYPE}")
    
    return " | ".join(status_parts)


def _is_request_complete(team: str) -> bool:
    """Verifica se todos os nodes foram confirmados."""
    if team not in _active_requests:
        return False
    
    req = _active_requests[team]
    for node_type in NODE_TYPES_PT.keys():
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
        rcon.message_player(pid, f"Aguarde {COOLDOWN_SECONDS}s entre usos de {CHAT_COMMAND_REQUEST}.", False)
        return


    role, team = _get_sender_info(rcon, pid)
    
    if _norm(role) != _norm(Roles.commander.value):
        rcon.message_player(pid, "Apenas o comandante pode usar !nodos.", False)
        return


    if not team:
        rcon.message_player(pid, "Não consegui identificar seu time.", False)
        return


    # Lista engenheiros disponíveis
    engineer_ids = _list_engineers(rcon, team)
    if not engineer_ids:
        rcon.message_player(pid, "Nenhum engenheiro encontrado no seu time.", False)
        return


    # Cria nova solicitação
    _create_request(team, pid, len(engineer_ids))
    
    # Monta mensagem com status inicial
    needed = []
    for node_label in NODE_TYPES_PT.values():
        needed.append(f"{node_label} (0/{NODES_REQUIRED_PER_TYPE})")
    
    msg_to_eng = (
        f"⚠️ COMANDANTE SOLICITOU NODES! ⚠️\n"
        f"Precisamos: {', '.join(NODE_TYPES_PT.values())}\n"
        f"Quando terminar, confirme: !feito [muni/fuel/manpower]"
    )
    
    for eid in engineer_ids:
        rcon.message_player(eid, msg_to_eng, False)


    rcon.message_player(
        pid, 
        f"✓ Solicitação enviada para {len(engineer_ids)} engenheiro(s)!\n"
        f"Aguardando confirmações: {_get_confirmation_status(team)}", 
        False
    )
    _set_used(pid)



def _handle_engineer_confirmation(rcon: Rcon, pid: str, msg: str):
    """Processa confirmação de node construído por engenheiro."""
    role, team = _get_sender_info(rcon, pid)
    
    if _norm(role) != "engineer":
        rcon.message_player(pid, "Apenas engenheiros podem usar !feito.", False)
        return
    
    if not team:
        return
    
    # Verifica se há solicitação ativa
    if team not in _active_requests:
        rcon.message_player(pid, "Nenhuma solicitação de nodes ativa no momento.", False)
        return
    
    # Extrai tipo de node do comando: !feito muni/fuel/manpower
    parts = msg.split()
    if len(parts) < 2:
        rcon.message_player(
            pid,
            f"Use: !feito [muni/fuel/manpower]\n"
            f"Exemplo: !feito muni",
            False
        )
        return
    
    node_type = _norm(parts[1])
    
    # Valida tipo de node
    if node_type not in NODE_TYPES_PT:
        rcon.message_player(
            pid, 
            f"Tipo inválido! Use: muni, fuel ou manpower\n"
            f"Exemplo: !feito muni",
            False
        )
        return
    
    # Adiciona confirmação
    if not _add_confirmation(team, node_type, pid):
        rcon.message_player(pid, f"Você já confirmou {NODE_TYPES_PT[node_type]}.", False)
        return
    
    # Feedback para engenheiro
    rcon.message_player(
        pid,
        f"✓ Confirmado: {NODE_TYPES_PT[node_type]}\n"
        f"Status: {_get_confirmation_status(team)}",
        False
    )
    
    # Notifica comandante do progresso
    commander_id = _get_commander_id(team)
    if commander_id:
        rcon.message_player(
            commander_id,
            f"✓ Node confirmado: {NODE_TYPES_PT[node_type]}\n"
            f"Status: {_get_confirmation_status(team)}",
            False
        )
    
    # Verifica se todos os nodes foram confirmados
    if _is_request_complete(team):
        # Notifica comandante
        if commander_id:
            rcon.message_player(
                commander_id,
                "🎉 TODOS OS NODES CONFIRMADOS! 🎉\n"
                "Recursos completos disponíveis!",
                False
            )
        
        # Notifica todos os engenheiros
        for eid in _list_engineers(rcon, team):
            rcon.message_player(
                eid,
                "🎉 Missão completa! Todos os nodes construídos! 🎉",
                False
            )
        
        # Limpa a solicitação
        _clear_request(team)
