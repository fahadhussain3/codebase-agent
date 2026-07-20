import time
import cohere
import config

co = cohere.Client(config.COHERE_API_KEY)


def embed_chunks(chunks, batch_size=90, delay_seconds=20):
    """
    Takes a list of chunks and returns them with an 'embedding' field added.
    Sends texts to Cohere in batches, pausing between calls and retrying
    automatically if the trial rate limit is hit.
    """
    texts = [chunk["chunk_text"] for chunk in chunks]
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"Embedding batch {i} to {i + len(batch)} of {len(texts)}...")

        response = embed_with_retry(batch)
        all_embeddings.extend(response.embeddings)

        time.sleep(delay_seconds)

    for chunk, embedding in zip(chunks, all_embeddings):
        chunk["embedding"] = embedding

    return chunks


def embed_with_retry(batch, max_retries=5):
    """
    Calls Cohere's embed API, automatically waiting and retrying
    if the rate limit is hit.
    """
    for attempt in range(max_retries):
        try:
            return co.embed(
                texts=batch,
                model=config.EMBED_MODEL,
                input_type="search_document",
            )
        except cohere.errors.too_many_requests_error.TooManyRequestsError:
            wait_time = 30 * (attempt + 1)
            print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)

    raise RuntimeError("Failed to embed batch after multiple retries.")