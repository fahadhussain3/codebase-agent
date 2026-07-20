from retrieval.vector_search import collection
import cohere
import config

co = cohere.Client(config.COHERE_API_KEY)

query = "send an email to users when their trial is ending"

query_embedding = co.embed(
    texts=[query],
    model=config.EMBED_MODEL,
    input_type="search_query",
).embeddings[0]

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
)

for name, filepath in zip(
    [m["name"] for m in results["metadatas"][0]],
    [m["filepath"] for m in results["metadatas"][0]],
):
    print(name, "-", filepath)