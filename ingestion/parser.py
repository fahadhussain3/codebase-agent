import ast
import os
def parse_file(filepath):
    """
    Parses a single Python file and extracts all function and class
    definitions as structured units.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=filepath)
    units = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            unit = {
                "name": node.name,
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "filepath": filepath,
                "start_line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "docstring": ast.get_docstring(node) or "",
                "source": ast.get_source_segment(source, node),
            }
            units.append(unit)

    return units


def parse_repo(repo_path):
    """
    Walks an entire repo directory, finds all .py files,
    and parses each one into structured units.
    Returns one combined list of units across the whole repo.
    """
    all_units = []
    skip_dirs = {"venv", ".venv", "__pycache__", ".git", "node_modules", "migrations", "tests"}

    for root, dirs, files in os.walk(repo_path):
        # modifies dirs in-place so os.walk skips these folders entirely
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for filename in files:
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                try:
                    units = parse_file(filepath)
                    all_units.extend(units)
                except (SyntaxError, UnicodeDecodeError) as e:
                    print(f"Skipping {filepath}: {e}")

    return all_units