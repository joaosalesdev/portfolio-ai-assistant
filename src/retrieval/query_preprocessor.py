"""Normalize whitespace in a validated question before retrieval."""


def preprocess_query(question):
    return " ".join(question.split())
