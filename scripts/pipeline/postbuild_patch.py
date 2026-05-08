"""Post-build patcher for Инструменты_translated_project.

After EDT rebuilds the translated project, applies literal text replacements
to translated module files to cover residual Russian fragments and known
mistranslations that EDT's LanguageTool cannot fix via dictionaries alone.

Run this after every EDT dependent-translation rebuild.

Scope:
- Only patches translated project (Инструменты_translated_project).
- Never touches source project, dictionaries, or metadata.
- Idempotent -- running twice is safe.
- Skips Cyrillic-named directories (those are EDT's RU mirror copies).

The default replacement table covers fixes that apply to ANY 1C project
(wrong platform aliases, platform field renames). Project-specific fixes
(literal-restore for tests, HTTP-verb literals, etc.) should be added as
they surface during testing -- see POSTBUILD_PATCHER.md.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

PROJ = Path(
    r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/"
    r"Tools UI 1C/Инструменты_Перевод"
)

CYR = re.compile(r"[А-Яа-яЁё]")

# Per-file RU source for literal restoration (EDT mistranslates some string
# literals via camelcase dict tokenization -- e.g. test data literals like
# "Секретный ключ" -> "Secret key" which breaks byte-level assertions).
# Add (ru_path, en_path) tuples per module needing this treatment.
LITERAL_RESTORE_PAIRS: list[tuple[Path, Path]] = [
    # Example -- uncomment and adjust as needed:
    # (
    #     Path(r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/"
    #          r"Tools UI 1C/Инструменты/src/DataProcessors/УИ_Тесты/ObjectModule.bsl"),
    #     PROJ / "src/DataProcessors/UI_Tests/ObjectModule.bsl",
    # ),
]

# Russian literals that phase-1 restore must LEAVE TRANSLATED (skip the
# line-aligned revert). Struct-key / list-of-names literals that the code
# reads/writes with English keys elsewhere -- restoring them to Russian
# would break runtime lookups.
RESTORE_EXCEPTIONS: frozenset[str] = frozenset({
    # Example: "Наименование,Значение",
})

# (russian_or_wrong_english, correct_english) -- longest-first ordering matters
# for substring overlaps. Generic 1C-platform fixes are kept here as a safety
# net even when the user dict overrides them. Project-specific entries should
# be added as runtime errors / failing tests reveal them.
REPLACEMENTS: list[tuple[str, str]] = [
    # --- EDT platform dictionary has wrong English alias for СтрНачинаетсяС ---
    # EDT maps it to StrStartsWith but the actual platform English identifier
    # is StrStartWith (no "s" in "Start"). StrEndsWith is OK -- leave alone.
    ("StrStartsWith(",  "StrStartWith("),
    ("СтрНачинаетсяС(", "StrStartWith("),

    # --- Platform object fields with wrong positional translation ---
    # Tokenizer reverses word order; platform names differ. Fix access sites
    # (.Name) and literals ("Name"). If dict is fixed via fix_platform_fields.py,
    # these are no-ops on next rebuild -- they remain as safety net.
    (".CodeStatus",              ".StatusCode"),                   # HTTPResponse
    ('"CodeStatus"',             '"StatusCode"'),
    (".BreakLines",              ".NewLines"),                     # JSONWriterSettings
    ('"BreakLines"',             '"NewLines"'),
    (".SymbolsIndent",           ".PaddingSymbols"),               # JSONWriterSettings
    ('"SymbolsIndent"',          '"PaddingSymbols"'),
    (".EscapeSeparatorsLines",   ".EscapeLineTerminators"),
    ('"EscapeSeparatorsLines"',  '"EscapeLineTerminators"'),
    (".AddressResource",         ".ResourceAddress"),              # HTTPRequest
    ('"AddressResource"',        '"ResourceAddress"'),
    (".UseAuthenticationOS",     ".UseOSAuthentication"),          # InternetProxy
    ('"UseAuthenticationOS"',    '"UseOSAuthentication"'),
]


def has_cyrillic_path(p: Path, src_root: Path) -> bool:
    rel = p.relative_to(src_root)
    return any(CYR.search(part) for part in rel.parts[:-1])


def apply_replacements(text: str) -> tuple[str, int]:
    total = 0
    for src, dst in REPLACEMENTS:
        if src in text:
            count = text.count(src)
            text = text.replace(src, dst)
            total += count
    return text, total


# --- Phase 2 -- literal restore from RU source ---

LITERAL_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
IDENT_LIKE = re.compile(r"^[A-Za-zА-Яа-яЁё0-9_]+(?:,\s*[A-Za-zА-Яа-яЁё0-9_]+)*$")


def is_identifier_like(s: str) -> bool:
    if not s:
        return False
    return bool(IDENT_LIKE.match(s))


def restore_literals(ru_path: Path, en_path: Path) -> int:
    if not ru_path.exists() or not en_path.exists():
        print(f"  SKIP literal-restore: missing file {ru_path if not ru_path.exists() else en_path}")
        return 0

    ru_lines = ru_path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    en_lines = en_path.read_text(encoding="utf-8-sig").splitlines(keepends=True)

    if len(ru_lines) != len(en_lines):
        print(f"  SKIP literal-restore: line count mismatch ({len(ru_lines)} vs {len(en_lines)}) {en_path.name}")
        return 0

    changed = 0
    out_lines: list[str] = []
    for ru_ln, en_ln in zip(ru_lines, en_lines):
        ru_lits = LITERAL_RE.findall(ru_ln)
        en_lits = LITERAL_RE.findall(en_ln)
        if not ru_lits or len(ru_lits) != len(en_lits) or ru_lits == en_lits:
            out_lines.append(en_ln)
            continue

        new_en = en_ln
        for ru_lit, en_lit in zip(ru_lits, en_lits):
            if ru_lit == en_lit:
                continue
            if not CYR.search(ru_lit):
                continue
            if ru_lit in RESTORE_EXCEPTIONS:
                continue
            if is_identifier_like(ru_lit):
                continue
            new_en = new_en.replace(f'"{en_lit}"', f'"{ru_lit}"', 1)
            changed += 1
        out_lines.append(new_en)

    if changed:
        en_path.write_text("".join(out_lines), encoding="utf-8")
    return changed


def main() -> int:
    src = PROJ / "src"
    if not src.is_dir():
        print(f"ERROR: source root not found: {src}", file=sys.stderr)
        return 2

    # Phase 1 -- literal replacements across all translated BSL files.
    files = [p for p in src.rglob("*.bsl") if not has_cyrillic_path(p, src)]
    phase1_total = 0
    phase1_files = 0
    for f in sorted(files):
        text = f.read_text(encoding="utf-8-sig")
        new_text, count = apply_replacements(text)
        if count:
            f.write_text(new_text, encoding="utf-8")
            phase1_total += count
            phase1_files += 1
    print(f"phase 1: {phase1_total} replacements across {phase1_files} files")

    # Phase 2 -- literal restore from RU source.
    phase2_total = 0
    for ru_path, en_path in LITERAL_RESTORE_PAIRS:
        n = restore_literals(ru_path, en_path)
        if n:
            print(f"  restored {n} literal(s) in {en_path.relative_to(PROJ) if en_path.is_relative_to(PROJ) else en_path}")
            phase2_total += n
    print(f"phase 2: {phase2_total} literal restorations across {len(LITERAL_RESTORE_PAIRS)} configured pair(s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
