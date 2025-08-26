from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import PROMPT_BUILDER_DESCRIPTION, PROMPT_BUILDER_PROMPT
from pydantic import BaseModel, Field
from typing import List

MODEL = LiteLlm(model="openai/gpt-4o")


class OptimizedPrompt(BaseModel):
    scene_id: int = Field(description="Scene ID from the original content plan")
    enhanced_prompt: str = Field(
        description="Detailed prompt with technical specs and text overlay instructions for vertical YouTube Shorts"
    )


class PromptBuilderOutput(BaseModel):
    optimized_prompts: List[OptimizedPrompt] = Field(
        description="Array of optimized image generation prompts for vertical YouTube Shorts"
    )


prompt_builder_agent = Agent(
    name="PromptBuilderAgent",
    description=PROMPT_BUILDER_DESCRIPTION,
    instruction=PROMPT_BUILDER_PROMPT,
    model=MODEL,
    output_schema=PromptBuilderOutput,
    output_key="prompt_builder_output",
)
