"""Atomically replace a document and its embedded chunks in PostgreSQL."""

from hashlib import sha256

from pgvector import Vector


def save_document(connection, document, chunks):
    sequencer = document.get("sequencer")
    if sequencer is not None:
        int(sequencer, 16)  # Reject invalid sequence numbers before writing.

    content_hash = sha256(document["text"].encode("utf-8")).hexdigest()
    with connection.transaction():
        with connection.cursor() as cursor:
            # The unique constraint serializes concurrent first inserts for this key.
            cursor.execute(
                """INSERT INTO portfolio_documents
                   (bucket, object_key, content_hash, content)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (bucket, object_key) DO NOTHING""",
                (document["bucket"], document["key"], content_hash, document["text"]),
            )
            cursor.execute(
                """SELECT id, sequencer FROM portfolio_documents
                   WHERE bucket = %s AND object_key = %s FOR UPDATE""",
                (document["bucket"], document["key"]),
            )
            document_id, previous_sequence = cursor.fetchone()
            if previous_sequence is not None:
                if sequencer is None:
                    raise ValueError("A sequenced document requires a sequenced update.")
                if int(sequencer, 16) <= int(previous_sequence, 16):
                    return False

            cursor.execute(
                """UPDATE portfolio_documents SET version_id = %s, sequencer = %s,
                   content_hash = %s, content = %s, updated_at = now() WHERE id = %s""",
                (document.get("version_id"), sequencer, content_hash, document["text"], document_id),
            )
            cursor.execute("DELETE FROM portfolio_chunks WHERE document_id = %s", (document_id,))
            for chunk in chunks:
                if any(chunk.get(key) != document.get(key)
                       for key in ("bucket", "key", "version_id", "sequencer")):
                    raise ValueError("Chunk source does not match the document.")
                if len(chunk["embedding"]) != 1536 or chunk["embedding_dimensions"] != 1536:
                    raise ValueError("Expected an embedding with 1536 dimensions.")
                cursor.execute(
                    """INSERT INTO portfolio_chunks
                       (document_id, chunk_index, start_char, end_char, content,
                        embedding_model, embedding_dimensions, embedding)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)""",
                    (document_id, chunk["chunk_index"], chunk["start_char"], chunk["end_char"],
                     chunk["text"], chunk["embedding_model"], chunk["embedding_dimensions"],
                     Vector(chunk["embedding"]).to_text()),
                )
    return True
