"""
commander_nodos.py

Plugin para CRCON/HLL:
- Comandante pode usar !nodos para solicitar nodos.
- Bot verifica se estão faltando nodos de Munição, Combustível ou Mão-de-obra.
- Se estiver faltando, engenheiros do mesmo time recebem mensagem.
- Feedback é enviado ao comandante.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Final

from rcon.rcon import Rcon, StructuredLogLineWithMetaData
from rcon.types import Roles

# -------- CONFIG --------
ENABLE_ON_SERVERS: Final = ["1"]
CHAT_COMMAND: Final = "!nodos"
COOLDOWN_SECONDS: Final = 10
NODE_TYPES = ["muni", "fuel", "manpower"]  # identificadores nos logs
NODES_REQUIRED_PER_TYPE = 3
# ------------------------

_last_used: dict[str, datetime] = {}
_node_counts: dict[str, dict[str, int]] = {
    "Allies": {"muni": 0, "fuel": 0, "manpower": 0},
    "Axis": {"muni": 0, "fuel": 0, "manpower": 0},
}


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

def _format_missing_nodes(team: str) -> str:
    counts = _node_counts.get(team, {})
    missing = []
    for key in NODE_TYPES:
        count = counts.get(key, 0)
        if count < NODES_REQUIRED_PER_TYPE:
            label = {
                "muni": "Munição",
                "fuel": "Combustível",
                "manpower": "Mão-de-obra"
            }[key]
            missing.append(f"{label}: {NODES_REQUIRED_PER_TYPE - count}")
    return ", ".join(missing)

def commander_nodos_on_chat(rcon: Rcon, log: StructuredLogLineWithMetaData):
    if not _enabled(): return

    msg = _norm(log.get("sub_content"))
    if not msg.startswith(CHAT_COMMAND): return

    pid = log.get("player_id_1")
    if not pid: return

    if not _can_use(pid):
        rcon.message_player(pid, f"Aguarde {COOLDOWN_SECONDS}s entre usos de {CHAT_COMMAND}.", False)
        return

    role, team = _get_sender_info(rcon, pid)
    if _norm(role) != _norm(Roles.commander.value):
        rcon.message_player(pid, "Apenas o comandante pode usar !nodos.", False)
        return

    if not team:
        rcon.message_player(pid, "Não consegui identificar seu time.", False)
        return

    missing_str = _format_missing_nodes(team)
    if not missing_str:
        rcon.message_player(pid, "Todos os tipos de nodos já estão construídos!", False)
        return

    ids = _list_engineers(rcon, team)
    if not ids:
        rcon.message_player(pid, "Nenhum engenheiro encontrado no seu time.", False)
        return

    msg_to_eng = f"Engenheiros, precisamos de NODOS. Faltando: {missing_str}. Por favor, completem para garantirmos recursos!"
    for eid in ids:
        rcon.message_player(eid, msg_to_eng, False)

    rcon.message_player(pid, f"Solicitação enviada para {len(ids)} engenheiro(s).", False)
    rcon.message_player(pid, "Solicitação de nodos enviadas aos engenheiros!", False)
    _set_used(pid)

# log handler para atualização do contador de nodos via logs

def commander_nodos_on_log(rcon: Rcon, log: StructuredLogLineWithMetaData):
    line = _norm(log.get("raw"))
    if "built" not in line and "dismantled" not in line:
        return

    for key in NODE_TYPES:
        if key in line:
            for team in ["Allies", "Axis"]:
                if team.lower() in line:
                    delta = 1 if "built" in line else -1
                    _node_counts[team][key] = max(0, _node_counts[team][key] + delta)
                    break
