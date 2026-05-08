"""Sort common-camelcase_en.dict (and optionally common_en.dict) alphabetically.

Theory: EDT may ignore entries that appear after the first blank line or out
of alphabetical order. Sorting puts all entries in the main sorted section
so EDT picks them up.

Usage:
    python scripts/migration/sort_dict.py                # sort common-camelcase only
    python scripts/migration/sort_dict.py --all          # sort both files
"""
import sys
from pathlib import Path

ROOT = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src")
TARGETS = {
    "camelcase": ROOT / "common-camelcase_en.dict",
    "common":    ROOT / "common_en.dict",
}


def split_kv(line):
    i = 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line):
            i += 2
            continue
        if line[i] == "=":
            return line[:i], line[i + 1:]
        i += 1
    return None


def sort_file(target: Path) -> int:
    raw = target.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(eol)

    header = None
    entries = {}
    for ln in lines:
        if not ln:
            continue
        if ln.startswith("#"):
            if header is None:
                header = ln
            continue
        kv = split_kv(ln)
        if kv:
            k, v = kv
            entries[k] = v

    sorted_keys = sorted(entries.keys())
    out_lines = []
    if header:
        out_lines.append(header)
        out_lines.append("")
    for k in sorted_keys:
        out_lines.append(k + "=" + entries[k])

    out_text = eol.join(out_lines) + eol
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    target.write_bytes(out_raw)
    return len(sorted_keys)


def main():
    do_all = "--all" in sys.argv
    targets = ["camelcase", "common"] if do_all else ["camelcase"]
    for name in targets:
        path = TARGETS[name]
        if not path.exists():
            print(f"SKIP: {path} not found")
            continue
        n = sort_file(path)
        print(f"sorted {n} entries in {path.name}")


if __name__ == "__main__":
    main()
