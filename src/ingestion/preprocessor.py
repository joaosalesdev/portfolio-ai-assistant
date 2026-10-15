"""Normalize text while preserving Markdown code and hard line breaks."""

import re


def preprocess_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    fence = None

    for line in text.split("\n"):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            lines.append(line)
            if marker:
                run, rest = marker.groups()
                if run[0] == fence[0] and len(run) >= len(fence) and not rest.strip():
                    fence = None
            continue
        if marker:
            fence = marker.group(1)
            lines.append(line)
            continue
        if line.startswith(("    ", "\t")):
            lines.append(line)
            continue

        # Two trailing spaces represent a hard line break in Markdown.
        cleaned = line.rstrip()
        if cleaned and line.endswith("  "):
            cleaned += "  "
        if cleaned or not lines or lines[-1] != "":
            lines.append(cleaned)

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)
