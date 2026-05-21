import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


@dataclass
class Settings:
    """Runtime configuration for the Email Agent."""

    minimax_api_key: str
    minimax_base_url: str
    minimax_model: str
    temperature: float = 0.0


def load_settings() -> Settings:
    """
    Load model configuration from environment variables.

    This function keeps secrets out of source code.
    It reads values from .env during local development.
    """

    load_dotenv()

    api_key = os.getenv("MINIMAX_API_KEY")
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/v1")
    model = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")

    if not api_key:
        raise ValueError(
            "MINIMAX_API_KEY is missing. Please create a .env file based on .env.example."
        )

    return Settings(
        minimax_api_key=api_key,
        minimax_base_url=base_url,
        minimax_model=model,
        temperature=0.0,
    )


def create_model() -> ChatOpenAI:
    """
    Create a MiniMax chat model through the OpenAI-compatible interface.
    """

    settings = load_settings()

    return ChatOpenAI(
        model=settings.minimax_model,
        api_key=settings.minimax_api_key,
        base_url=settings.minimax_base_url,
        temperature=settings.temperature,
    )