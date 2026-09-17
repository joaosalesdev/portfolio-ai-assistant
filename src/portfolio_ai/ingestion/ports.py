"""Contratos pequenos para dependências externas do serviço."""

from typing import Protocol

from portfolio_ai.ingestion.models import DocumentSource


class DocumentLoader(Protocol):
    def load(self, source: DocumentSource) -> str:
        """Lê texto de uma fonte selecionada; propaga falhas de leitura."""
        ...
