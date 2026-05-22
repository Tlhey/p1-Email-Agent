from __future__ import annotations
import json
from typing import Any
from langchain.messages import HumanMessage
from langgraph.types import Command
from email_agent.agent import build_agent


def print_message_token(data: Any) -> None:
    """
    Print streaming message tokens.

    In stream_mode=["messages", "updates"], message chunks usually contain:
    - token
    - metadata
    """

    try:
        token, _metadata = data
    except Exception:
        return

    content = getattr(token, "content", "")

    if content:
        print(content, end="", flush=True)


def extract_interrupt(data: Any) -> Any | None:
    """
    Extract interrupt data from a stream update.

    Different LangChain/LangGraph versions may expose interrupt payloads
    slightly differently, so this function handles the common shapes.
    """

    if not isinstance(data, dict):
        return None

    if "__interrupt__" in data:
        return data["__interrupt__"]

    if "interrupts" in data:
        return data["interrupts"]

    return None


def print_interrupt(interrupt_data: Any) -> None:
    """
    Print human-readable interrupt information.
    """

    print("\n\nHUMAN APPROVAL REQUIRED")

    try:
        print(json.dumps(interrupt_data, ensure_ascii=False, indent=2, default=str))
    except TypeError:
        print(interrupt_data)


def ask_human_decision() -> dict[str, Any]:
    """
    Ask the human reviewer how to handle the interrupted tool call.

    Supported decisions:
    - approve
    - reject
    """

    print("\n请选择操作：")
    print("1. approve  允许执行")
    print("2. reject   拒绝执行，并告诉 Agent 原因")

    choice = input("\n你的选择 [approve/reject]: ").strip().lower()

    if choice in {"approve", "a", "1"}:
        return {"type": "approve"}

    if choice in {"reject", "r", "2"}:
        reason = input("拒绝原因：").strip() or "未提供原因"
        return {
            "type": "reject",
            "message": (
                f"[REJECTED] 该操作已被用户拒绝，邮件未发送。\n"
                f"原因：{reason}\n"
                f"请告知用户操作已被取消，不要重试。"
            ),
        }

    print("无法识别输入，默认 reject。")
    return {
        "type": "reject",
        "message": "[REJECTED] 该操作已被用户拒绝，邮件未发送。请告知用户操作已被取消，不要重试。",
    }


def stream_agent(agent, payload: Any, config: dict[str, Any]) -> bool:
    """
    Stream one agent run.

    Returns:
    - True if an interrupt occurred
    - False otherwise
    """

    interrupted = False

    response = agent.stream(
        payload,
        config=config,
        stream_mode=["messages", "updates"],
        version="v2",
    )

    for chunk in response:
        chunk_type = chunk.get("type")
        data = chunk.get("data")

        if chunk_type == "messages":
            print_message_token(data)

        elif chunk_type == "updates":
            interrupt_data = extract_interrupt(data)
            if interrupt_data is not None:
                interrupted = True
                print_interrupt(interrupt_data)

    print()

    return interrupted


def main() -> None:
    """
    Run the Email Agent in CLI mode.
    """

    agent = build_agent()

    thread_id = input("Thread ID [demo-thread]: ").strip() or "demo-thread"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    print("\nEmail Agent CLI started.")
    print("测试账号：huge@itcast.cn")
    print("测试密码：123")
    print("输入 exit 退出。\n")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Bye.")
            break

        interrupted = stream_agent(
            agent=agent,
            payload={"messages": [HumanMessage(content=user_input)]},
            config=config,
        )

        while interrupted:
            decision = ask_human_decision()

            interrupted = stream_agent(
                agent=agent,
                payload=Command(
                    resume={
                        "decisions": [decision],
                    }
                ),
                config=config,
            )


if __name__ == "__main__":
    main()