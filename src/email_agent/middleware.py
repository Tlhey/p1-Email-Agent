from typing import Callable

from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    ModelRequest,
    ModelResponse,
    dynamic_prompt,
    wrap_model_call,
)

from email_agent.state import AUTHENTICATED_KEY
from email_agent.tools import authenticate, check_inbox, send_email


UNAUTHENTICATED_PROMPT = """
You are a helpful email assistant.

The user has not been authenticated yet.
For security reasons, you must help the user authenticate before doing anything else.

Rules:
1. Do not check the inbox before authentication.
2. Do not send emails before authentication.
3. Ask the user to provide email and password if needed.
4. If the user provides credentials, call the authenticate tool.
"""


AUTHENTICATED_PROMPT = """
You are a helpful email assistant.

The user has already been authenticated.
You can help the user:
1. Check inbox.
2. Summarize emails.
3. Draft email replies.
4. Send emails only through the send_email tool.

Important:
Sending an email is a high-risk action and will require human approval.
"""


@wrap_model_call
def dynamic_tool_call(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """
    """
    authenticated = request.state.get(AUTHENTICATED_KEY, False)
    if authenticated:
        available_tools = [check_inbox, send_email]
    else:
        available_tools = [authenticate]
    request = request.override(tools=available_tools)
    return handler(request)


@dynamic_prompt
def dynamic_prompt_func(request: ModelRequest) -> str:
    """
    Dynamically switch the system prompt based on authentication state.
    """
    authenticated = request.state.get(AUTHENTICATED_KEY, False)
    if authenticated:
        return AUTHENTICATED_PROMPT
    return UNAUTHENTICATED_PROMPT


def create_hitl_middleware() -> HumanInTheLoopMiddleware:
    """
    Create human-in-the-loop middleware.

    Only send_email requires approval.
    Authentication and inbox reading can run automatically.
    """

    return HumanInTheLoopMiddleware(
        interrupt_on={
            "authenticate": False,
            "check_inbox": False,
            "send_email": True,
        }
    )