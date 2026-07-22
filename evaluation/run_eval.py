import json
from ingestion.parser import parse_repo
from ingestion.graph_builder import build_call_graph
from agent.orchestrator import run_agent


def load_questions(path="evaluation/test_questions.json"):
    with open(path, "r") as f:
        return json.load(f)


def score_answer(answer_text, expected_functions, expected_files):
    """
    Simple automated check: does the answer text mention the
    expected function names and file names?
    """
    normalized_answer = answer_text.replace("\\", "/")

    found_functions = [fn for fn in expected_functions if fn in answer_text]
    found_files = [fp for fp in expected_files if fp.replace("\\", "/") in normalized_answer]

    function_score = len(found_functions) / len(expected_functions) if expected_functions else 1
    file_score = len(found_files) / len(expected_files) if expected_files else 1

    return {
        "function_score": function_score,
        "file_score": file_score,
        "found_functions": found_functions,
        "found_files": found_files,
    }


def run_evaluation():
    questions = load_questions()
    units = parse_repo(r"storage/cloned_repos/app")
    graph = build_call_graph(units)

    results = []

    for q in questions:
        print(f"\n=== Question {q['id']}: {q['question']} ===")
        answer = run_agent(q["question"], graph)
        score = score_answer(answer, q["expected_functions"], q["expected_files"])

        results.append({
            "id": q["id"],
            "question": q["question"],
            "answer": answer,
            "score": score,
        })

        print(f"Function score: {score['function_score']:.2f}")
        print(f"File score: {score['file_score']:.2f}")

    avg_function_score = sum(r["score"]["function_score"] for r in results) / len(results)
    avg_file_score = sum(r["score"]["file_score"] for r in results) / len(results)

    print(f"\n=== OVERALL ===")
    print(f"Average function score: {avg_function_score:.2f}")
    print(f"Average file score: {avg_file_score:.2f}")

    save_report(results, avg_function_score, avg_file_score)


def save_report(results, avg_function_score, avg_file_score):
    with open("evaluation/results.md", "w", encoding="utf-8") as f:
        f.write("# Evaluation Results\n\n")
        f.write(f"**Average function score:** {avg_function_score:.2f}\n\n")
        f.write(f"**Average file score:** {avg_file_score:.2f}\n\n")
        f.write("---\n\n")

        for r in results:
            f.write(f"## Q{r['id']}: {r['question']}\n\n")
            f.write(f"**Answer:**\n{r['answer']}\n\n")
            f.write(f"**Function score:** {r['score']['function_score']:.2f} "
                     f"(found: {r['score']['found_functions']})\n\n")
            f.write(f"**File score:** {r['score']['file_score']:.2f} "
                     f"(found: {r['score']['found_files']})\n\n")
            f.write("---\n\n")

    print("\nReport saved to evaluation/results.md")


if __name__ == "__main__":
    run_evaluation()