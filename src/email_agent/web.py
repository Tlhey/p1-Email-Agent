from __future__ import annotations

import asyncio
import concurrent.futures
import json
import os
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from langchain.messages import HumanMessage
from langchain_core.messages import AIMessageChunk
from langgraph.types import Command
from pydantic import BaseModel

from email_agent.agent import build_agent


app = FastAPI(title="Email Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_agent = build_agent()
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
_static_dir = os.path.join(os.path.dirname(__file__), "static")


class MessageRequest(BaseModel):
    message: str


class ResumeRequest(BaseModel):
    decision: dict[str, Any]


def _to_json_safe(data: Any) -> Any:
    return json.loads(json.dumps(data, default=str))


def _sse(event: str, data: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _extract_interrupt(data: Any) -> Any | None:
    if not isinstance(data, dict):
        return None
    if "__interrupt__" in data:
        return data["__interrupt__"]
    if "interrupts" in data:
        return data["interrupts"]
    return None


def _format_rejection(decision: dict[str, Any]) -> dict[str, Any]:
    if decision.get("type") == "reject":
        raw = decision.get("message", "未提供原因")
        return {
            **decision,
            "message": (
                f"[REJECTED] 该操作已被用户拒绝，邮件未发送。\n"
                f"原因：{raw}\n"
                f"请告知用户操作已被取消，不要重试。"
            ),
        }
    return decision


async def _run_agent_sse(
    payload: Any,
    config: dict,
) -> AsyncGenerator[str, None]:
    loop = asyncio.get_event_loop()
    queue: asyncio.Queue[tuple[str, Any] | None] = asyncio.Queue()

    def run() -> None:
        try:
            for chunk in _agent.stream(
                payload,
                config=config,
                stream_mode=["messages", "updates"],
                version="v2",
            ):
                chunk_type = chunk.get("type")
                data = chunk.get("data")

                if chunk_type == "messages":
                    try:
                        token, _ = data
                    except Exception:
                        continue

                    # Only forward AI-generated text, skip ToolMessage / HumanMessage
                    if not isinstance(token, AIMessageChunk):
                        continue

                    content = getattr(token, "content", "")
                    if content:
                        loop.call_soon_threadsafe(
                            queue.put_nowait,
                            ("token", {"content": content}),
                        )

                elif chunk_type == "updates":
                    interrupt_data = _extract_interrupt(data)
                    if interrupt_data is not None:
                        loop.call_soon_threadsafe(
                            queue.put_nowait,
                            ("interrupt", _to_json_safe(interrupt_data)),
                        )

        except Exception as e:
            loop.call_soon_threadsafe(
                queue.put_nowait,
                ("error", {"message": str(e)}),
            )
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    loop.run_in_executor(_executor, run)

    while True:
        item = await queue.get()
        if item is None:
            yield _sse("done", {})
            break
        event, data = item
        yield _sse(event, data)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_ui() -> FileResponse:
    return FileResponse(os.path.join(_static_dir, "index.html"))


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/threads/{thread_id}/state")
async def get_state(thread_id: str) -> dict:
    """Debug: inspect current state for a thread."""
    config = {"configurable": {"thread_id": thread_id}}
    state = await asyncio.get_event_loop().run_in_executor(
        _executor, lambda: _agent.get_state(config)
    )
    return _to_json_safe({"values": state.values, "next": state.next})


@app.post("/threads/{thread_id}/messages")
async def send_message(thread_id: str, req: MessageRequest) -> StreamingResponse:
    print(f"[msg] thread={thread_id!r}  message={req.message!r}")
    config = {"configurable": {"thread_id": thread_id}}
    payload = {"messages": [HumanMessage(content=req.message)]}
    return StreamingResponse(
        _run_agent_sse(payload, config),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/threads/{thread_id}/resume")
async def resume_after_interrupt(thread_id: str, req: ResumeRequest) -> StreamingResponse:
    print(f"[resume] thread={thread_id!r}  decision={req.decision!r}")
    config = {"configurable": {"thread_id": thread_id}}
    decision = _format_rejection(req.decision)
    payload = Command(resume={"decisions": [decision]})
    return StreamingResponse(
        _run_agent_sse(payload, config),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("email_agent.web:app", host="0.0.0.0", port=8000, reload=True)
