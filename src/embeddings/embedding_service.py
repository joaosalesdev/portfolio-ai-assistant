"""Generate OpenAI embeddings in small batches, preserving chunk metadata."""

MODEL = "text-embedding-3-small"
DIMENSIONS = 1536
BATCH_SIZE = 32


def _embed_texts(client, texts):
    vectors = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        if any(not isinstance(text, str) or not text.strip() for text in batch):
            raise ValueError("Embedding input must not be empty.")

        response = client.embeddings.create(
            model=MODEL,
            dimensions=DIMENSIONS,
            input=batch,
            encoding_format="float",
        )
        results = sorted(response.data, key=lambda item: item.index)
        if [item.index for item in results] != list(range(len(batch))):
            raise ValueError("Embedding response does not match the input batch.")
        for result in results:
            if len(result.embedding) != DIMENSIONS:
                raise ValueError("Unexpected embedding dimension.")
            vectors.append(result.embedding)
    return vectors


def embed_query(client, question):
    """Generate a question vector using the same configuration as documents."""
    return _embed_texts(client, [question])[0]


def embed_chunks(client, chunks):
    vectors = _embed_texts(client, [chunk["text"] for chunk in chunks])
    return [{
        **chunk,
        "embedding": vector,
        "embedding_model": MODEL,
        "embedding_dimensions": DIMENSIONS,
    } for chunk, vector in zip(chunks, vectors)]
