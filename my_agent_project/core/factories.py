"""Factory helpers for building initial world state."""

from .world_state import WorldState, NPCState, PlayerState


def build_default_world() -> WorldState:
    """Create a default world with one player and two NPCs."""
    world = WorldState(player=PlayerState(name="Hero", position=(0, 0)))
    world.npcs["alice"] = NPCState(
        name="Alice",
        persona="You are Alice, a cheerful adventurer always eager to help.",
        avatar="https://via.placeholder.com/150?text=Alice",
        affection=0,
        position=(1, 0),
    )
    world.npcs["bob"] = NPCState(
        name="Bob",
        persona="You are Bob, a grumpy but kind-hearted guard.",
        avatar="https://via.placeholder.com/150?text=Bob",
        affection=0,
        position=(3, 0),
    )
    return world
