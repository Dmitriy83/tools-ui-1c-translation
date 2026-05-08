"""Extract untranslated entries from one specific dict/lstr/trans file.

Outputs:
- glossary.txt: already-translated entries (no Cyrillic in value) -- useful
  as a terminology reference for the LLM phase.
- untranslated.txt: TSV `key<TAB>russian_value` -- worklist to translate.

Usage:
    python scripts/analysis/extract_untranslated.py <path_to_dict_or_lstr_or_trans>
"""
import re
import sys
from pathlib import Path


def read_text(p: Path) -> str:
    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8")


def split_kv(line: str):
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line[i] == "=":
            return line[:i], line[i + 1:]
        i += 1
    return None


def read_props_ordered(p: Path):
    out = []
    for ln in read_text(p).splitlines():
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            out.append(kv)
    return out


def has_cyrillic(s: str) -> bool:
    return bool(re.search(r"[А-Яа-яЁё]", s))


def main():
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"ERROR: file not found: {target}", file=sys.stderr)
        return 2

    out_root = Path(__file__).resolve().parent.parent.parent
    entries = read_props_ordered(target)

    glossary = []
    untranslated = []
    for k, v in entries:
        # Untranslated = empty value OR value still contains Cyrillic.
        if (not v) or has_cyrillic(v):
            untranslated.append((k, v))
        else:
            glossary.append((k, v))

    (out_root / "glossary.txt").write_text(
        "\n".join(f"{k}\t{v}" for k, v in glossary),
        encoding="utf-8"
    )
    (out_root / "untranslated.txt").write_text(
        "\n".join(f"{k}\t{v}" for k, v in untranslated),
        encoding="utf-8"
    )

    print(f"glossary (already-translated): {len(glossary)}")
    print(f"untranslated (Cyrillic-valued): {len(untranslated)}")
    print(f"total entries: {len(entries)}")
    print(f"\nwrote: {out_root / 'glossary.txt'}")
    print(f"wrote: {out_root / 'untranslated.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
