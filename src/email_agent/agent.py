from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from email_agent.config import create_model
from email_agent.middleware import (
    create_hitl_middleware,
    dynamic_prompt_func,
    dynamic_tool_call,
)
from email_agent.state import AuthenticatedState
from email_agent.tools import authenticate, check_inbox, send_email


def build_agent(checkpointer=None):
    """
    Build the Email Agent.

    Components:
    - model: MiniMax chat model
    - tools: authentication, inbox reading, email sending
    - state_schema: custom state with authenticated flag
    - checkpointer: short-term memory persistence
    - middleware: dynamic tool routing, dynamic prompt, human approval
    """

    model = create_model()

    if checkpointer is None:
        checkpointer = InMemorySaver()

    return create_agent(
        model=model,
        tools=[authenticate, check_inbox, send_email],
        state_schema=AuthenticatedState,
        checkpointer=checkpointer,
        middleware=[
            dynamic_tool_call,
            dynamic_prompt_func,
            create_hitl_middleware(),
        ],
    )