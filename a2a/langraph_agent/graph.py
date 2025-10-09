from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, MessagesState, StateGraph


llm = init_chat_model("openai:gpt-4o")


class ConversationState(MessagesState):
    pass


def call_model(state: ConversationState) -> ConversationState:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(ConversationState)
graph_builder.add_node("llm", call_model)
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)

graph = graph_builder.compile()
