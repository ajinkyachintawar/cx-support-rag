from langgraph.graph import StateGraph, END

from src.agent.state import AgentState
from src.agent.nodes import query_node, retrieval_node, synthesis_node, guard_node


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("query_node", query_node)
    graph.add_node("retrieval_node", retrieval_node)
    graph.add_node("synthesis_node", synthesis_node)
    graph.add_node("guard_node", guard_node)

    graph.set_entry_point("query_node")
    graph.add_edge("query_node", "retrieval_node")
    graph.add_edge("retrieval_node", "synthesis_node")
    graph.add_edge("synthesis_node", "guard_node")
    graph.add_edge("guard_node", END)

    return graph.compile()
