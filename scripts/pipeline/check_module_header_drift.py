"""Detect drift between RU module-header docstring and the frozen English
translation in ``Module_en.trans`` (the ``Description=`` key).

EDT's translation builder treats the module-level docstring as a single prose
blob keyed by ``Description=`` in ``.trans``. The English value is hand-written
once and never auto-refreshed when the RU source changes -- so literal facts
inside the comment (copyright year, version number, URLs, emails) silently
drift behind the upstream RU source.

This script extracts literal patterns (year ranges, version strings) from
the current RU module header and from the EN ``Description=`` value and flags
any mismatch.

Idempotent and read-only by default. Exit 1 if drift is detected.

Usage:
    python scripts/pipeline/check_module_header_drift.py

Configure `PAIRS` with the (RU module .bsl, EN .trans) pairs that have a
hand-written ``Description=`` block (typically root common modules whose
header is a project-wide license/version block).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# Pairs of (RU module .bsl, EN .trans) to check. Empty by default for
# tools_ui_1c -- populate as you discover modules with versioned headers.
PAIRS: list[tuple[Path, Path]] = [
    # Example -- uncomment and adjust per actual paths:
    # (
    #     Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/"
    #          r"Tools UI 1C/Инструменты/src/CommonModules/УИ_ОбщегоНазначения/Module.bsl"),
    #     Path(r"C:/git/tools-ui-1c-translation/dictionaries_en/src/"
    #          r"CommonModules/УИ_ОбщегоНазначения/Module_en.trans"),
    # ),
]

PATTERNS = [
    (re.compile(r"\b[12][0-9]{3}-[12][0-9]{3}\b"), "year-range"),
    (re.compile(r"\b[0-9]+\.[0-9]+\.[0-9]+\b"),    "version"),
]


def extract_ru_header(bsl: Path) -> str:
    lines = bsl.read_text(encoding="utf-8-sig").splitlines()
    header: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("//"):
            header.append(stripped[2:].strip())
        elif stripped == "":
            header.append("")
        else:
            break
    return "\n".join(header)


def extract_en_description(trans: Path) -> str:
    for raw in trans.read_text(encoding="utf-8-sig").splitlines():
        if raw.startswith("Description="):
            value = raw[len("Description="):]
            return (
                value.replace("\\n", "\n")
                     .replace("\\:", ":")
                     .replace("\\\\", "\\")
            )
    return ""


def find_literals(text: str, regex: re.Pattern[str]) -> list[str]:
    return regex.findall(text)


def main() -> int:
    if not PAIRS:
        print("PAIRS is empty -- nothing to check. Edit the script to add module-header pairs.")
        return 0

    drift_count = 0
    for ru_path, en_path in PAIRS:
        if not ru_path.exists():
            print(f"SKIP: RU file missing: {ru_path}", file=sys.stderr)
            continue
        if not en_path.exists():
            print(f"SKIP: EN .trans missing: {en_path}", file=sys.stderr)
            continue

        ru_text = extract_ru_header(ru_path)
        en_text = extract_en_description(en_path)

        for regex, label in PATTERNS:
            ru_lits = find_literals(ru_text, regex)
            en_lits = find_literals(en_text, regex)
            if ru_lits != en_lits:
                drift_count += 1
                print(f"DRIFT in {ru_path.name} <-> {en_path.name}:")
                print(f"  pattern: {label}")
                print(f"  RU has:  {ru_lits}")
                print(f"  EN has:  {en_lits}")

    if drift_count == 0:
        print("module-header drift: none")
        return 0
    print(f"\n{drift_count} drift(s) detected -- update the Description value(s) in the .trans file(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
