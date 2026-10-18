"""Build bounded context from ranked chunks with traceable source identifiers."""


def select_context(matches, max_chars=6000):
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars <= 0:
        raise ValueError("max_chars must be a positive integer.")

    blocks = []
    sources = []
    seen = set()
    used = 0
    for match in matches:
        text = match["text"].strip()
        if not text:
            continue
        if match.get("document_id") is not None and match.get("chunk_index") is not None:
            identity = (match["document_id"], match["chunk_index"], match.get("version_id"))
        else:
            identity = (match["source"], match.get("version_id"), text)
        if identity in seen:
            continue
        seen.add(identity)

        source_id = f"S{len(sources) + 1}"
        block = f"[{source_id}]\n{text}"
        size = len(block) + (2 if blocks else 0)
        # Keep complete chunks; a smaller later chunk may still fit.
        if used + size > max_chars:
            continue
        blocks.append(block)
        sources.append({**match, "id": source_id})
        used += size

    return {"context": "\n\n".join(blocks), "sources": sources}
