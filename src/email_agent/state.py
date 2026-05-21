from typing_extensions import NotRequired
from langchain.agents import AgentState

AUTHENTICATED_KEY = "authenticated"

class AuthenticatedState(AgentState):
    authenticated: NotRequired[bool]