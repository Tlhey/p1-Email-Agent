from typing import Any

from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

from email_agent.state import AUTHENTICATED_KEY


VALID_EMAIL = "huge@itcast.cn"
VALID_PASSWORD = "123"


@tool
def authenticate(email: str, password: str, runtime: ToolRuntime) -> Command:
    """
    Authenticate the user with a simulated email and password.
    """

    is_authenticated = email == VALID_EMAIL and password == VALID_PASSWORD

    if is_authenticated:
        message = "Successfully authenticated."
    else:
        message = "Authentication failed. Please check your email and password."

    return Command(
        update={
            AUTHENTICATED_KEY: is_authenticated,
            "messages": [
                ToolMessage(
                    content=message,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool
def check_inbox() -> list[dict[str, Any]]:
    """
    Read the user's inbox.
    """

    return [
        {
            "subject": "周末见个面？",
            "content": (
                "嗨 Tlhey，\n"
                "我下周会去城里，不知道我们有没有机会一起喝杯咖啡？\n\n"
                "祝好，简"
            ),
            "from": "jane@itcast.cn",
            "status": "unread",
        },
        {
            "subject": "周五会议",
            "content": (
                "嗨 Tlhey，\n"
                "非常抱歉，我周五的会议无法准时参加了，能不能重新安排个时间？\n\n"
                "祝好，小李"
            ),
            "from": "lixiaolong@itcast.cn",
            "status": "checked",
        },
    ]


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email.
    In this demo, the email is not actually sent.
    The tool returns a simulated success message.
    """

    return f"邮件已发送至 {to}，主题：{subject}，内容：{body}"