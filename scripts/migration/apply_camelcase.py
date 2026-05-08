"""Apply token-by-token translation to common-camelcase_en.dict.

Reads each entry, tokenizes the VALUE portion, substitutes Cyrillic tokens
via TOKEN_TR, rejoins. Preserves file structure.

Requires every Cyrillic token found in the file to have an entry in TOKEN_TR --
otherwise reports missing tokens and aborts without writing.

TOKEN_TR is loaded from `camelcase_token_tr.py` next to this script.
"""
import re
from pathlib import Path
import importlib.util

TARGET = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")
SRC = Path(__file__).parent / "camelcase_token_tr.py"


def load_tr():
    spec = importlib.util.spec_from_file_location("tr_mod", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.TOKEN_TR


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


def tokenize(ident):
    tokens = []
    cur = ""

    def flush():
        nonlocal cur
        if cur:
            tokens.append(cur)
            cur = ""

    def char_kind(c):
        if c == "_":
            return "_"
        if c.isdigit():
            return "d"
        if "а" <= c <= "я" or "А" <= c <= "Я" or c in "ёЁ":
            return "c" if c.islower() else "C"
        if c.isalpha():
            return "l" if c.islower() else "L"
        return "x"

    prev = None
    for c in ident:
        k = char_kind(c)
        new_token = False
        if prev is None:
            pass
        elif c == "_" or prev == "_":
            new_token = True
        elif k == "d" and prev != "d":
            new_token = True
        elif prev == "d" and k != "d":
            new_token = True
        elif (prev == "l" and k == "L") or (prev == "c" and k == "C"):
            new_token = True
        elif (prev == "L" and k == "l") or (prev == "C" and k == "c"):
            if len(cur) > 1:
                tokens.append(cur[:-1])
                cur = cur[-1]
        elif (prev in "lL" and k in "cC") or (prev in "cC" and k in "lL"):
            new_token = True

        if new_token:
            flush()
        cur += c
        prev = k
    flush()
    return tokens


CYR = re.compile(r"[А-Яа-яЁё]")


def translate_value(val, tr):
    tokens = tokenize(val)
    out = []
    missing = []
    for t in tokens:
        if CYR.search(t):
            if t in tr:
                out.append(tr[t])
            else:
                missing.append(t)
                out.append(t)
        else:
            out.append(t)
    return "".join(out), missing


def main():
    TR = load_tr()
    print(f"loaded translations: {len(TR)}")

    raw = TARGET.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(eol)

    all_missing = set()
    for ln in lines:
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv is None:
            continue
        _, v = kv
        _, miss = translate_value(v, TR)
        all_missing.update(miss)

    if all_missing:
        miss_file = Path(__file__).resolve().parent.parent.parent / "camelcase_missing.txt"
        miss_file.write_text("\n".join(sorted(all_missing)) + "\n", encoding="utf-8")
        print(f"\nMISSING translations for {len(all_missing)} tokens -- written to {miss_file}")
        print("\nAborting (not writing).")
        raise SystemExit(1)

    print("all tokens covered, applying...")

    replaced = 0
    unchanged = 0
    out_lines = []
    for ln in lines:
        if not ln or ln.startswith("#"):
            out_lines.append(ln)
            continue
        kv = split_kv(ln)
        if kv is None:
            out_lines.append(ln)
            continue
        k, v = kv
        tr_v, _ = translate_value(v, TR)
        if tr_v != v:
            out_lines.append(k + "=" + tr_v)
            replaced += 1
        else:
            out_lines.append(ln)
            unchanged += 1

    out_text = eol.join(out_lines)
    out_raw = out_text.encode("utf-8")
    if has_bom:
        out_raw = b"\xef\xbb\xbf" + out_raw
    TARGET.write_bytes(out_raw)

    text2 = TARGET.read_bytes().decode("utf-8-sig")
    cyr_lines = []
    for ln in text2.splitlines():
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv and CYR.search(kv[1]):
            cyr_lines.append(ln)

    print(f"\nreplaced: {replaced}  unchanged: {unchanged}")
    print(f"lines with Cyrillic in value remaining: {len(cyr_lines)}")
    if cyr_lines:
        print("samples:")
        for ln in cyr_lines[:10]:
            print(f"  {ln}")


if __name__ == "__main__":
    main()
