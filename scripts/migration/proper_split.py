"""Move entries between common-camelcase and common dicts per
translation_storages.yml feature_filter rules.

CamelCase identifier = has >=2 uppercase letters (case boundary inside).
non-CamelCase = single word (only the first letter is uppercase).

EDT's storage filter (`feature_filter: camelcase: ONLY` vs `NONE`) means a
single-word identifier like `Имя=Name` placed in `common-camelcase_en.dict`
is IGNORED by EDT. It must live in `common_en.dict`.

Edit `TO_COMMON` to list keys to migrate from camelcase -> common.
"""
from pathlib import Path

CAMEL = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")
COMMON = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common_en.dict")

TO_COMMON = {
    # Example -- populate as you discover misplaced single-word identifiers:
    # "Имя": "Name",
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


def read_sorted_entries(path):
    raw = path.read_bytes()
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
            entries[kv[0]] = kv[1]
    return header, entries, eol, has_bom


def write_sorted(path, header, entries, eol, has_bom):
    out_lines = []
    if header:
        out_lines.append(header)
        out_lines.append("")
    for k in sorted(entries):
        out_lines.append(k + "=" + entries[k])
    out_text = eol.join(out_lines) + eol
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    path.write_bytes(out_raw)


def main():
    if not TO_COMMON:
        print("TO_COMMON is empty -- nothing to move. Edit the script to populate.")
        return

    cheader, centries, ceol, cbom = read_sorted_entries(CAMEL)
    nheader, nentries, neol, nbom = read_sorted_entries(COMMON)

    for k, v in TO_COMMON.items():
        if k in centries:
            del centries[k]
        nentries[k] = v

    write_sorted(CAMEL, cheader, centries, ceol, cbom)
    write_sorted(COMMON, nheader, nentries, neol, nbom)

    print(f"camelcase: {len(centries)} entries")
    print(f"common:    {len(nentries)} entries")


if __name__ == "__main__":
    main()
