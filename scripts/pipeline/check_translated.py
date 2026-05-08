"""Scan the EDT-translated project for residual Cyrillic.

For tools_ui_1c (~40 common modules + 20 data processors + reports), walks
every `.bsl` file inside the translated project and separates findings into
two buckets:

- CODE issues: lines outside `//` comments that still contain Cyrillic.
  Actionable -- means an identifier or string literal wasn't translated.
- DOC issues: lines inside `//` comments that still contain Cyrillic.
  Often translation gaps in the corresponding `.trans` (EDT generator
  occasionally skips per-field keys for nested return structures).

By default, scans ALL `.bsl` files including those in Cyrillic-named dirs --
which is the right choice while translation is still in progress (untranslated
identifier `УИ_X` keeps the directory name Cyrillic). After translation is
mostly done and English-named copies appear alongside RU mirrors, pass
--skip-ru-mirrors to ignore Cyrillic-named paths.

Usage:
    python scripts/pipeline/check_translated.py
    python scripts/pipeline/check_translated.py --skip-ru-mirrors
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# Translated project root -- output of `translate_configuration`. Adjust the
# directory name after you create it.
PROJ = Path(
    r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/"
    r"Tools UI 1C/Инструменты_Перевод"
)
OUT = Path(__file__).resolve().parent.parent.parent / "check_translated.out"

CYR = re.compile(r"[А-Яа-яЁё]")


def has_cyrillic_path(p: Path, src_root: Path) -> bool:
    """True iff any directory part of `p` (relative to src) contains Cyrillic."""
    rel = p.relative_to(src_root)
    return any(CYR.search(part) for part in rel.parts[:-1])


def scan(bsl: Path) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """Return (code_issues, doc_issues) for one BSL file."""
    try:
        text = bsl.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], []
    code: list[tuple[int, str]] = []
    doc: list[tuple[int, str]] = []
    for i, ln in enumerate(text.split("\n"), 1):
        stripped = ln.lstrip()
        if not stripped:
            continue
        if not CYR.search(ln):
            continue
        if stripped.startswith("//"):
            doc.append((i, ln.rstrip()))
        else:
            code.append((i, ln.rstrip()))
    return code, doc


def main() -> int:
    src = PROJ / "src"
    if not src.is_dir():
        print(f"ERROR: source root not found: {src}", file=sys.stderr)
        return 2

    skip_ru = "--skip-ru-mirrors" in sys.argv
    if skip_ru:
        files = [p for p in src.rglob("*.bsl") if not has_cyrillic_path(p, src)]
    else:
        files = list(src.rglob("*.bsl"))
    files.sort()

    per_file: list[tuple[Path, list[tuple[int, str]], list[tuple[int, str]]]] = []
    code_total = 0
    doc_total = 0
    for f in files:
        code, doc = scan(f)
        if code or doc:
            per_file.append((f, code, doc))
            code_total += len(code)
            doc_total += len(doc)

    with OUT.open("w", encoding="utf-8") as out:
        out.write(f"=== SUMMARY ===\n")
        out.write(f"files scanned: {len(files)}\n")
        out.write(f"files with Cyrillic: {len(per_file)}\n")
        out.write(f"CODE issues: {code_total}  (actionable)\n")
        out.write(f"DOC issues:  {doc_total}  (likely .trans gaps)\n\n")
        for f, code, doc in per_file:
            rel = f.relative_to(src)
            out.write(f"--- src/{rel} ---\n")
            if code:
                out.write(f"  CODE ({len(code)}):\n")
                for lno, ln in code:
                    out.write(f"    {lno:5d}: {ln}\n")
            if doc:
                out.write(f"  DOC ({len(doc)}):\n")
                for lno, ln in doc[:30]:
                    out.write(f"    {lno:5d}: {ln}\n")
                if len(doc) > 30:
                    out.write(f"    ... ({len(doc) - 30} more)\n")
            out.write("\n")

    print(f"CODE issues: {code_total}  DOC issues: {doc_total}")
    print(f"wrote {OUT}")
    return 0 if code_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
