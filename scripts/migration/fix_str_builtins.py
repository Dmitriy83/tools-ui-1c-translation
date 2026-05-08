"""Override EDT's platform-dictionary translations of СтрНачинаетсяС.

EDT maps it to `StrStartsWith` -- but the actual 1C platform English alias
is `StrStartWith` (no "s" in Start). Adding the entry to user dict
(`common-camelcase_en.dict`) overrides EDT's platform context.

Note: `СтрЗаканчиваетсяНа` -> `StrEndsWith` IS correct (with "s"). Don't
let the pattern mislead you -- the asymmetry is real.
"""
from pathlib import Path

CAMEL = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")

OVERRIDES = {
    "СтрНачинаетсяС": "StrStartWith",
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


raw = CAMEL.read_bytes()
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

for k, v in OVERRIDES.items():
    entries[k] = v
    print(f"set: {k}={v}")

out_lines = [header, ""] if header else []
for k in sorted(entries):
    out_lines.append(k + "=" + entries[k])
out_text = eol.join(out_lines) + eol
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
CAMEL.write_bytes(out_raw)

print(f"\ntotal: {len(entries)} entries")
