"""Data structures for storing world and NPC state."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional

from .config import HISTORY_KEEP

@dataclass
class NPCState:
    """State associated with a single NPC."""

    name: str
    persona: str
    avatar: str
    affection: int = 0
    position: Tuple[int, int] = (0, 0)
    history: List[Tuple[str, str]] = field(default_factory=list)

    def add_message(self, role: str, content: str, keep: int = HISTORY_KEEP) -> None:
        """Append a message to the history and keep only the last ``keep`` entries."""
        self.history.append((role, content))
        if len(self.history) > keep:
            self.history.pop(0)


@dataclass
class PlayerState:
    """State associated with the single player."""

    name: str
    hp: int = 100
    position: Tuple[int, int] = (0, 0)
    inventory: List[str] = field(default_factory=list)

    def add_item(self, item: str) -> None:
        """Add an item to the player's inventory."""
        self.inventory.append(item)

    def move_to(self, x: int, y: int) -> None:
        """Move the player to the given coordinates."""
        self.position = (x, y)

    def distance_to(self, npc: "NPCState") -> int:
        """Return Manhattan distance to the given NPC."""
        return abs(self.position[0] - npc.position[0]) + abs(self.position[1] - npc.position[1])

@dataclass
class WorldState:
    """Global world state tracking NPCs and unlocked events."""

    player: PlayerState = field(default_factory=lambda: PlayerState(name="Hero"))
    npcs: Dict[str, NPCState] = field(default_factory=dict)
    events: Set[str] = field(default_factory=set)
    active_npc: Optional[str] = None

    def get_active_npc(self) -> Optional[NPCState]:
        """Return the NPC the player is currently talking to, if any."""
        if self.active_npc:
            return self.npcs.get(self.active_npc)
        return None
