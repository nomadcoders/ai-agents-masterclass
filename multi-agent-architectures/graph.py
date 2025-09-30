from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model


class AgentsState(MessagesState):
    current_agent: str
    transfered_by: str


llm = init_chat_model("openai:gpt-4o")


def make_agent(prompt, tools):

    def agent_node(state: AgentsState):
        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(
            f"""
        {prompt}

        You have a tool called 'handoff_tool' use it to transfer to other agent, don't use it to transfer to yourself.

        Conversation History:
        {state["messages"]}
        """
        )
        return {"messages": [response]}

    agent_builder = StateGraph(AgentsState)

    agent_builder.add_node("agent", agent_node)
    agent_builder.add_node(
        "tools",
        ToolNode(tools=tools),
    )

    agent_builder.add_edge(START, "agent")
    agent_builder.add_conditional_edges("agent", tools_condition)
    agent_builder.add_edge("tools", "agent")
    agent_builder.add_edge("agent", END)

    return agent_builder.compile()


@tool
def handoff_tool(transfer_to: str, transfered_by: str):
    """
    Handoff to another agent.

    Use this tool when the customer speaks a language that you don't understand.

    Possible values for `transfer_to`:
    - `korean_agent`
    - `greek_agent`
    - `spanish_agent`

    Possible values for `transfered_by`:
    - `korean_agent`
    - `greek_agent`
    - `spanish_agent`

    Args:
        transfer_to: The agent to transfer the conversation to
        transfered_by: The agent that transferred the conversation
    """
    if transfer_to == transfered_by:
        return {
            "error": "Stop trying to transfer to yourself and answer the question or i will fire you."
        }

    return Command(
        update={
            "current_agent": transfer_to,
            "transfered_by": transfered_by,
        },
        goto=transfer_to,
        graph=Command.PARENT,
    )


graph_builder = StateGraph(AgentsState)

graph_builder.add_node(
    "korean_agent",
    make_agent(
        prompt="You're a Korean customer support agent. You only speak and understand Korean.",
        tools=[handoff_tool],
    ),
    destinations=("greek_agent", "spanish_agent"),
)
graph_builder.add_node(
    "greek_agent",
    make_agent(
        prompt="You're a Greek customer support agent. You only speak and understand Greek.",
        tools=[handoff_tool],
    ),
    destinations=("korean_agent", "spanish_agent"),
)
graph_builder.add_node(
    "spanish_agent",
    make_agent(
        prompt="You're a Spanish customer support agent. You only speak and understand Spanish.",
        tools=[handoff_tool],
    ),
    destinations=("greek_agent", "korean_agent"),
)

graph_builder.add_edge(START, "korean_agent")

graph = graph_builder.compile()
