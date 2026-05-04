import asyncio
import json

from claude_agent_sdk import (
    AgentDefinition,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ResultMessage,
    StreamEvent,
)
from claude_agent_sdk.types import HookContext, HookInput
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

load_dotenv()

app = FastAPI()


# Researcher subagent — returns its findings as text, no file I/O.
researcher = AgentDefinition(
    description="Researches a subtopic using web search and fetches sources.",
    prompt=(
        "You are a research assistant. Given a subtopic, use WebSearch to find "
        "2-3 relevant, recent sources. Use WebFetch to read each source. "
        "Then return your findings as a concise markdown report with key facts, "
        "direct quotes where relevant, and source URLs. "
        "Do NOT write to any files. Limit yourself to 3 WebSearch calls maximum."
    ),
    tools=["WebSearch", "WebFetch"],
    permissionMode="acceptEdits",
    maxTurns=15,
)


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/events")
async def events(topic: str):
    """SSE endpoint. Runs the research agent and streams semantic events."""

    queue = asyncio.Queue()

    # ---- Hooks: push semantic events onto the queue ----
    # The SDK calls every hook with the same `HookInput` union type, so the
    # narrow per-event types (PreToolUseHookInput, etc.) don't fit `HookCallback`.
    # We widen to `HookInput` and pull fields with `.get()`.
    async def on_pre_tool(input_data: HookInput, tool_use_id, context):
        tool = input_data.get("tool_name", "")
        inp = input_data.get("tool_input", {})
        origin = input_data.get("agent_type", "main")  # subagent name, or "main"

        if tool == "WebSearch":
            await queue.put({"type": "search", "origin": origin, "value": inp.get("query", "")})
        elif tool == "WebFetch":
            await queue.put({"type": "fetch", "origin": origin, "value": inp.get("url", "")})
        elif tool == "Write":
            await queue.put({"type": "write", "origin": origin, "value": inp.get("file_path", "")})
        elif tool == "Agent":
            await queue.put({"type": "spawn", "origin": origin, "value": inp.get("description", "")})
        elif tool == "TodoWrite":
            await queue.put({"type": "todos", "origin": origin, "todos": inp.get("todos", [])})
        else:
            await queue.put({"type": "tool", "origin": origin, "value": tool})

        return {}

    async def on_subagent_start(input_data: HookInput, tool_use_id, context):
        await queue.put(
            {"type": "subagent_started", "value": input_data.get("agent_type", "")}
        )
        return {}

    # ---- Agent setup ----
    options = ClaudeAgentOptions(
        agents={"researcher": researcher},
        allowed_tools=["Agent"],
        permission_mode="acceptEdits",
        max_turns=20,
        include_partial_messages=True,  # opt into token-by-token deltas
        hooks={
            "PreToolUse": [HookMatcher(matcher=".*", hooks=[on_pre_tool])],
            "SubagentStart": [HookMatcher(matcher=None, hooks=[on_subagent_start])],
        },
    )

    prompt = f"""Research the topic: "{topic}"

First, use the `TodoWrite` tool to lay out your plan as a todo list (one item
per subtopic plus a final "synthesize summary" item). Update the todo list as
you progress: mark items `in_progress` when you start them and `completed`
when done.

Steps:
1. Break the topic into 2 subtopics.
2. Spawn one `researcher` subagent per subtopic. Pass each a task like:
   "Research [subtopic] and report your findings."
3. After both finish, synthesize their findings into a final markdown summary.
   The summary should have: an intro paragraph, key findings as bullets, and sources.

Output the final summary as your last message. Do NOT write to any files.
"""

    # ---- Agent task: forwards token-level deltas + result ----
    async def run_agent():
        block_id = 0  # unique id per text block, so the browser groups deltas
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for message in client.receive_response():
                if isinstance(message, StreamEvent):
                    origin = "subagent" if message.parent_tool_use_id else "main"
                    e = message.event
                    etype = e.get("type")

                    if etype == "content_block_start":
                        if e.get("content_block", {}).get("type") == "text":
                            block_id += 1
                            await queue.put(
                                {
                                    "type": "thinking_start",
                                    "origin": origin,
                                    "id": block_id,
                                }
                            )

                    elif etype == "content_block_delta":
                        delta = e.get("delta", {})
                        if delta.get("type") == "text_delta":
                            await queue.put(
                                {
                                    "type": "thinking_delta",
                                    "origin": origin,
                                    "id": block_id,
                                    "value": delta.get("text", ""),
                                }
                            )

                elif isinstance(message, ResultMessage):
                    if message.result:
                        await queue.put(
                            {"type": "summary", "value": message.result}
                        )
                    await queue.put(
                        {
                            "type": "done",
                            "turns": message.num_turns,
                            "duration_ms": message.duration_ms,
                        }
                    )
        await queue.put(None)  # sentinel

    # ---- SSE stream: drain the queue until the sentinel ----
    async def stream():
        agent_task = asyncio.create_task(run_agent())
        try:
            while (event := await queue.get()) is not None:
                yield {"data": json.dumps(event)}
        finally:
            if not agent_task.done():
                agent_task.cancel()

    return EventSourceResponse(stream())
