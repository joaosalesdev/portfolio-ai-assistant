"""Essential question preprocessing tests."""

from retrieval.query_preprocessor import preprocess_query


def test_normalize_whitespace():
    assert preprocess_query("  Quais\r\n\toportunidades   em\u00a0Portugal?  ") == "Quais oportunidades em Portugal?"


def test_preserve_case_accents_and_punctuation():
    question = "João usa C++ e Python? E AWS/Lambda?"
    assert preprocess_query(question) == question


def test_normalization_is_idempotent():
    question = preprocess_query("\nExperiência   com AWS?\n")
    assert preprocess_query(question) == question
