"""Fix 1C standard region/subsystem naming in common-camelcase_en.dict.

EDT expects canonical English region names per 1C SSL (Standard Subsystems
Library). If a region is translated to something non-canonical (e.g.,
ProgramInterface, HandlersEvents), EDT issues "method should be placed in
standard region" warnings for every method in that region.
"""
from pathlib import Path

TARGET = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")

FIXES = {
    "ПрограммныйИнтерфейс":                  "Public",
    "СлужебныйПрограммныйИнтерфейс":         "Internal",
    "СлужебныеПроцедурыИФункции":            "Private",
    "ОбработчикиСобытий":                    "EventHandlers",
    "ОбработчикиСобытийФормы":               "FormEventHandlers",
    "ОбработчикиСобытийЭлементовШапкиФормы": "FormHeaderItemsEventHandlers",
    "ОбработчикиСобытийКомандФормы":         "FormCommandsEventHandlers",
    "ОбработчикиКомандФормы":                "FormCommandsEventHandlers",
    "ОбработчикиСобытийТаблицы":             "TableEventHandlers",
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

existing = set()
out = []
in_place = 0
for ln in lines:
    if not ln or ln.startswith("#"):
        out.append(ln)
        continue
    kv = split_kv(ln)
    if kv is None:
        out.append(ln)
        continue
    k, v = kv
    existing.add(k)
    if k in FIXES and v != FIXES[k]:
        print(f"  fixing: {k}: {v} -> {FIXES[k]}")
        out.append(k + "=" + FIXES[k])
        in_place += 1
    else:
        out.append(ln)

new_adds = [(k, v) for k, v in FIXES.items() if k not in existing]
for k, v in sorted(new_adds):
    print(f"  adding: {k}={v}")
    out.append(k + "=" + v)

out_text = eol.join(out)
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
TARGET.write_bytes(out_raw)

print(f"\nin-place fixes: {in_place}  new entries: {len(new_adds)}")
