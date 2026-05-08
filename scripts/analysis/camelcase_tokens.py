"""Tokenize Cyrillic identifiers from common-camelcase_en.dict, list unique tokens.

Reads the dict's KEYS (or VALUES if --values is passed), tokenizes each into
parts (lowercase->uppercase boundary, latin<->cyrillic boundary, digit/underscore
boundary), collects unique Cyrillic tokens with frequency. Output is the input
to `camelcase_token_tr.py`.

Usage:
    python scripts/analysis/camelcase_tokens.py            # tokenize keys
    python scripts/analysis/camelcase_tokens.py --values   # tokenize values
"""
import re
import sys
from pathlib import Path
from collections import Counter

DICT = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")
OUT = Path(__file__).resolve().parent.parent.parent / "camelcase_cyr_tokens.txt"


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


def is_cyrillic(t):
    return bool(re.search(r"[А-Яа-яЁё]", t))


def main():
    use_values = "--values" in sys.argv
    raw = DICT.read_bytes().decode("utf-8-sig")
    entries = []
    for ln in raw.splitlines():
        if not ln or ln.startswith("#"):
            continue
        kv = split_kv(ln)
        if kv:
            entries.append(kv)

    cyr_tokens = Counter()
    all_tokens = []
    for k, v in entries:
        target = v if use_values else k
        toks = tokenize(target)
        all_tokens.extend(toks)
        for t in toks:
            if is_cyrillic(t):
                cyr_tokens[t] += 1

    print(f"entries: {len(entries)}")
    print(f"total tokens: {len(all_tokens)}")
    print(f"unique cyrillic tokens: {len(cyr_tokens)}")
    print(f"\nmost frequent cyrillic tokens (top 100):")
    for t, c in cyr_tokens.most_common(100):
        print(f"  {c:>4}  {t}")

    with OUT.open("w", encoding="utf-8") as f:
        for t, c in cyr_tokens.most_common():
            f.write(f"{t}\t{c}\n")
    print(f"\nwrote full list: {OUT}")


if __name__ == "__main__":
    main()
