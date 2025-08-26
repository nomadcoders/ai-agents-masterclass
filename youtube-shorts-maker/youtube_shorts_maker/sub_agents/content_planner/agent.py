from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import CONTENT_PLANNER_DESCRIPTION, CONTENT_PLANNER_PROMPT
from pydantic import BaseModel, Field
from typing import List


class SceneOutput(BaseModel):
    id: int = Field(description="Scene ID number")
    narration: str = Field(description="Narration text for the scene")
    visual_description: str = Field(
        description="Detailed description for image generation"
    )
    embedded_text: str = Field(
        description="Text overlay for the image (can be any case/style)"
    )
    embedded_text_location: str = Field(
        description="Where to position the text on the image (e.g., 'top center', 'bottom left', 'middle right', 'center')"
    )
    duration: int = Field(description="Duration in seconds for this scene")


class ContentPlanOutput(BaseModel):
    topic: str = Field(description="The topic of the YouTube Short")
    total_duration: int = Field(description="Total video duration in seconds (max 20)")
    scenes: List[SceneOutput] = Field(
        description="List of scenes (agent decides how many)"
    )


MODEL = LiteLlm(model="openai/gpt-4o")

content_planner_agent = Agent(
    name="ContentPlannerAgent",
    description=CONTENT_PLANNER_DESCRIPTION,
    instruction=CONTENT_PLANNER_PROMPT,
    model=MODEL,
    output_schema=ContentPlanOutput,
    output_key="content_planner_output",
)
