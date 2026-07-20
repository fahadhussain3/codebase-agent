import ast
import networkx as nx

def extract_calls(source_code):
    """
    Given a function/class's source code, returns the names of
    all functions it calls inside its body.
    """
    calls = set()
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return calls

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)

    return calls

def build_call_graph(units):
    """
    Builds a directed graph: node = function/class name,
    edge = "this function calls that function".
    """
    graph = nx.DiGraph()

    # first pass: add every unit as a node, with metadata attached
    for unit in units:
        graph.add_node(
            unit["name"],
            type=unit["type"],
            filepath=unit["filepath"],
            start_line=unit["start_line"],
            end_line=unit["end_line"],
        )

    # build a lookup so we only link calls to names we actually parsed
    known_names = {unit["name"] for unit in units}

    # second pass: find calls inside each unit, add edges
    for unit in units:
        if not unit["source"]:
            continue
        called_names = extract_calls(unit["source"])
        for called in called_names:
            if called in known_names and called != unit["name"]:
                graph.add_edge(unit["name"], called)

    return graph