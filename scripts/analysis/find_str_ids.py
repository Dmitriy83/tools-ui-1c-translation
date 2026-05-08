"""Find all Стр* identifiers in RU source modules.

Useful for auditing which platform string built-ins are used in the project,
to anticipate which ones might need overrides via fix_str_builtins.py
(EDT's platform dictionary has wrong English aliases for some).
"""
import re
from pathlib import Path

# EDT loads Инструменты directly from the source repo.
PROJ_RU = Path(r"C:/git/tools_ui_1c/src/Инструменты/src")
OUT = Path(__file__).resolve().parent.parent.parent / "str_ids.out"


def main():
    if not PROJ_RU.is_dir():
        print(f"ERROR: source root not found: {PROJ_RU}")
        return 2

    idents = set()
    for f in sorted(PROJ_RU.rglob("*.bsl")):
        try:
            text = f.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        no_str = re.sub(r'"[^"]*"', '""', text)
        no_comm = re.sub(r"//[^\n]*", "", no_str)
        idents.update(re.findall(r"\b(Стр[А-Яа-яёЁ]+)\b", no_comm))

    OUT.write_text("\n".join(sorted(idents)) + "\n", encoding="utf-8")
    print(f"found {len(idents)} Стр* identifiers")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
