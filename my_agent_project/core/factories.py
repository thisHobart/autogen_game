"""Factory helpers for building initial world state."""

from .world_state import WorldState, NPCState, PlayerState
from .avatar import generate_triangle_avatar


def build_default_world() -> WorldState:
    """Create a default world with one player and two NPCs."""
    world = WorldState(player=PlayerState(name="Hero", position=(0, 0)))
    world.npcs["alice"] = NPCState(
        name="Alice",
        persona="You are Alice, a cheerful adventurer always eager to help.",
        avatar=generate_triangle_avatar("alice"),
        affection=0,
        position=(1, 0),
    )
    world.npcs["bob"] = NPCState(
        name="Bob",
        persona="You are Bob, a grumpy but kind-hearted guard.",
        avatar=generate_triangle_avatar("bob", color="green"),
        affection=0,
        position=(3, 0),
    )
    return world
