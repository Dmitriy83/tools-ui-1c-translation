"""Delete orphan metadata-object directories left over by EDT translation
builder after dictionary renames.

When a whole-identifier override in `common-camelcase_<lang>.dict` is changed
(e.g. `КоннекторHTTP=ConnectorHTTP` -> `=HTTPConnector`), EDT's dependent
translation builder generates the new directory but does NOT delete the old
one. The old directory keeps its `Module.bsl` (and other files) but loses its
`<DirName>.mdo` metadata file -- because no metadata object is registered
under the old name anymore. EDT's validator still picks up these orphan
modules and reports phantom errors against them.

This script walks the standard EDT metadata category directories, finds any
`<Name>/` subdirectory that lacks a `<Name>.mdo` metadata file, and deletes
the whole directory.

Idempotent. Prints what was deleted. Run after `translate_configuration` /
EDT rebuild, before validation.

Usage:
    python scripts/pipeline/cleanup_orphan_modules.py            # delete
    python scripts/pipeline/cleanup_orphan_modules.py --dry-run  # preview only

Configure `PROJ` below to point at the translated project root.
"""
from __future__ import annotations
import re
import shutil
import sys
from pathlib import Path

# Cyrillic-named directories under src/ are intentional Russian mirrors that
# EDT's dependent translation builder writes alongside the translated output
# (see CLAUDE.md "Translated project has both source and translation"). They
# legitimately lack `.mdo` files because they are not separate metadata
# objects. Don't treat them as orphans.
CYRILLIC = re.compile(r"[А-Яа-яЁё]")

# Translated project root -- the project EDT generates as output of dependent
# translation (via `translate_configuration` MCP tool). Sits in the EDT
# workspace alongside the source extension. Adjust the directory name after
# you create it (typical convention: `<source>_translated_project`).
PROJ = Path(
    r"C:/Users/DmitryZhikharev/AppData/Local/1C/1cedtstart/projects/"
    r"Tools UI 1C/Инструменты_Перевод"
)

# Standard EDT metadata category directories where each metadata object lives
# in its own subfolder with a `<Name>.mdo` descriptor. Categories whose
# children DON'T have a per-object `.mdo` (Languages, Configuration, Ext) are
# excluded by simply not listing them here.
CATEGORIES = [
    "CommonModules", "CommonForms", "CommonCommands", "CommonTemplates",
    "CommonAttributes", "CommonPictures",
    "Catalogs", "Documents", "DocumentJournals", "DocumentNumerators",
    "Reports", "DataProcessors",
    "Enums", "Constants",
    "ChartsOfCharacteristicTypes", "ChartsOfAccounts", "ChartsOfCalculationTypes",
    "InformationRegisters", "AccumulationRegisters", "AccountingRegisters",
    "CalculationRegisters",
    "BusinessProcesses", "Tasks",
    "ExchangePlans", "ExternalDataSources",
    "FilterCriteria", "Subsystems", "EventSubscriptions", "ScheduledJobs",
    "FunctionalOptions", "FunctionalOptionsParameters",
    "DefinedTypes", "SettingsStorages", "Sequences",
    "WebServices", "HTTPServices", "WSReferences",
    "Roles", "StyleItems", "Styles", "Languages",
    "Bots", "IntegrationServices",
]


def find_orphan_dirs(src_root: Path) -> list[Path]:
    """Return list of orphan metadata-object dirs under `src_root`.

    A subdirectory `src/<Category>/<Name>/` is orphan iff it lacks a sibling
    `<Name>.mdo` file inside it.
    """
    orphans: list[Path] = []
    for category in CATEGORIES:
        cat_dir = src_root / category
        if not cat_dir.is_dir():
            continue
        for child in sorted(cat_dir.iterdir()):
            if not child.is_dir():
                continue
            if CYRILLIC.search(child.name):
                continue
            mdo = child / f"{child.name}.mdo"
            if not mdo.exists():
                orphans.append(child)
    return orphans


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    src = PROJ / "src"
    if not src.is_dir():
        print(f"ERROR: source root not found: {src}", file=sys.stderr)
        return 2

    orphans = find_orphan_dirs(src)
    if not orphans:
        print("no orphan module directories found")
        return 0

    print(f"found {len(orphans)} orphan module director{'y' if len(orphans)==1 else 'ies'}:")
    for d in orphans:
        rel = d.relative_to(src)
        contents = sorted(p.name for p in d.iterdir())
        print(f"  - src/{rel}  ({', '.join(contents) if contents else 'empty'})")

    if dry_run:
        print("\n--dry-run: nothing deleted")
        return 0

    print()
    deleted = 0
    for d in orphans:
        try:
            shutil.rmtree(d)
            print(f"deleted: src/{d.relative_to(src)}")
            deleted += 1
        except OSError as e:
            print(f"FAILED: src/{d.relative_to(src)} -- {e}", file=sys.stderr)
    print(f"\n{deleted} orphan dir{'s' if deleted != 1 else ''} deleted")
    return 0 if deleted == len(orphans) else 1


if __name__ == "__main__":
    sys.exit(main())
