from google.genai import types
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
from .sub_agents.content_planner.agent import content_planner_agent
from .sub_agents.asset_generator.agent import asset_generator_agent
from .sub_agents.video_assembler.agent import video_assembler_agent
from .prompt import SHORTS_PRODUCER_DESCRIPTION, SHORTS_PRODUCER_PROMPT
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

MODEL = LiteLlm(model="openai/gpt-4o")


def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
):
    # print(callback_context.agent_name)
    history = llm_request.contents
    last_message = history[-1]
    if last_message.role == "user":
        text = last_message.parts[0].text
        if "hummus" in text:
            return LlmResponse(
                content=types.Content(
                    parts=[
                        types.Part(text="Sorry I can't help with that."),
                    ],
                    role="model",
                )
            )
    return None


shorts_producer_agent = Agent(
    name="ShortsProducerAgent",
    model=MODEL,
    description=SHORTS_PRODUCER_DESCRIPTION,
    instruction=SHORTS_PRODUCER_PROMPT,
    tools=[
        AgentTool(agent=content_planner_agent),
        AgentTool(agent=asset_generator_agent),
        AgentTool(agent=video_assembler_agent),
    ],
    before_model_callback=before_model_callback,
)

root_agent = shorts_producer_agent
