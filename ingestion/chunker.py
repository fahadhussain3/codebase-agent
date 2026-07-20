def create_chunk_text(unit):
    """
    Builds a single clean text block for one function/class,
    combining metadata + docstring + source code.
    This is the exact text that will get embedded.
    """
    parts = []

    parts.append(f"{unit['type'].upper()}: {unit['name']}")
    parts.append(f"File: {unit['filepath']}")

    if unit["docstring"]:
        parts.append(f"Docstring: {unit['docstring']}")

    if unit["source"]:
        parts.append(f"Code:\n{unit['source']}")

    return "\n".join(parts)


def chunk_units(units):
    """
    Takes the full list of parsed units and attaches a
    ready-to-embed 'chunk_text' field to each one.
    """
    chunked = []

    for unit in units:
        chunk_text = create_chunk_text(unit)
        unit_with_chunk = dict(unit)  # copy, so we don't mutate the original
        unit_with_chunk["chunk_text"] = chunk_text
        chunked.append(unit_with_chunk)

    return chunked