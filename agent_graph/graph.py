import networkx as nx
from states.state import AgentState
from agents.json_parser_agent import json_parser_agent
from agents.json_structurer_agent import json_structurer_agent
from agents.schema_comparison_agent import schema_comparison_agent


class GraphExecutor:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.state = AgentState()

        self.graph.add_node("json_parser", func=json_parser_agent)
        self.graph.add_node("json_structurer", func=json_structurer_agent)
        self.graph.add_node("schema_comparison", func=schema_comparison_agent)

        self.graph.add_edge("json_parser", "json_structurer")
        self.graph.add_edge("json_structurer", "schema_comparison")

    def execute(self, start_node="json_parser"):
        current_node = start_node
        while current_node:
            node_func = self.graph.nodes[current_node]["func"]
            response = node_func(self.state)
            self.state[current_node + "_response"] = response

            next_nodes = list(self.graph.successors(current_node))
            current_node = next_nodes[0] if next_nodes else None
