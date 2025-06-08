"""Routing functions to dispatch user input to the correct NPC."""

import logging
from typing import Tuple

from .world_state import WorldState, NPCState

logger = logging.getLogger(__name__)


def route(world: WorldState, user_input: str) -> Tuple[NPCState, str]:
    """Return the target NPC and cleaned message."""
    lowered = user_input.lower()
    for name, npc in world.npcs.items():
        prefix = f"{name.lower()}:"
        if lowered.startswith(prefix):
            cleaned = user_input[len(prefix):].lstrip()
            logger.debug("Routed input to NPC %s", name)
            return npc, cleaned
    # fallback to first NPC
    npc = next(iter(world.npcs.values()))
    logger.debug("Defaulting to first NPC: %s", npc.name)
    return npc, user_input
