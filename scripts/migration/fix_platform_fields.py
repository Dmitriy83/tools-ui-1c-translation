"""Override EDT/tokenizer translations of platform object field/method names
that don't match the actual 1C platform English identifiers.

These are properties/methods of platform types (HTTPResponse, HTTPRequest,
JSONWriterSettings, InternetProxy, etc.) whose English names in 1C don't
follow the positional word-for-word translation of the Russian name.
"""
from pathlib import Path

CAMEL = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/common-camelcase_en.dict")

OVERRIDES = {
    # HTTPResponse.КодСостояния -> StatusCode (not CodeStatus)
    "КодСостояния": "StatusCode",

    # JSONWriterSettings -- platform English differs from positional translation
    "ПереносСтрок":                  "NewLines",            # was BreakLines
    "СимволыОтступа":                "PaddingSymbols",      # was SymbolsIndent
    "ЭкранироватьРазделителиСтрок":  "EscapeLineTerminators",  # was EscapeSeparatorsLines

    # HTTPRequest.АдресРесурса -> ResourceAddress (not AddressResource)
    "АдресРесурса": "ResourceAddress",

    # InternetProxy
    "ИспользоватьАутентификациюОС": "UseOSAuthentication",   # was UseAuthenticationOS

    # NOTE: СНачала=FromBegin is correct per EDT (verified). Don't override
    # without confirming via get_platform_documentation MCP tool.
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

changed = 0
for k, v in OVERRIDES.items():
    if entries.get(k) != v:
        print(f"set: {k}: {entries.get(k, '(none)')} -> {v}")
        entries[k] = v
        changed += 1

out_lines = [header, ""] if header else []
for k in sorted(entries):
    out_lines.append(k + "=" + entries[k])
out_text = eol.join(out_lines) + eol
out_raw = out_text.encode("utf-8")
if has_bom:
    out_raw = b"\xef\xbb\xbf" + out_raw
CAMEL.write_bytes(out_raw)

print(f"\n{changed} entries updated, total: {len(entries)}")
