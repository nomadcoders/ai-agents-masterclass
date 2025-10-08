from langgraph.types import Command
from langchain_core.tools import tool


@tool
def transfer_to_agent(agent_name: str):
    """
    Transfer to the given agent

    Args:
        agent_name: Name of the agent to transfer to, one of: 'quiz_agent', 'teacher_agent' or 'feynman_agent'
    """
    return f"Transfer to {agent_name} completed."
    # return Command(
    #     goto=agent_name,
    #     graph=Command.PARENT,
    # )
