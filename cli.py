import click
from ingestion.clone import clone_repo
from ingestion.parser import parse_repo
from ingestion.chunker import chunk_units
from ingestion.embedder import embed_chunks
from ingestion.graph_builder import build_call_graph
from retrieval.vector_search import store_chunks, collection
from agent.orchestrator import run_agent


@click.group()
def cli():
    """AI Codebase Agent — ask questions about any Python GitHub repo."""
    pass


@cli.command()
@click.option("--repo", required=True, help="GitHub repo URL to index")
def index(repo):
    """Clone, parse, and index a repo (run this once per repo)."""
    click.echo(f"Cloning {repo}...")
    local_path = clone_repo(repo)

    click.echo("Parsing codebase...")
    units = parse_repo(local_path)
    click.echo(f"Found {len(units)} functions/classes.")

    click.echo("Chunking...")
    chunked = chunk_units(units)

    click.echo("Embedding (this may take a few minutes)...")
    embedded = embed_chunks(chunked)

    click.echo("Storing in vector database...")
    store_chunks(embedded)

    click.echo("Indexing complete. You can now run 'python cli.py ask'.")


@cli.command()
@click.option("--repo-path", default=r"storage/cloned_repos/app", help="Local path to the indexed repo")
@click.argument("question")
def ask(repo_path, question):
    """Ask a question about an already-indexed repo."""
    click.echo("Loading codebase graph...")
    units = parse_repo(repo_path)
    graph = build_call_graph(units)

    click.echo(f"\nQuestion: {question}\n")
    answer = run_agent(question, graph)

    click.echo("\n=== Answer ===")
    click.echo(answer)


if __name__ == "__main__":
    cli()