"""Objetos de dados sem dependência de SDKs ou persistência."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DocumentSource:
    """Metadata de uma fonte; aprovação deverá vir do manifesto administrativo."""

    source_key: str
    title: str
    project: str
    approved_for_publication: bool = False

    def __post_init__(self) -> None:
        for field in (self.source_key, self.title, self.project):
            if not field.strip():
                raise ValueError("Source metadata must not be blank")


@dataclass(frozen=True, slots=True)
class PreparedDocument:
    source: DocumentSource
    content: str
    content_hash: str
