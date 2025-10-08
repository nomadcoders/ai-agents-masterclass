from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import START, END, StateGraph, MessagesState

from agents.classification_agent import classification_agent


class TutorState(MessagesState):
    pass


graph_builder = StateGraph(TutorState)

graph_builder.add_node("classification_agent", classification_agent)

graph_builder.add_edge(START, "classification_agent")
graph_builder.add_edge("classification_agent", END)

graph = graph_builder.compile()
