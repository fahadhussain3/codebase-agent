import cohere
import config
from agent.tools import search_code, get_callers, get_callees, TOOL_DEFINITIONS

co = cohere.Client(config.COHERE_API_KEY)

# maps tool names (strings) to the actual Python functions that do the work
TOOL_FUNCTIONS = {
    "search_code": search_code,
    "get_callers": get_callers,
    "get_callees": get_callees,
}

SYSTEM_PROMPT = """You are a codebase assistant. You answer questions about a
specific codebase using the tools available to you. Always use tools to gather
evidence before answering — never guess or make up function names or file paths.
When you give a final answer, mention the specific file(s) and function name(s)
you used as evidence."""


def run_agent(question, graph, max_iterations=6):
    """
    Runs the ReAct-style reasoning loop: the model decides which tools to call,
    tools are executed, results are fed back, until a final answer is produced.
    """
    chat_history = []
    current_message = question

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        response = co.chat(
            message=current_message,
            chat_history=chat_history,
            preamble=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
        )

        if not response.tool_calls:
            print("Model gave a final answer.")
            return response.text

        chat_history.append({"role": "USER", "message": current_message})
        chat_history.append({"role": "CHATBOT", "message": response.text or "", "tool_calls": response.tool_calls})

        tool_results = []
        for call in response.tool_calls:
            print(f"Model wants to call: {call.name} with {call.parameters}")

            func = TOOL_FUNCTIONS.get(call.name)
            if func is None:
                result = f"Unknown tool: {call.name}"
            else:
                if call.name in ("get_callers", "get_callees"):
                    result = func(call.parameters.get("function_name"), graph)
                else:
                    result = func(**call.parameters)

            tool_results.append({
                "call": call,
                "outputs": [{"result": str(result)}],
            })

        current_message = ""
        response = co.chat(
            message=current_message,
            chat_history=chat_history,
            preamble=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            tool_results=tool_results,
        )

        if not response.tool_calls:
            return response.text

        chat_history.append({"role": "USER", "message": ""})
        chat_history.append({"role": "CHATBOT", "message": response.text or "", "tool_calls": response.tool_calls})

    return "I wasn't able to fully answer within the allowed reasoning steps. Try rephrasing your question."