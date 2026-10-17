"""Split normalized documents into bounded chunks with source metadata."""


def chunk_document(document, max_chars=1000):
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars <= 0:
        raise ValueError("max_chars must be a positive integer.")

    text = document["text"]
    if not text.strip():
        return []

    metadata = {key: value for key, value in document.items() if key != "text"}
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            # Prefer paragraph boundaries, then whitespace, then a hard cut.
            paragraph = text.rfind("\n\n", start, end)
            if paragraph > start:
                end = paragraph + 2
            else:
                for position in range(end - 1, start, -1):
                    if text[position].isspace():
                        end = position + 1
                        break

        chunks.append({
            **metadata,
            "chunk_index": len(chunks),
            "start_char": start,
            "end_char": end,
            "text": text[start:end],
        })
        start = end

    return chunks
