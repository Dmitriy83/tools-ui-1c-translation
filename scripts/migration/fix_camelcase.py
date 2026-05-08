"""Fix camelcase dict issues found after EDT applied the translation.

Two roles:
1. Normalize weird-case values inherited from legacy dicts
   (`Get=GET` -> `Get=Get`, `Patch=PATCH` -> `Patch=Patch`).
2. Add missing entries for identifiers used in source BSL but not in dict.

Populate FIXES / ADDS as you discover issues during testing.
"""
from pathlib import Path

TARGET = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")

FIXES = {
    # Examples -- populate as needed:
    # "Get":   "Get",
    # "Put":   "Put",
}

ADDS = {
    # Examples -- populate from find_missing_dict_keys.py output:
    # "Имя":            "Name",
    # "ПолучитьПрокси": "GetProxy",
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


raw = TARGET.read_bytes()
has_bom = raw.startswith(b"\xef\xbb\xbf")
if has_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
eol = "\r\n" if "\r\n" in text else "\n"
lines = text.split(eol)

existing_keys = set()
fixed_in_place = 0
out = []
for ln in lines:
    if not ln or ln.startswith("#"):
        out.append(ln)
        continue
    kv = split_kv(ln)
    if kv is None:
        out.append(ln)
        continue
    k, v = kv
    existing_keys.add(k)
    if k in FIXES and v != FIXES[k]:
        out.append(k + "=" + FIXES[k])
        fixed_in_place += 1
    else:
        out.append(ln)

new_adds = [(k, v) for k, v in ADDS.items() if k not in existing_keys]
already = [(k, v) for k, v in ADDS.items() if k in existing_keys]

print(f"in-place fixes: {fixed_in_place}")
print(f"new entries to add: {len(new_adds)}  (already present: {len(already)})")
for k, v in new_adds:
    print(f"  +{k}={v}")
for k, v in already:
    print(f"  (already) {k}=...")

for k, v in sorted(new_adds):
    out.append(k + "=" + v)

out_text = eol.join(out)
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
TARGET.write_bytes(out_raw)

print(f"\nwritten to {TARGET}")
