# AI Codebase Agent

Ask questions about a Python codebase in plain English and get answers grounded in the actual source code — not generic explanations, but answers that cite the real functions and files in that specific repo.

Point it at a GitHub repo, and ask things like:

- "How does the app authenticate API requests?"
- "What functions call `send_trial_end_soon_email`?"
- "How can an admin manually extend a user's trial?"

It answers by actually searching and reasoning over the codebase, not by guessing from general knowledge.

## Why I built this

Most "chat with your code" projects treat source code like any other document — chunk it by line count, embed it, do similarity search. That works okay for prose, but code has structure: functions call other functions, classes depend on other classes. Ignoring that structure means the assistant can find code that *sounds* related but has no idea how it actually connects to anything else.

So this project combines two retrieval strategies instead of one:
- **Semantic search** — find code related to a concept or question, even if the wording doesn't match exactly
- **Call graph traversal** — know exactly which functions call which, so questions like "what breaks if I change this?" have a real, structural answer instead of a guess

An agent decides which of these to use (or both) depending on the question, then answers using whatever it actually finds — never from memory.

## How it works

```
GitHub repo URL
      │
      ▼
  Clone locally
      │
      ▼
  Parse every function/class using Python's AST
      │
      ├──────────────┬──────────────────┐
      ▼              ▼
Build call graph   Chunk + embed each unit
(who calls whom)   (Cohere embeddings → Chroma vector DB)
      │              │
      └──────┬───────┘
             ▼
     Agent (Cohere command model)
     decides which tool(s) to use,
     gathers evidence, answers with
     citations to real files/functions
```

**Stack:** Python, Cohere (embeddings, reranking, chat/tool-use), ChromaDB (vector storage), NetworkX (call graph), Streamlit (web UI), Click (CLI).

Everything runs locally and for free — no paid infrastructure, no hosted database, just a Cohere trial key and your own machine.

## Try it

**Web demo:** [link once deployed]

**Run it yourself:**

```bash
git clone https://github.com/<your-username>/codebase-agent.git
cd codebase-agent
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file with:
```
COHERE_API_KEY=your_key_here
```

Get a free key at [dashboard.cohere.com](https://dashboard.cohere.com).

Then either use the CLI:
```bash
python cli.py index --repo https://github.com/user/repo.git
python cli.py ask "how does authentication work here?"
```

or launch the web UI:
```bash
streamlit run streamlit_app.py
```

## Evaluation

I built a 10-question test set covering different parts of a real production codebase ([SimpleLogin](https://github.com/simple-login/app), an open-source email alias service, ~1,500 indexed functions/classes) — spanning trial/subscription logic, API authentication, and custom domain management, so the eval isn't just testing one lucky code path.

Each answer is checked against the specific function names and files it should reference.

**Latest run:**
- Function accuracy: ~0.95–1.00
- File citation accuracy: ~0.75–1.00

Full breakdown per question is in `evaluation/results.md`, regenerated each time you run `python -m evaluation.run_eval`.

One thing worth calling out: these scores fluctuate a little between runs on the exact same questions, even with nothing changed. That's not a bug — it's the model itself giving slightly different phrasing each time (sometimes naming both relevant functions, sometimes only the most central one). Any project built on an LLM inherits this — worth designing around, not something you can fully eliminate.

## Known limitations

I'd rather be upfront about these than have them look like accidents.

**Call graph accuracy on common names.** The graph builder links function calls by name. If two unrelated classes both have a method called `save()` or `filter()`, the graph can't tell them apart — it doesn't track *which object* a method belongs to, only the name. This means the graph is very reliable for distinctively-named functions and less reliable for generic ones. Fixing this properly would mean adding type resolution — tracking what kind of object a variable actually is — which is closer to what a real compiler or IDE does, and was out of scope for the timeframe I had.

**Python only.** The parser uses Python's built-in `ast` module, which only understands Python syntax. Supporting other languages (JavaScript, Java, Go, etc.) would mean swapping in `tree-sitter`, which has grammars for most major languages — the rest of the pipeline (chunking, embedding, graph logic) wouldn't need to change much. This is the most natural next extension if I keep working on it.

**Public repos only, for now.** Private repo support just needs a GitHub personal access token passed into the clone step — the architecture already supports it, I just haven't wired up the auth flow in the UI yet.

**Simple evaluation scoring.** Answers are checked by looking for expected function/file names as literal text. This misses cases where the model correctly describes the right code using different wording (e.g., referring to a class name instead of a bare filename). A more thorough version would use an LLM to judge answer quality directly rather than string matching.

## What I'd do next

- Swap in `tree-sitter` for multi-language support
- Add type-aware resolution to cut down false-positive graph edges on common method names
- Expand the eval set further and add an LLM-based judge instead of pure string matching
- Add a `run_tests` tool so the agent can actually execute the repo's test suite as part of its reasoning, not just read code

## Project structure

```
codebase-agent/
├── ingestion/        # clone, parse, chunk, embed, build call graph
├── retrieval/        # vector search over the embedded codebase
├── agent/            # tools + the reasoning loop that ties it together
├── evaluation/        # test questions + scoring
├── cli.py            # command-line interface
├── streamlit_app.py  # web interface
└── config.py          # settings and secrets
```