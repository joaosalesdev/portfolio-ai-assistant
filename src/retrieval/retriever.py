"""Retrieve compatible chunks for an embedded question."""

from embeddings.embedding_service import DIMENSIONS, MODEL
from persistence.vector_repository import search_chunks


def retrieve_chunks(connection, vector, top_k=5):
    return search_chunks(connection, vector, MODEL, DIMENSIONS, top_k=top_k)
