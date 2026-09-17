from dataclasses import replace

import pytest

from portfolio_ai.ingestion.models import DocumentSource
from portfolio_ai.ingestion.service import PrepareDocument


class StubLoader:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls = 0

    def load(self, source: DocumentSource) -> str:
        self.calls += 1
        return self.text


@pytest.fixture
def source() -> DocumentSource:
    return DocumentSource("example/readme", "Exemplo fictício", "example", True)


def test_unapproved_source_is_rejected_before_reading(source):
    loader = StubLoader("Texto")
    with pytest.raises(ValueError, match="not approved"):
        PrepareDocument(loader).execute(replace(source, approved_for_publication=False))
    assert loader.calls == 0


def test_sources_are_not_approved_by_default():
    assert not DocumentSource("example", "Exemplo", "example").approved_for_publication


@pytest.mark.parametrize("text", ["", "  ", "\r\n\t"])
def test_empty_documents_are_rejected(source, text):
    with pytest.raises(ValueError, match="empty"):
        PrepareDocument(StubLoader(text)).execute(source)


def test_line_endings_do_not_change_hash_and_markdown_is_preserved(source):
    markdown = "# Exemplo\n\n    código indentado\nlinha com quebra explícita  \n"
    unix = PrepareDocument(StubLoader(markdown)).execute(source)
    windows = PrepareDocument(StubLoader(markdown.replace("\n", "\r\n"))).execute(source)
    assert windows.content == markdown
    assert unix.content_hash == windows.content_hash
    assert windows.source == source


def test_changed_content_changes_hash_without_changing_source_identity(source):
    before = PrepareDocument(StubLoader("Versão A")).execute(source)
    after = PrepareDocument(StubLoader("Versão B")).execute(source)
    assert before.content_hash != after.content_hash
    assert before.source.source_key == after.source.source_key


def test_loader_failure_is_not_reported_as_success(source):
    class FailingLoader:
        def load(self, source: DocumentSource) -> str:
            raise OSError("Read failed")

    with pytest.raises(OSError, match="Read failed"):
        PrepareDocument(FailingLoader()).execute(source)


@pytest.mark.parametrize("field", ["source_key", "title", "project"])
def test_blank_metadata_is_rejected(source, field):
    with pytest.raises(ValueError, match="metadata"):
        replace(source, **{field: " "})
