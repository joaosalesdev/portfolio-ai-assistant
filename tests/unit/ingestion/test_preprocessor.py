"""Essential text normalization tests."""

from ingestion.preprocessor import preprocess_text


def test_normalize_whitespace():
    assert preprocess_text("\r\nTitle\t\r\n\r\n\r\nText\r\n") == "Title\n\nText"
    assert preprocess_text("  \n\t\n") == ""


def test_preserve_markdown_and_code():
    text = '# Experiência\n\n- AWS\n  - Python\nLine  \nNext\n\n```python\n    x = "  "  \n\n\n```'
    assert preprocess_text(text) == text


def test_preserve_indented_code_and_tilde_fences():
    text = '    x = 1  \n\n~~~text\nvalue  \n\n\n~~~'
    assert preprocess_text(text) == text


def test_normalization_is_idempotent():
    text = "\nTitle\t\n\n\nText\n"
    normalized = preprocess_text(text)
    assert preprocess_text(normalized) == normalized
