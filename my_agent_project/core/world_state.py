"""Data structures for storing world and NPC state."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set

from .config import HISTORY_KEEP

@dataclass
class NPCState:
    """State associated with a single NPC."""

    name: str
    persona: str
    avatar: str
    affection: int = 0
    history: List[Tuple[str, str]] = field(default_factory=list)

    def add_message(self, role: str, content: str, keep: int = HISTORY_KEEP) -> None:
        """Append a message to the history and keep only the last ``keep`` entries."""
        self.history.append((role, content))
        if len(self.history) > keep:
            self.history.pop(0)

@dataclass
class WorldState:
    """Global world state tracking NPCs and unlocked events."""

    npcs: Dict[str, NPCState] = field(default_factory=dict)
    events: Set[str] = field(default_factory=set)
