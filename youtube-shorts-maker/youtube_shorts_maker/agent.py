from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
from .sub_agents.content_planner.agent import content_planner_agent
from .prompt import SHORTS_PRODUCER_DESCRIPTION, SHORTS_PRODUCER_PROMPT

MODEL = LiteLlm(model="openai/gpt-4o")

shorts_producer_agent = Agent(
    name="ShortsProducerAgent",
    model=MODEL,
    description=SHORTS_PRODUCER_DESCRIPTION,
    instruction=SHORTS_PRODUCER_PROMPT,
    tools=[
        AgentTool(agent=content_planner_agent),
    ],
)

root_agent = shorts_producer_agent
