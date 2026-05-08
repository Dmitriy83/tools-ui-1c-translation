"""Apply per-file translations from translations_small.py to the dict tree.

Reads target files line-by-line, replaces values for keys found in TR.
Preserves header, blank lines, EOL, and BOM. Verifies every key in TR
exists in its target file -- reports missing.
"""
from pathlib import Path
import importlib.util

ROOT = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src")
SRC = Path(__file__).parent / "translations_small.py"


def load_tr():
    spec = importlib.util.spec_from_file_location("tr_mod", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.TR


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


def apply_file(rel, tr_map):
    path = ROOT / rel
    if not path.exists():
        print(f"  SKIP: {path} not found")
        return 0
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(eol)

    file_keys = set()
    for ln in lines:
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            file_keys.add(kv[0])

    missing = set(tr_map) - file_keys
    if missing:
        print(f"  MISSING keys (not in file):")
        for k in sorted(missing):
            print(f"    {k}")

    replaced = 0
    out = []
    for ln in lines:
        if not ln or ln.startswith("#"):
            out.append(ln)
            continue
        kv = split_kv(ln)
        if kv is None:
            out.append(ln)
            continue
        k, _ = kv
        if k in tr_map:
            out.append(k + "=" + tr_map[k])
            replaced += 1
        else:
            out.append(ln)

    out_text = eol.join(out)
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    path.write_bytes(out_raw)
    return replaced


def main():
    TR = load_tr()
    grand = 0
    for rel, m in TR.items():
        print(f"{rel}: {len(m)} translations", end=" -> ")
        n = apply_file(rel, m)
        print(f"replaced {n}")
        grand += n
    print(f"\nGRAND TOTAL: {grand}")


if __name__ == "__main__":
    main()
