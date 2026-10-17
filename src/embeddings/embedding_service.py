"""Generate OpenAI embeddings in small batches, preserving chunk metadata."""

MODEL = "text-embedding-3-small"
DIMENSIONS = 1536
BATCH_SIZE = 32


def embed_chunks(client, chunks):
    embedded = []
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        if any(not chunk["text"].strip() for chunk in batch):
            raise ValueError("Embedding input must not be empty.")

        response = client.embeddings.create(
            model=MODEL,
            dimensions=DIMENSIONS,
            input=[chunk["text"] for chunk in batch],
            encoding_format="float",
        )
        results = sorted(response.data, key=lambda item: item.index)
        if [item.index for item in results] != list(range(len(batch))):
            raise ValueError("Embedding response does not match the input batch.")
        for chunk, result in zip(batch, results):
            if len(result.embedding) != DIMENSIONS:
                raise ValueError("Unexpected embedding dimension.")
            embedded.append({
                **chunk,
                "embedding": result.embedding,
                "embedding_model": MODEL,
                "embedding_dimensions": DIMENSIONS,
            })
    return embedded
