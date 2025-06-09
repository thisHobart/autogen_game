"""Core functions to generate NPC replies via AutoGen."""

import os
import logging
import asyncio
from typing import List, Union

from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import (
    SystemMessage,
    UserMessage,
    AssistantMessage,
)

from .world_state import NPCState
from .config import MODEL_NAME

logger = logging.getLogger(__name__)

_CLIENT: OpenAIChatCompletionClient | None = None


def _ensure_client() -> OpenAIChatCompletionClient:
    """Initialize the model client if it hasn't been created."""
    global _CLIENT
    if _CLIENT is None:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        _CLIENT = OpenAIChatCompletionClient(
            model=MODEL_NAME,
            api_key=api_key,
            base_url=base_url,
        )
    return _CLIENT


def _build_messages(npc: NPCState, user_input: str) -> List[Union[SystemMessage, UserMessage, AssistantMessage]]:
    """Construct chat messages using NPC persona and history."""
    messages: List[Union[SystemMessage, UserMessage, AssistantMessage]] = [SystemMessage(content=npc.persona)]
    for role, content in npc.history:
        if role == "user":
            messages.append(UserMessage(content=content, source="user"))
        else:
            messages.append(AssistantMessage(content=content, source="assistant"))
    messages.append(UserMessage(content=user_input, source="user"))
    return messages


async def get_npc_reply(npc: NPCState, user_input: str) -> str:
    """Send conversation to the model and return the assistant reply."""
    client = _ensure_client()
    messages = _build_messages(npc, user_input)
    logger.debug("Sending messages to model: %s", [m.model_dump() for m in messages])
    try:
        result = await client.create(messages)
    except Exception as exc:
        logger.error("Failed to get completion: %s", exc)
        raise
    reply: str = str(result.content).strip()
    npc.add_message("user", user_input)
    npc.add_message("assistant", reply)
    logger.debug("NPC %s replied: %s", npc.name, reply)
    return reply
