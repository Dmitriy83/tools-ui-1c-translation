"""Apply per-key translations from a TR dict to a target .lstr/.trans/.dict file.

Reads the target file line-by-line, for any line whose key exists in TR,
replaces the value. Preserves file structure (header, blank lines, EOL, BOM).

Usage:
    python scripts/migration/apply_translations.py <target_file> <translations_module>

`translations_module` is a Python file exposing a top-level `TR = {key: value}`
dict. Pass either a relative path or a name resolved relative to this script's
directory.

Example:
    python scripts/migration/apply_translations.py \
      ../../dictionaries_en/src/CommonModules/УИ_ОбщегоНазначения/Module_en.trans \
      translations_УИ_ОбщегоНазначения.py
"""
import sys
from pathlib import Path
import importlib.util


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


def load_tr(path: Path):
    spec = importlib.util.spec_from_file_location("tr_mod", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.TR


def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    target = Path(sys.argv[1]).resolve()
    tr_arg = Path(sys.argv[2])
    tr_path = tr_arg if tr_arg.is_absolute() else (Path(__file__).parent / tr_arg)

    TR = load_tr(tr_path)
    print(f"translations loaded: {len(TR)}")

    raw = target.read_bytes()
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

    missing_in_file = set(TR) - file_keys
    print(f"keys in file: {len(file_keys)}")
    print(f"keys in TR not found in file: {len(missing_in_file)}")
    for k in sorted(missing_in_file)[:10]:
        print(f"  MISSING: {k}")

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
        if k in TR:
            out.append(k + "=" + TR[k])
            replaced += 1
        else:
            out.append(ln)

    out_text = eol.join(out)
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    target.write_bytes(out_raw)

    print(f"\nreplaced: {replaced}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
