"""Audit translation status across all module categories."""
import re
from pathlib import Path

CYR = re.compile(r"[А-Яа-яЁё]")
ROOT = Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src")


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


def categorize_value(line):
    """Return ('name'|'word'|'prose'|'other', is_cyr_value)"""
    kv = split_kv(line)
    if not kv:
        return None, False
    k, v = kv
    if not v:
        return None, False
    cyr = bool(CYR.search(v))
    if k.endswith(".Name"):
        return "name", cyr
    if ".String.Word." in k and k.endswith(".Key"):
        return "word", cyr
    if k.endswith(".Description") or k.endswith(".Lines"):
        return "prose", cyr
    return "other", cyr


categories = ["CommonModules", "DataProcessors", "Reports", "Catalogs",
              "CommonForms", "CommonCommands", "CommonTemplates",
              "HTTPServices", "Roles", "Subsystems"]

print(f"{'category':<18} {'files':>6} {'.Name (cyr)':>14} {'.Word (cyr)':>14} {'prose (cyr)':>14}")
for cat in categories:
    cat_dir = ROOT / cat
    if not cat_dir.is_dir():
        continue
    n_files = 0
    n_name = n_name_cyr = 0
    n_word = n_word_cyr = 0
    n_prose = n_prose_cyr = 0
    for f in cat_dir.rglob("*"):
        if f.suffix not in (".lstr", ".trans"):
            continue
        n_files += 1
        text = f.read_bytes().decode("utf-8-sig")
        for ln in text.splitlines():
            if not ln or ln.startswith("#"):
                continue
            cat_t, cyr = categorize_value(ln)
            if cat_t == "name":
                n_name += 1
                if cyr:
                    n_name_cyr += 1
            elif cat_t == "word":
                n_word += 1
                if cyr:
                    n_word_cyr += 1
            elif cat_t == "prose":
                n_prose += 1
                if cyr:
                    n_prose_cyr += 1
    print(f"{cat:<18} {n_files:>6} {n_name:>6}({n_name_cyr:>5}) {n_word:>6}({n_word_cyr:>5}) {n_prose:>6}({n_prose_cyr:>5})")
