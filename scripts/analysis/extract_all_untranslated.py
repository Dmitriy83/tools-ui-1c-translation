"""Extract untranslated entries from ALL dict files under dictionaries_en/src/.

Walks every `.lstr`, `.trans`, and `.dict` file. For each: only keys whose
value still contains Cyrillic are considered untranslated. Outputs per-file
TSV files under `untr/` for manual translation, plus a summary table.

Usage:
    python scripts/analysis/extract_all_untranslated.py
"""
from __future__ import annotations
import re
from pathlib import Path

NEW_ROOT = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src")
OUT_DIR = Path(__file__).resolve().parent.parent.parent / "untr"
OUT_DIR.mkdir(exist_ok=True)

CYR = re.compile(r"[А-Яа-яЁё]")


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


def read_entries(p: Path):
    out = []
    for ln in read_text(p).splitlines():
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            out.append(kv)
    return out


def discover_files(root: Path):
    patterns = ("*.lstr", "*.trans", "*.dict", "*.lsdict")
    files: list[Path] = []
    for pat in patterns:
        files.extend(root.rglob(pat))
    return sorted(files)


def main():
    files = discover_files(NEW_ROOT)
    if not files:
        print(f"no dict/lstr/trans files under {NEW_ROOT}")
        return

    totals = []
    for p in files:
        rel = p.relative_to(NEW_ROOT)
        entries = read_entries(p)
        # Untranslated = empty value OR value still contains Cyrillic.
        # EDT generates keys with empty values for fresh projects; manual/LLM
        # translation later fills them; partial states may still have Cyrillic
        # if the dict was bootstrapped from an older project.
        empty = [(k, v) for k, v in entries if not v]
        cyr   = [(k, v) for k, v in entries if v and CYR.search(v)]
        untr  = empty + cyr
        totals.append((rel, len(entries), len(empty), len(cyr)))
        if untr:
            safe_name = str(rel).replace("/", "__").replace("\\", "__")
            (OUT_DIR / f"{safe_name}.tsv").write_text(
                "\n".join(f"{k}\t{v}" for k, v in untr),
                encoding="utf-8"
            )

    print(f"{'file':<70} {'total':>6} {'empty':>6} {'cyr':>6}")
    grand_total = grand_empty = grand_cyr = 0
    for rel, t, e, c in totals:
        marker = "*" if (e or c) else " "
        print(f"{marker} {str(rel):<68} {t:>6} {e:>6} {c:>6}")
        grand_total += t
        grand_empty += e
        grand_cyr   += c
    print(f"\nGRAND TOTAL: total={grand_total}  empty={grand_empty}  cyr-valued={grand_cyr}  untr={grand_empty + grand_cyr}")
    print(f"per-file lists in: {OUT_DIR}")


if __name__ == "__main__":
    main()
