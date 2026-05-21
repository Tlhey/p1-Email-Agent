# Email Agent HITL

A LangChain/LangGraph-based Email Agent prototype demonstrating dynamic tool routing, authentication-aware state management, and human-in-the-loop approval for high-risk tool calls.

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

## Project Goal

This project is an agent engineering demo that focuses on:

1. State-driven agent behavior
2. Runtime and middleware usage
3. Safe tool execution
4. Human approval for irreversible actions
5. Interview-ready system design explanation

## Planned Roadmap

- [ ] CLI demo
- [ ] MiniMax model integration
- [ ] Authentication tool
- [ ] Inbox and send-email tools
- [ ] Dynamic middleware
- [ ] Human-in-the-loop approval
- [ ] FastAPI + SSE backend
- [ ] Simple web UI