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

# Build initial world with two NPCs
WORLD = build_default_world()


def process(user_input: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
    """Process the player's message and return updated chat history."""
    npc, cleaned = route(WORLD, user_input)
    try:
        reply = get_npc_reply(npc, cleaned)
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
    status = {n.name: n.affection for n in WORLD.npcs.values()}
    return history, str(status)


def build_interface() -> gr.Blocks:
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot()
        info = gr.Textbox(label="状态信息")
        state = gr.State([])
        with gr.Row():
            msg = gr.Textbox(label="输入")
            btn = gr.Button("发送")
        btn.click(process, [msg, state], [chatbot, info])
        msg.submit(process, [msg, state], [chatbot, info])
    return demo


if __name__ == "__main__":
    ui = build_interface()
    ui.launch()
