"""Primeiro passo da ingestão: aprovação, leitura, normalização e hash."""

from hashlib import sha256

from portfolio_ai.ingestion.models import DocumentSource, PreparedDocument
from portfolio_ai.ingestion.ports import DocumentLoader


class PrepareDocument:
    def __init__(self, loader: DocumentLoader) -> None:
        self._loader = loader

    def execute(self, source: DocumentSource) -> PreparedDocument:
        if not source.approved_for_publication:
            raise ValueError("Source is not approved for publication")

        raw_content = self._loader.load(source)
        # Preserva indentação, parágrafos e espaços significativos do Markdown.
        content = raw_content.replace("\r\n", "\n").replace("\r", "\n")
        if not content.strip():
            raise ValueError("Document must not be empty")

        return PreparedDocument(
            source=source,
            content=content,
            content_hash=sha256(content.encode("utf-8")).hexdigest(),
        )
