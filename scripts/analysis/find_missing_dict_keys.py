"""Find Cyrillic identifiers used in RU source modules that are missing as keys
in common-camelcase_en.dict.

These are the identifiers EDT cannot translate -- they stay Cyrillic in the
translated module.

Walks all `.bsl` files under the source RU EDT project (PROJ_RU), extracts
Cyrillic-containing identifiers (excluding those inside string literals and
line comments), and diffs against the dict's keys.
"""
import re
from pathlib import Path

# Source RU EDT project root. The Инструменты extension is loaded into EDT
# directly from the source repo via .location -- no copy in the workspace.
PROJ_RU = Path(r"C:/git/tools_ui_1c/src/Инструменты/src")
DICT = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")
OUT = Path(__file__).resolve().parent.parent.parent / "missing_keys.out"

CYR = re.compile(r"[А-Яа-яЁё]")
IDENT_RE = re.compile(r"[A-Za-zА-Яа-яЁё_][A-Za-z0-9А-Яа-яЁё_]*")
STRING_RE = re.compile(r'"[^"]*"')
COMMENT_RE = re.compile(r"//[^\n]*")


def extract_idents(text: str):
    no_str = STRING_RE.sub('""', text)
    no_comm = COMMENT_RE.sub("", no_str)
    return set(IDENT_RE.findall(no_comm))


def main():
    if not PROJ_RU.is_dir():
        print(f"ERROR: source root not found: {PROJ_RU}")
        return 2

    cyr_idents = set()
    files = sorted(PROJ_RU.rglob("*.bsl"))
    for f in files:
        try:
            text = f.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        for ident in extract_idents(text):
            if CYR.search(ident):
                cyr_idents.add(ident)

    dict_keys = set()
    if DICT.exists():
        for ln in DICT.read_bytes().decode("utf-8-sig").splitlines():
            if not ln or ln.startswith("#"):
                continue
            i = 0
            while i < len(ln):
                if ln[i] == "\\" and i + 1 < len(ln):
                    i += 2
                    continue
                if ln[i] == "=":
                    break
                i += 1
            if i < len(ln):
                dict_keys.add(ln[:i])

    missing = sorted(cyr_idents - dict_keys)
    covered = cyr_idents & dict_keys

    with OUT.open("w", encoding="utf-8") as f:
        f.write(f"BSL files scanned: {len(files)}\n")
        f.write(f"identifiers in source (Cyrillic only): {len(cyr_idents)}\n")
        f.write(f"covered by camelcase dict: {len(covered)}\n")
        f.write(f"MISSING from camelcase dict: {len(missing)}\n\n")
        f.write("=== Missing identifiers (these stay Russian in translated module) ===\n")
        for m in missing:
            f.write(f"  {m}\n")

    print(f"wrote {OUT}")
    print(f"BSL files scanned: {len(files)}")
    print(f"cyr idents in source: {len(cyr_idents)}")
    print(f"missing from dict: {len(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
