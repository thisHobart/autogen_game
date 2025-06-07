import os
from dotenv import load_dotenv
import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base._task import TaskResult

# ────────────── ① 加载 .env 配置 ──────────────
env_path = os.path.join(os.path.dirname(__file__), "config", ".env")
load_dotenv(dotenv_path=env_path)

# ────────────── ② 创建模型客户端 ──────────────
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-2024-11-20",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# ────────────── ③ 自定义便捷函数 ──────────────
def extract_assistant_reply(result: TaskResult) -> str:
    """在 TaskResult.messages 中取最后一条 assistant 消息"""
    for msg in reversed(result.messages):
        if msg.source == "assistant":
            return msg.content
    return ""

# ────────────── ④ 声明 Agent ──────────────
agent = AssistantAgent(name="assistant", model_client=model_client)

# ────────────── ⑤ 交互式聊天函数 ──────────────
def interactive_chat() -> None:
    """
    在 PyCharm 控制台中循环读取用户输入，并调用 agent.run 进行异步对话，
    直到用户输入 “exit” 或 “quit” 才停止。
    """
    print("===== 欢迎进入 AI 交互式对话 (输入 exit 或 quit 以退出) =====\n")
    while True:
        try:
            # 1. 从用户读取一行输入
            user_input = input("你: ").strip()
            if not user_input:
                # 空行则跳过，不调用 AI
                continue
            if user_input.lower() in ("exit", "quit"):
                print("已退出对话。")
                break

            # 2. 异步调用 agent.run，让 AI 作答
            #    这里我们每次都用 asyncio.run 重新创建一个事件循环，简单易懂
            result = asyncio.run(agent.run(task=user_input))
            reply_raw = extract_assistant_reply(result)
            reply = reply_raw.removesuffix(" TERMINATE").strip()

            # 3. 输出 AI 回复
            print("助手: " + reply + "\n")

        except KeyboardInterrupt:
            # 捕捉 Ctrl+C，友好退出循环
            print("\n检测到中断，已退出对话。")
            break
        except Exception as e:
            # 其他异常时打印错误信息，但不终止整个对话
            print(f"[错误] 处理失败：{e}\n")

# ────────────── ⑥ 入口保护 ──────────────
if __name__ == "__main__":
    interactive_chat()
