import cohere
import config
from retrieval.vector_search import collection

co = cohere.Client(config.COHERE_API_KEY)


def search_code(query, n_results=5):
    """
    Semantic search: finds code relevant to a natural-language query.
    """
    query_embedding = co.embed(
        texts=[query],
        model=config.EMBED_MODEL,
        input_type="search_query",
    ).embeddings[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    output = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        output.append({
            "name": meta["name"],
            "filepath": meta["filepath"],
            "start_line": meta["start_line"],
            "end_line": meta["end_line"],
            "content": doc,
        })
    return output


def get_callers(function_name, graph):
    """
    Graph lookup: what functions call this one?
    """
    if function_name not in graph:
        return f"'{function_name}' not found in the codebase graph."
    return list(graph.predecessors(function_name))


def get_callees(function_name, graph):
    """
    Graph lookup: what functions does this one call?
    """
    if function_name not in graph:
        return f"'{function_name}' not found in the codebase graph."
    return list(graph.successors(function_name))


TOOL_DEFINITIONS = [
    {
        "name": "search_code",
        "description": "Semantic search over the codebase. Use this to find code related to a concept, feature, or question — e.g. 'where is authentication handled' or 'how are emails sent'.",
        "parameter_definitions": {
            "query": {
                "description": "A natural-language description of what to search for",
                "type": "str",
                "required": True,
            }
        },
    },
    {
        "name": "get_callers",
        "description": "Find all functions that call a specific function. Use this to understand impact/blast-radius of changing a function.",
        "parameter_definitions": {
            "function_name": {
                "description": "The exact name of the function to look up",
                "type": "str",
                "required": True,
            }
        },
    },
    {
        "name": "get_callees",
        "description": "Find all functions that a specific function calls. Use this to understand what a function depends on.",
        "parameter_definitions": {
            "function_name": {
                "description": "The exact name of the function to look up",
                "type": "str",
                "required": True,
            }
        },
    },
]