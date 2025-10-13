from re import L
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

load_dotenv()

from agents import Agent, Runner


agent = Agent(
    name="Assistant",
    instructions="You help users with their questions.",
)


app = FastAPI()

client = AsyncOpenAI()


class CreateConversationResponse(BaseModel):
    conversation_id: str


@app.get("/")
def hello_world():
    return {
        "message": "hello world",
    }


@app.post("/conversations")
async def create_conversation() -> CreateConversationResponse:
    conversation = await client.conversations.create()
    return {
        "conversation_id": conversation.id,
    }


class CreateMessageInput(BaseModel):
    question: str


class CreateMessageOutput(BaseModel):
    answer: str


@app.post("/conversations/{conversation_id}/message")
async def create_message(
    conversation_id: str, message_input: CreateMessageInput
) -> CreateMessageOutput:
    answer = await Runner.run(
        starting_agent=agent,
        input=message_input.question,
        conversation_id=conversation_id,
    )
    return {
        "answer": answer.final_output,
    }


@app.post("/conversations/{conversation_id}/message-stream")
async def create_message(
    conversation_id: str, message_input: CreateMessageInput
) -> CreateMessageOutput:
    async def event_generator():
        events = Runner.run_streamed(
            starting_agent=agent,
            input=message_input.question,
            conversation_id=conversation_id,
        )
        async for event in events.stream_events():
            if (
                event.type == "raw_response_event"
                and event.data.type == "response.output_text.delta"
            ):
                yield event.data.delta

    return StreamingResponse(event_generator(), media_type="text/plain")


@app.post("/conversations/{conversation_id}/message-stream-all")
async def create_message_all(
    conversation_id: str, message_input: CreateMessageInput
) -> CreateMessageOutput:
    async def event_generator():
        events = Runner.run_streamed(
            starting_agent=agent,
            input=message_input.question,
            conversation_id=conversation_id,
        )
        async for event in events.stream_events():
            if event.type == "raw_response_event":
                yield f"{event.data.to_json()}\n"

    return StreamingResponse(event_generator(), media_type="text/plain")
