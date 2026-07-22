from ingestion.parser import parse_repo
from ingestion.graph_builder import build_call_graph
from agent.orchestrator import run_agent

units = parse_repo(r"storage/cloned_repos/app")
graph = build_call_graph(units)

answer = run_agent("How does the app notify users when their trial is ending?", graph)
print("\n=== FINAL ANSWER ===")
print(answer)


