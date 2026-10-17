-- Run once in the database where the vector extension is already enabled.
BEGIN;

CREATE TABLE IF NOT EXISTS portfolio_documents (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bucket text NOT NULL,
    object_key text NOT NULL,
    version_id text,
    sequencer text,
    content_hash text NOT NULL,
    content text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (bucket, object_key)
);

CREATE TABLE IF NOT EXISTS portfolio_chunks (
    document_id bigint NOT NULL REFERENCES portfolio_documents(id) ON DELETE CASCADE,
    chunk_index integer NOT NULL CHECK (chunk_index >= 0),
    start_char integer NOT NULL CHECK (start_char >= 0),
    end_char integer NOT NULL CHECK (end_char > start_char),
    content text NOT NULL,
    embedding_model text NOT NULL,
    embedding_dimensions integer NOT NULL CHECK (embedding_dimensions = 1536),
    embedding vector(1536) NOT NULL,
    PRIMARY KEY (document_id, chunk_index)
);

COMMIT;
