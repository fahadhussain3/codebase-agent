import chromadb
import config

client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
collection = client.get_or_create_collection(name="codebase")


def store_chunks(chunks):
    """
    Saves embedded chunks into the local Chroma vector database.
    """
    ids = [f"{chunk['filepath']}::{chunk['name']}::{chunk['start_line']}" for chunk in chunks]
    embeddings = [chunk["embedding"] for chunk in chunks]
    documents = [chunk["chunk_text"] for chunk in chunks]
    metadatas = [
        {
            "name": chunk["name"],
            "type": chunk["type"],
            "filepath": chunk["filepath"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"Stored {len(chunks)} chunks in Chroma.")