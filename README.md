# Email Agent HITL

A LangChain/LangGraph-based Email Agent prototype demonstrating dynamic tool routing, authentication-aware state management, and human-in-the-loop approval for high-risk tool calls.

# Run
cli:
PYTHONPATH=src python -m email_agent.cli
backend:
PYTHONPATH=src .venv/bin/uvicorn email_agent.web:app --port 8000 --reload
http://localhost:8000/docs 
fronntend:
http://localhost:8000


## Features

- Authentication-aware agent state
- Dynamic prompt switching
- Dynamic tool routing
- Simulated inbox reading and email sending
- Human-in-the-loop approval before sending emails
- Multi-turn conversation persistence with checkpointer
- MiniMax model integration through OpenAI-compatible API

## Tech Stack

- Python
- LangChain
- LangGraph
- MiniMax
- python-dotenv
- FastAPI/SSE planned

## Planned Roadmap

- [√] CLI demo
- [√] MiniMax model integration
- [√] Authentication tool
- [√] Inbox and send-email tools
- [√] Dynamic middleware
- [√] Human-in-the-loop approval
- [ ] FastAPI + SSE backend
- [ ] Simple web UI