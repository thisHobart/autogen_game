"""Simple Gradio interface for interacting with NPCs."""

import os
import logging
from typing import List, Tuple

import gradio as gr
from dotenv import load_dotenv

from core.factories import build_default_world
from core.router import route
from core.dialog import get_npc_reply
from core.config import AFFECTION_EVENT_THRESHOLD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
env_path = os.path.join(os.path.dirname(__file__), "config", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    logger.warning("Environment file %s not found", env_path)

if not os.getenv("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY is not configured")

# Build initial world with player and two NPCs
WORLD = build_default_world()


def _status() -> str:
    """Return a human-readable status of player and NPCs."""
    status = {n.name: n.affection for n in WORLD.npcs.values()}
    status[WORLD.player.name] = WORLD.player.hp
    return str(status)


async def start_dialog(npc_name: str, history: List[Tuple[str, str]] | None) -> Tuple[List[Tuple[str, str]], str]:
    """Move player near ``npc_name`` and begin conversation."""
    history = history or []
    npc = WORLD.npcs.get(npc_name.lower())
    if not npc:
        logger.warning("NPC %s not found", npc_name)
        history.append(("系统", f"未找到 NPC {npc_name}"))
        return history, _status()
    WORLD.player.move_to(*npc.position)
    WORLD.active_npc = npc_name.lower()
    logger.info("Player approaches %s", npc_name)
    try:
        reply = await get_npc_reply(npc, "你好")
    except Exception as exc:
        reply = f"[对话出错]: {exc}"
        logger.error("Error starting dialog: %s", exc)
    history.append(("系统", f"你靠近了 {npc.name}"))
    history.append((npc.name, reply))
    return history, _status()


async def end_dialog(history: List[Tuple[str, str]] | None) -> Tuple[List[Tuple[str, str]], str]:
    """Finish current conversation if any."""
    history = history or []
    if WORLD.active_npc:
        logger.info("End conversation with %s", WORLD.active_npc)
        history.append(("系统", f"你离开了 {WORLD.active_npc}"))
        WORLD.active_npc = None
    else:
        history.append(("系统", "当前没有进行中的对话"))
    return history, _status()


async def on_end(history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """Callback for the UI end button."""
    return await end_dialog(history)


async def process(user_input: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """Process the player's message and return updated chat history."""
    if not user_input:
        logger.debug("Empty user input received")
        return history or [], _status()

    lowered = user_input.lower()
    if lowered in ("结束对话", "exit"):
        return await end_dialog(history)
    if lowered.startswith("approach "):
        npc_name = user_input.split(" ", 1)[1]
        return await start_dialog(npc_name, history)
    if lowered.startswith("靠近"):
        npc_name = user_input[2:].strip()
        return await start_dialog(npc_name, history)

    npc, cleaned = route(WORLD, user_input)
    try:
        reply = await get_npc_reply(npc, cleaned)
    except Exception as exc:
        reply = f"[对话出错]: {exc}"
        logger.error("Error during dialog: %s", exc)
    npc.affection += 1
    if (
        npc.affection >= AFFECTION_EVENT_THRESHOLD
        and f"{npc.name}_event" not in WORLD.events
    ):
        WORLD.events.add(f"{npc.name}_event")
        reply += f"\n[{npc.name} 的特殊剧情已解锁!]"
    history = history or []
    history.append(("玩家", user_input))
    history.append((npc.name, reply))
    return history, _status()


def build_interface() -> gr.Blocks:
    with gr.Blocks() as demo:
        gr.Markdown(f"### Player: {WORLD.player.name}")
        with gr.Row():
            gr.Image(value=WORLD.npcs["alice"].avatar, label="Alice")
            gr.Image(value=WORLD.npcs["bob"].avatar, label="Bob")

        chatbot = gr.Chatbot()
        info = gr.Textbox(label="状态信息")
        state = gr.State([])
        with gr.Row():
            msg = gr.Textbox(label="输入")
            btn = gr.Button("发送")
            end_btn = gr.Button("结束对话")
        btn.click(process, [msg, state], [chatbot, info])
        msg.submit(process, [msg, state], [chatbot, info])
        end_btn.click(on_end, [state], [chatbot, info])
    return demo


if __name__ == "__main__":
    ui = build_interface()
    ui.launch()
