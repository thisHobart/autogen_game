"""Factory helpers for building initial world state."""

from .world_state import WorldState, NPCState


def build_default_world() -> WorldState:
    """Create a simple world with two NPCs."""
    world = WorldState()
    world.npcs["alice"] = NPCState(
        name="Alice",
        persona="You are Alice, a cheerful adventurer always eager to help.",
        avatar="/static/alice.png",
        affection=0,
    )
    world.npcs["bob"] = NPCState(
        name="Bob",
        persona="You are Bob, a grumpy but kind-hearted guard.",
        avatar="/static/bob.png",
        affection=0,
    )
    return world
