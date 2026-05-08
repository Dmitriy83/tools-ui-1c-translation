"""Normalize PascalCase=lowercase entries inherited from legacy dicts.

Pattern: a PascalCase key with an all-lowercase value (`Cookie=cookie`,
`Basic=basic`) makes EDT emit identifiers like `cookies`, `basic` -- which
trigger BSL "variable name must start with capital letter" warnings.

The script forces value-case to match key-case for a known list of keys, and
flags suspicious identity-lowercase entries for manual review.
"""
from pathlib import Path

TARGET = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")

FIXES = {
    # Populate as you discover legacy lowercase values. Examples:
    # "Cookie":   "Cookie",
    # "Basic":    "Basic",
    # "Json":     "Json",
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

out = []
in_place = 0
suspicious = []
for ln in lines:
    if not ln or ln.startswith("#"):
        out.append(ln)
        continue
    kv = split_kv(ln)
    if kv is None:
        out.append(ln)
        continue
    k, v = kv
    if k in FIXES and v != FIXES[k]:
        print(f"  fix: {k}: {v} -> {FIXES[k]}")
        out.append(k + "=" + FIXES[k])
        in_place += 1
        continue
    out.append(ln)
    if k and k[0].isupper() and v and v == v.lower() and not any(c.isdigit() for c in v) and len(v) > 2 and v.isascii():
        if v == k.lower():
            suspicious.append((k, v))

out_text = eol.join(out)
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
TARGET.write_bytes(out_raw)

print(f"\nfixed: {in_place}")
print(f"\nSuspicious lowercase-valued entries (review and add to FIXES if these break BSL):")
for k, v in suspicious[:30]:
    print(f"  {k}={v}")
if len(suspicious) > 30:
    print(f"  ... ({len(suspicious)} total)")
