# tools-ui-1c-translation

Английский перевод расширения конфигурации **«Универсальные инструменты»** ([tools_ui_1c](https://github.com/tools-ui-1c/tools_ui_1c)) через зависимый проект перевода EDT (`dictionaries_en/`) — заполняется LLM-агентами (Claude/Opus) по чёткому workflow.

> **Полный контекст и workflow для агентов** — в [CLAUDE.md](CLAUDE.md).
> **Style guides** — [`prompts/NAME_RETRANSLATE_GUIDE.md`](prompts/NAME_RETRANSLATE_GUIDE.md), [`prompts/MODULE_STYLE_GUIDE.md`](prompts/MODULE_STYLE_GUIDE.md).

## О проекте

«Универсальные инструменты» (`УИ_`) — расширение конфигурации с инструментарием для разработчика и администратора 1С: консоли запросов/кода/HTTP-запросов, навигатор по метаданным, редактор алгоритмов, групповая обработка справочников и документов, парсер встроенного языка и пр. Расширение исторически развивается на русском, английская версия отсутствует.

Этот репозиторий — словарь зависимого перевода EDT (`dictionaries_en/`) + workflow + style guides + утилиты. Перевод формируется итерациями:

1. EDT генерирует пустые словари с русскими placeholder-значениями
2. LLM-агенты (Opus) заполняют значения английскими по правилам style guide
3. EDT через `translate_configuration` собирает translated_project с английскими BSL-модулями

## Текущее состояние

Подробный аудит — `python scripts/analysis/audit_status.py`. Кратко:

| Категория | Файлов | `.Name=` (cyr) | `prose` (cyr) |
|---|---:|---:|---:|
| CommonModules | 128 | 13 256 (0) | 3 364 (1) |
| DataProcessors | 620 | 28 013 (0) | 6 050 (~2 400) |
| Reports | 26 | 1 332 (1 332) | 526 (517) |
| Catalogs | 19 | 406 (404) | 19 (16) |
| CommonForms | 151 | 1 551 (1 550) | 115 (86) |

- **5 пилотных CommonModules с Opus-ревизией** (правильный английский compound order): `УИ_ОбщегоНазначения`, `УИ_РедакторКодаКлиент`, `УИ_СтроковыеФункцииКлиентСервер`, `УИ_АлгоритмыСервер`, `УИ_РаботаСФормами`. Плюс 5 модулей переведённых вручную в первой волне.
- **35 CommonModules** ждут Opus-ревизии `.Name=` (значения там есть, но позиционные — `NameTable` вместо `TableName`)
- **42 DataProcessors** — то же самое + ~2400 prose-строк недопереведено
- **Reports / Catalogs / CommonForms / Commands / HTTPServices** — почти не тронуты

Подробности в [CLAUDE.md → Текущее состояние](CLAUDE.md#текущее-состояние-перевода) и [TODO](CLAUDE.md#todo).

## Конфигурация EDT

В EDT-настройках проекта `Инструменты` оставлены **только контекстные словари** (per-module `.lstr` / `.trans`).

- Глобальный токен-словарь `common-camelcase_en.dict` **не используется** — удалён.
- Все переводы идентификаторов BSL — в `Module_en.trans` каждого модуля как explicit `.Name=` записи.

## Структура

```
tools-ui-1c-translation/
├── dictionaries_en/                   # зависимый проект перевода EDT
│   ├── DT-INF/DEPENDENT.PMF           # Parent-Project: Инструменты
│   ├── .project                       # dependentProjectNature
│   └── src/
│       ├── CommonModules/<Имя>/       # Module_en.trans + Module_en.lstr + module-level _en.lstr/_en.trans
│       ├── DataProcessors/<Имя>/...   # тот же паттерн + ObjectModule + Forms + Templates
│       ├── Reports/<Имя>/...
│       ├── Catalogs/<Имя>/...
│       ├── CommonForms/<Имя>/...
│       ├── HTTPServices/<Имя>/...
│       ├── Languages/English/         # объект целевого языка
│       └── common_en.dict             # display strings (Авто, Включая, ...)
├── prompts/                           # style guides для агентов
│   ├── NAME_RETRANSLATE_GUIDE.md      # правила compound order для .Name= идентификаторов
│   └── MODULE_STYLE_GUIDE.md          # общие правила перевода значений в .lstr/.trans
├── scripts/
│   ├── analysis/                      # audit_status, extract_untranslated, ...
│   ├── pipeline/                      # cleanup_orphan_modules, check_translated, postbuild_patch
│   └── migration/                     # точечные fix_* (regions, str_builtins, platform_fields)
├── CLAUDE.md                          # ⭐ полный контекст и workflow для агентов
├── POSTBUILD_PATCHER.md               # описание post-build шага (для HTTP-специфичных багов)
└── README.md                          # этот файл
```

## Активный workflow (для одного модуля)

1. `git pull`
2. В Claude Code дать агенту команду: «переведи `dictionaries_en/src/<Category>/<Module>/Module_en.trans` через Opus subagent (`subagent_type: general-purpose`, `model: "opus"`), используя `prompts/NAME_RETRANSLATE_GUIDE.md`. Референс стиля — `dictionaries_en/src/CommonModules/УИ_ОбщегоНазначения/Module_en.trans`.»
3. Если файл >800 строк — chunk на 2-3 части, по агенту на чанк, склеить
4. `python scripts/analysis/audit_status.py` — убедиться что cyr-valued = 0 в модуле
5. `git commit -am "Opus retranslate <module>"` + `git push`
6. Периодически — `mcp__edt-mcp__translate_configuration` в EDT, потом `cleanup_orphan_modules.py`, спот-чек BSL в translated_project

Полный workflow и правила — в [CLAUDE.md → Активный workflow](CLAUDE.md#активный-workflow-opus-retranslate-per-module).

## Требования

- **Claude Code** или совместимый агент с поддержкой Opus subagents
- **Python 3.10+** для скриптов аудита и pipeline
- **Git** для координации
- **EDT 2026.1+** + LanguageTool — нужен только для финальной сборки `Инструменты_Перевод/` через `translate_configuration` (не каждому участнику)
- Опционально: [EDT-MCP плагин](https://github.com/DitriXNew/EDT-MCP) с тулами `translate_configuration` / `clean_project` / `cleanup_orphan_modules`

## Координация работы между несколькими разработчиками

См. [CLAUDE.md → Координация](CLAUDE.md#координация-работы-между-несколькими-агентами--разработчиками). Кратко:

- Каждый берёт **непересекающийся набор модулей** (категория или конкретный список)
- Работа на ветке: `git checkout -b retranslate/<scope>`
- Пушите регулярно (после каждого модуля или пары)
- `translate_configuration` в EDT запускает **только один человек** (тот, у кого EDT) — он же финальный rebuild + проверка

## Ключевые скрипты

- [`scripts/analysis/audit_status.py`](scripts/analysis/audit_status.py) — статус по всем категориям (.Name / .Word / prose, % cyr-valued)
- [`scripts/analysis/extract_untranslated.py`](scripts/analysis/extract_untranslated.py) — список untranslated по одному файлу
- [`scripts/pipeline/cleanup_orphan_modules.py`](scripts/pipeline/cleanup_orphan_modules.py) — удалить orphan-папки в translated_project после переименований
- [`scripts/pipeline/check_translated.py`](scripts/pipeline/check_translated.py) — финальный сканер кириллицы (CODE/DOC) в translated_project
- [`scripts/pipeline/postbuild_patch.py`](scripts/pipeline/postbuild_patch.py) — фиксы остаточных багов EDT (StrStartWith, поля платформы)

Legacy-скрипты от ранней токен-словарной методологии (`apply_camelcase.py`, `camelcase_token_tr.py`, `proper_split.py`, и т.п.) **не используются в текущем подходе** — оставлены в репе для истории.

## Связанные проекты

- [tools-ui-1c/tools_ui_1c](https://github.com/tools-ui-1c/tools_ui_1c) — исходник расширения (RU)
- [DitriXNew/EDT-MCP](https://github.com/DitriXNew/EDT-MCP) — MCP-сервер для EDT
- [Dmitriy83/EDT-MCP](https://github.com/Dmitriy83/EDT-MCP) — fork с тулами LanguageTool / Workspace export-import
- [vbondarevsky/Connector → Dmitriy83/httpconnector-translations](https://github.com/Dmitriy83/httpconnector-translations) — предшественник этого pipeline для библиотеки HTTPConnector (использовалась старая токен-словарная методология)

## Лицензия

Соответствует лицензии [tools_ui_1c](https://github.com/tools-ui-1c/tools_ui_1c).
