#!/usr/bin/env python3

import argparse
import re
from pathlib import Path
from typing import List


# ----------------------------
# Title normalization logic
# ----------------------------

ACRONYM_RE = re.compile(r"[A-Z]{2,}")

def split_camel_and_acronyms(text: str) -> List[str]:
    """
    Split a string into semantic tokens:
    - Preserve acronyms (HTML, URL)
    - Split CamelCase words
    """
    tokens = []
    buf = ""

    i = 0
    while i < len(text):
        # Acronym
        m = ACRONYM_RE.match(text, i)
        if m:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(m.group())
            i = m.end()
            continue

        c = text[i]
        if c.isupper():
            if buf and not buf[-1].isupper():
                tokens.append(buf)
                buf = c
            else:
                buf += c
        elif c.isalnum():
            buf += c
        else:
            if buf:
                tokens.append(buf)
                buf = ""
        i += 1

    if buf:
        tokens.append(buf)

    return tokens


def normalize_title(title: str) -> str | None:
    """
    Normalize title into kebab-case according to ADR-0009
    """
    words: List[str] = []

    for part in re.split(r"\s+", title.strip()):
        words.extend(split_camel_and_acronyms(part))

    if len(words) < 2 or words[0].lower() != 'adr' or not words[1].isdigit():
        return None
    adr_id = int(words[1])

    title_words = []
    for w in words[2:]:
        title_words.append(w.lower())
    rest = "-".join(filter(None, title_words))

    normalized_name = f'ADR-{adr_id:0>4}--{rest}'
    return normalized_name


# ----------------------------
# ADR filename handling
# ----------------------------

ADR_ID_RE = re.compile(r"ADR-(\d{4})", re.IGNORECASE)
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def extract_title(md_text: str) -> str | None:
    m = TITLE_RE.search(md_text)
    return m.group(1).strip() if m else None

def expected_filename(file: Path, raw_title: str) -> str | None:
    # Use ADR-{adr_id} in title
    m = ADR_ID_RE.search(raw_title)
    if not m:
        return None
    normalized = normalize_title(raw_title)
    if normalized is None:
        return None
    return f"{normalized}.md"


# ----------------------------
# Main
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Normalize ADR filenames")
    parser.add_argument("path", help="Path to ADR directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without renaming files",
    )
    args = parser.parse_args()

    base = Path(args.path)
    if not base.is_dir():
        raise SystemExit(f"Not a directory: {base}")

    for md_file in sorted(base.glob("*.md")):
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        title = extract_title(text)

        if not title:
            print(f"[SKIP] {repr(md_file.name)}: No markdown title")
            continue

        new_name = expected_filename(md_file, title)
        if not new_name:
            print(f"[SKIP] {repr(md_file.name)}: No ADR id found")
            continue

        if md_file.name == new_name:
            print(f"[SKIP] {repr(md_file.name)}: Already good ADR file name")
            continue

        target = md_file.with_name(new_name)

        if args.dry_run:
            print(f"[DRY-RUN] {repr(md_file.name)} -> {repr(new_name)}")
        else:
            print(f"[RENAME]  {repr(md_file.name)} -> {repr(new_name)}")
            md_file.rename(target)


if __name__ == "__main__":
    main()
