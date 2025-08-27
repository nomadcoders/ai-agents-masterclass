from google.adk.agents import Agent, LoopAgent
from google.adk.models.lite_llm import LiteLlm
from .prompt import (
    EMAIL_OPTIMIZER_DESCRIPTION,
    TONE_STYLIST_DESCRIPTION,
    CLARITY_EDITOR_DESCRIPTION,
    LITERARY_CRITIC_DESCRIPTION,
    EMAIL_SYNTHESIZER_DESCRIPTION,
    PERSUASION_STRATEGIST_DESCRIPTION,
    TONE_STYLIST_INSTRUCTION,
    CLARITY_EDITOR_INSTRUCTION,
    LITERARY_CRITIC_INSTRUCTION,
    EMAIL_SYNTHESIZER_INSTRUCTION,
    PERSUASION_STRATEGIST_INSTRUCTION,
)

MODEL = LiteLlm(model="openai/gpt-4o-mini")

clarity_agent = Agent(
    name="ClarityEditorAgent",
    description=CLARITY_EDITOR_DESCRIPTION,
    instruction=CLARITY_EDITOR_INSTRUCTION,
)

tone_stylist_agent = Agent(
    name="ToneStylistAgent",
    description=TONE_STYLIST_DESCRIPTION,
    instruction=TONE_STYLIST_INSTRUCTION,
)

persuation_agent = Agent(
    name="PersuationAgent",
    description=PERSUASION_STRATEGIST_DESCRIPTION,
    instruction=PERSUASION_STRATEGIST_INSTRUCTION,
)

email_synthesizer_agent = Agent(
    name="EmailSynthesizerAgent",
    description=EMAIL_SYNTHESIZER_DESCRIPTION,
    instruction=EMAIL_SYNTHESIZER_INSTRUCTION,
)

literary_critic_agent = Agent(
    name="LiteraryCriticAgent",
    description=LITERARY_CRITIC_DESCRIPTION,
    instruction=LITERARY_CRITIC_INSTRUCTION,
)
